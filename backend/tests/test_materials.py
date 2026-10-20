from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.materials import get_material_storage
from app.db.database import SessionLocal
from app.main import app
from app.models import Material
from app.services.material_storage import IMAGE_LIMIT_BYTES, VIDEO_LIMIT_BYTES, MaterialStorage


PNG = b"\x89PNG\r\n\x1a\n" + b"image-data"
JPEG = b"\xff\xd8\xff\xe0" + b"image-data"
MP4 = b"\x00\x00\x00\x18ftypisom" + b"video-data"


def signup_login(client: TestClient, email: str, nickname: str) -> None:
    assert client.post(
        "/api/auth/signup",
        json={"email": email, "password": "password123", "nickname": nickname},
    ).status_code == 201
    assert client.post(
        "/api/auth/login",
        json={"email": email, "password": "password123"},
    ).status_code == 200


def upload(
    client: TestClient,
    *,
    title: str = "자료",
    memo: str | None = "메모",
    filename: str = "note.png",
    content_type: str = "image/png",
    content: bytes = PNG,
):
    data = {"title": title}
    if memo is not None:
        data["memo"] = memo
    return client.post(
        "/api/materials",
        data=data,
        files=[("file", (filename, content, content_type))],
    )


@pytest.fixture
def material_clients(tmp_path: Path):
    storage = MaterialStorage(tmp_path / "uploads")
    app.dependency_overrides[get_material_storage] = lambda: storage
    try:
        with TestClient(app) as first, TestClient(app) as second:
            signup_login(first, "material-first@example.com", "자료사용자1")
            signup_login(second, "material-second@example.com", "자료사용자2")
            yield first, second, storage
    finally:
        app.dependency_overrides.pop(get_material_storage, None)


def test_material_endpoints_require_login(tmp_path: Path):
    storage = MaterialStorage(tmp_path / "uploads")
    app.dependency_overrides[get_material_storage] = lambda: storage
    try:
        with TestClient(app) as client:
            assert client.get("/api/materials").status_code == 401
            response = upload(client)
            assert response.status_code == 401
    finally:
        app.dependency_overrides.pop(get_material_storage, None)


def test_upload_normalizes_text_and_hides_internal_path(material_clients):
    first, _second, storage = material_clients
    response = upload(first, title="  REST API 정리  ", memo="  요청 흐름  ")

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "REST API 정리"
    assert body["memo"] == "요청 흐름"
    assert body["media_type"] == "image"
    assert body["content_type"] == "image/png"
    assert body["size_bytes"] == len(PNG)
    assert body["ai_status"] == "pending"
    assert body["ai_summary"] is None
    assert body["ai_analyzed_at"] is None
    assert "stored_path" not in body
    assert "user_id" not in body
    assert "ai_error_code" not in body
    assert "ai_model" not in body

    with SessionLocal() as database:
        material = database.scalar(select(Material).where(Material.id == body["id"]))
        assert material is not None
        stored_path = storage.resolve_existing(material.stored_path)
        assert stored_path.read_bytes() == PNG
        assert stored_path.name != "note.png"


def test_upload_accepts_optional_memo_jpeg_and_mp4(material_clients):
    first, _second, _storage = material_clients
    jpeg = upload(
        first,
        memo=None,
        filename="photo.jpeg",
        content_type="image/jpeg",
        content=JPEG,
    )
    video = upload(
        first,
        title="영상",
        filename="lesson.mp4",
        content_type="video/mp4",
        content=MP4,
    )

    assert jpeg.status_code == 201
    assert jpeg.json()["memo"] is None
    assert jpeg.json()["content_type"] == "image/jpeg"
    assert video.status_code == 201
    assert video.json()["media_type"] == "video"


