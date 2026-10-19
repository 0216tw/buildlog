import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.database import SessionLocal
from app.main import app
from app.models import User


@pytest.fixture
def clients():
    with TestClient(app) as first, TestClient(app) as second:
        signup_login(first, "first@example.com", "첫사용자")
        signup_login(second, "second@example.com", "둘째사용자")
        yield first, second


def signup_login(client, email, nickname):
    assert client.post("/api/auth/signup", json={"email": email, "password": "password123", "nickname": nickname}).status_code == 201
    assert client.post("/api/auth/login", json={"email": email, "password": "password123"}).status_code == 200


def test_study_crud_search_validation_and_permissions(clients):
    first, second = clients
    invalid = first.post("/api/studies", json={"title": "   ", "content": "내용"})
    assert invalid.status_code == 422

    created = first.post("/api/studies", json={"title": "  FastAPI 학습  ", "content": "  의존성 주입 정리  "})
    assert created.status_code == 201
    record = created.json()
    assert record["title"] == "FastAPI 학습"
    assert record["content"] == "의존성 주입 정리"
    assert record["is_public"] is False
    assert first.get("/api/studies?q=의존성").json()[0]["id"] == record["id"]
    assert second.get(f"/api/studies/{record['id']}").status_code == 404
    assert second.put(f"/api/studies/{record['id']}", json={"title": "침입", "content": "안됨"}).status_code == 403

    updated = first.put(f"/api/studies/{record['id']}", json={"title": "수정", "content": "수정 내용", "is_public": True})
    assert updated.status_code == 200
    assert second.get(f"/api/studies/{record['id']}").status_code == 200
    assert first.delete(f"/api/studies/{record['id']}").status_code == 204


def test_todo_completion_order_filters_and_permissions(clients):
    first, second = clients
    old = first.post("/api/todos", json={"title": "첫 할 일"}).json()
    new = first.post("/api/todos", json={"title": "둘째 할 일"}).json()
    completed = first.patch(f"/api/todos/{new['id']}/completion", json={"is_completed": True})
    assert completed.status_code == 200
    assert completed.json()["completed_at"] is not None
    items = first.get("/api/todos").json()
    assert [item["id"] for item in items] == [old["id"], new["id"]]
    assert len(first.get("/api/todos?state=pending").json()) == 1
    assert len(first.get("/api/todos?state=completed").json()) == 1
    undone = first.patch(f"/api/todos/{new['id']}/completion", json={"is_completed": False}).json()
    assert undone["completed_at"] is None
    assert second.patch(f"/api/todos/{old['id']}/completion", json={"is_completed": True}).status_code == 403


def test_error_resolution_search_and_validation(clients):
    first, _second = clients
    invalid = first.post("/api/errors", json={"title": "오류", "content": "내용", "is_resolved": True})
    assert invalid.status_code == 422
    created = first.post("/api/errors", json={"title": "  연결 오류  ", "content": "  timeout 발생  "}).json()
    assert created["is_resolved"] is False
    resolved = first.put(f"/api/errors/{created['id']}", json={"title": "연결 오류", "content": "timeout 발생", "resolution": "재시도 설정", "is_resolved": True}).json()
    assert resolved["resolved_at"] is not None
    assert first.get("/api/errors?state=resolved&q=연결").json()[0]["id"] == created["id"]
    unresolved = first.put(f"/api/errors/{created['id']}", json={"title": "연결 오류", "content": "timeout 발생", "resolution": "재시도 설정", "is_resolved": False}).json()
    assert unresolved["resolution"] == "재시도 설정"
    assert unresolved["resolved_at"] is None


def test_public_list_comments_likes_and_private_hiding(clients):
    first, second = clients
    study = first.post("/api/studies", json={"title": "공개 학습", "content": "공개 내용", "is_public": True}).json()
    private = first.post("/api/studies", json={"title": "비밀", "content": "숨김"}).json()
    public_items = second.get("/api/public-records?q=공개").json()
    assert len(public_items) == 1
    assert public_items[0]["author_nickname"] == "첫사용자"
    assert all(item["id"] != private["id"] for item in second.get("/api/public-records").json())

    comment = second.post(f"/api/studies/{study['id']}/comments", json={"content": "  좋은 기록입니다  "})
    assert comment.status_code == 201
    assert comment.json()["content"] == "좋은 기록입니다"
    assert len(first.get(f"/api/studies/{study['id']}/comments").json()) == 1
    assert first.delete(f"/api/comments/{comment.json()['id']}").status_code == 204

    liked = second.post(f"/api/studies/{study['id']}/like").json()
    assert liked == {"liked": True, "count": 1}
    assert second.post(f"/api/studies/{study['id']}/like").json()["count"] == 1
    assert second.delete(f"/api/studies/{study['id']}/like").json() == {"liked": False, "count": 0}

    first.patch(f"/api/studies/{study['id']}/visibility", json={"is_public": False})
    assert second.get(f"/api/studies/{study['id']}/comments").status_code == 403
    assert second.get(f"/api/studies/{study['id']}/like").status_code == 403


def test_reports_are_unique_and_admin_only_even_after_private(clients):
    first, second = clients
    study = first.post("/api/studies", json={"title": "신고 대상", "content": "내용", "is_public": True}).json()
    report = second.post("/api/reports", json={"target_type": "study", "target_id": study["id"], "reason": "  확인이 필요합니다  "})
    assert report.status_code == 201
    assert second.post("/api/reports", json={"target_type": "study", "target_id": study["id"], "reason": "중복"}).status_code == 409
    assert second.get("/api/admin/reports").status_code == 403

    with SessionLocal() as database:
        admin = database.scalar(select(User).where(User.email == "first@example.com"))
        admin.is_admin = True
        database.commit()

    first.patch(f"/api/studies/{study['id']}/visibility", json={"is_public": False})
    reports = first.get("/api/admin/reports")
    assert reports.status_code == 200
    assert reports.json()[0]["reason"] == "확인이 필요합니다"
    assert first.get(f"/api/admin/reports/{report.json()['id']}").status_code == 200