def test_upload_accepts_text_and_file_size_boundaries(material_clients):
    first, _second, _storage = material_clients
    short_title = upload(first, title="가", memo="나" * 1000)
    long_title = upload(first, title="다" * 100, memo=None, filename="other.png")
    exact_image = upload(
        first,
        title="이미지 경계",
        filename="limit.png",
        content=b"\x89PNG\r\n\x1a\n" + b"x" * (IMAGE_LIMIT_BYTES - 8),
    )
    exact_video = upload(
        first,
        title="영상 경계",
        filename="limit.mp4",
        content_type="video/mp4",
        content=b"\x00\x00\x00\x18ftypisom" + b"x" * (VIDEO_LIMIT_BYTES - 12),
    )
    oversized_video = upload(
        first,
        title="큰 영상",
        filename="large.mp4",
        content_type="video/mp4",
        content=b"\x00\x00\x00\x18ftypisom" + b"x" * (VIDEO_LIMIT_BYTES - 11),
    )

    assert short_title.status_code == 201
    assert len(short_title.json()["memo"]) == 1000
    assert long_title.status_code == 201
    assert len(long_title.json()["title"]) == 100
    assert exact_image.status_code == 201
    assert exact_image.json()["size_bytes"] == IMAGE_LIMIT_BYTES
    assert exact_video.status_code == 201
    assert exact_video.json()["size_bytes"] == VIDEO_LIMIT_BYTES
    assert oversized_video.status_code == 422


@pytest.mark.parametrize(
    ("title", "memo", "expected"),
    [
        ("   ", None, "제목"),
        ("가" * 101, None, "100자"),
        ("제목", "가" * 1001, "1,000자"),
    ],
)
def test_upload_rejects_invalid_text(material_clients, title, memo, expected):
    first, _second, _storage = material_clients
    response = upload(first, title=title, memo=memo)
    assert response.status_code == 422
    assert expected in response.json()["detail"]


def test_upload_rejects_invalid_file_count_type_signature_and_size(material_clients):
    first, _second, _storage = material_clients

    multiple = first.post(
        "/api/materials",
        data={"title": "두 파일"},
        files=[
            ("file", ("one.png", PNG, "image/png")),
            ("file", ("two.png", PNG, "image/png")),
        ],
    )
    mismatch = upload(first, filename="fake.png", content_type="text/plain")
    fake_signature = upload(first, content=b"not-a-png")
    empty = upload(first, content=b"")
    oversized = upload(
        first,
        content=b"\x89PNG\r\n\x1a\n" + b"x" * (IMAGE_LIMIT_BYTES - 7),
    )

    assert multiple.status_code == 422
    assert mismatch.status_code == 422
    assert fake_signature.status_code == 422
    assert empty.status_code == 422
    assert oversized.status_code == 422
    assert not first.get("/api/materials").json()


def test_list_file_and_delete_are_owner_only(material_clients):
    first, second, storage = material_clients
    older = upload(first, title="첫 자료").json()
    newer = upload(first, title="둘째 자료", filename="photo.jpg", content_type="image/jpeg", content=JPEG).json()

    first_list = first.get("/api/materials")
    assert first_list.status_code == 200
    assert [item["id"] for item in first_list.json()] == [newer["id"], older["id"]]
    assert second.get("/api/materials").json() == []

    own_file = first.get(f"/api/materials/{older['id']}/file")
    assert own_file.status_code == 200
    assert own_file.content == PNG
    assert own_file.headers["content-type"].startswith("image/png")
    assert own_file.headers["cache-control"] == "private, no-store"
    assert second.get(f"/api/materials/{older['id']}/file").status_code == 404
    assert second.delete(f"/api/materials/{older['id']}").status_code == 404

    with SessionLocal() as database:
        material = database.get(Material, older["id"])
        stored_path = material.stored_path
        file_path = storage.resolve_existing(stored_path)

    assert first.delete(f"/api/materials/{older['id']}").status_code == 204
    assert not file_path.exists()
    with SessionLocal() as database:
        assert database.get(Material, older["id"]) is None


def test_missing_original_file_does_not_delete_metadata(material_clients):
    first, _second, storage = material_clients
    created = upload(first).json()
    with SessionLocal() as database:
        material = database.get(Material, created["id"])
        storage.remove_stored(material.stored_path)

    assert first.get(f"/api/materials/{created['id']}/file").status_code == 500
    assert first.delete(f"/api/materials/{created['id']}").status_code == 500
    assert first.get("/api/materials").json()[0]["id"] == created["id"]
