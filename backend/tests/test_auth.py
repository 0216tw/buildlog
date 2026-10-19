import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.database import SessionLocal
from app.main import app
from app.models import User


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def signup(
    client: TestClient,
    email: str = "learner@example.com",
    password: str = "password123",
    nickname: str = "학습자_1",
):
    return client.post(
        "/api/auth/signup",
        json={"email": email, "password": password, "nickname": nickname},
    )


def login(
    client: TestClient,
    email: str = "learner@example.com",
    password: str = "password123",
):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def test_signup_normalizes_fields_and_never_stores_plain_password(client: TestClient):
    response = signup(client, email="  Learner@Example.com ", nickname="  학습자_1  ")

    assert response.status_code == 201
    assert response.json()["email"] == "learner@example.com"
    assert response.json()["nickname"] == "학습자_1"

    with SessionLocal() as database:
        user = database.scalar(select(User))
        assert user is not None
        assert user.password_hash != "password123"
        assert "password123" not in user.password_hash


def test_signup_rejects_duplicate_email_and_nickname(client: TestClient):
    assert signup(client).status_code == 201

    duplicate_email = signup(
        client,
        email="learner@example.com",
        nickname="다른닉네임",
    )
    duplicate_nickname = signup(
        client,
        email="other@example.com",
        nickname="학습자_1",
    )

    assert duplicate_email.status_code == 409
    assert duplicate_email.json()["detail"] == "이미 사용 중인 이메일입니다."
    assert duplicate_nickname.status_code == 409
    assert duplicate_nickname.json()["detail"] == "이미 사용 중인 닉네임입니다."


@pytest.mark.parametrize(
    ("email", "password", "nickname", "message"),
    [
        ("not-an-email", "password123", "정상닉네임", "올바른 이메일 주소"),
        ("short@example.com", "1234567", "정상닉네임", "비밀번호는 8~64자"),
        ("long@example.com", "x" * 65, "정상닉네임", "비밀번호는 8~64자"),
        ("nick1@example.com", "password123", "한", "닉네임은 2~20자"),
        ("nick2@example.com", "password123", "가" * 21, "닉네임은 2~20자"),
        ("nick3@example.com", "password123", "잘못된 닉네임", "한글, 영문, 숫자, 밑줄"),
    ],
)
def test_signup_rejects_invalid_input(
    client: TestClient,
    email: str,
    password: str,
    nickname: str,
    message: str,
):
    response = signup(client, email=email, password=password, nickname=nickname)

    assert response.status_code == 422
    assert message in response.json()["detail"]


def test_password_boundary_values_are_allowed(client: TestClient):
    first = signup(
        client,
        email="eight@example.com",
        password="x" * 8,
        nickname="닉네임_8",
    )
    second = signup(
        client,
        email="sixtyfour@example.com",
        password="x" * 64,
        nickname="닉네임_64",
    )

    assert first.status_code == 201
    assert second.status_code == 201


def test_login_sets_http_only_cookie_and_allows_current_user(client: TestClient):
    signup(client)
    response = login(client)

    assert response.status_code == 200
    assert "httponly" in response.headers["set-cookie"].lower()
    assert "samesite=lax" in response.headers["set-cookie"].lower()

    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["nickname"] == "학습자_1"


def test_login_failure_does_not_create_login_state(client: TestClient):
    signup(client)
    response = login(client, password="wrong-password")

    assert response.status_code == 401
    assert response.json()["detail"] == "이메일 또는 비밀번호가 맞지 않습니다."
    assert client.get("/api/auth/me").status_code == 401


def test_protected_api_rejects_unauthenticated_user(client: TestClient):
    response = client.patch("/api/users/me/nickname", json={"nickname": "새닉네임"})

    assert response.status_code == 401


def test_logged_in_user_can_change_only_own_nickname(client: TestClient):
    signup(client)
    login(client)
    response = client.patch(
        "/api/users/me/nickname",
        json={"nickname": "  새닉네임_2  "},
    )

    assert response.status_code == 200
    assert response.json()["nickname"] == "새닉네임_2"
    assert client.get("/api/auth/me").json()["nickname"] == "새닉네임_2"


def test_nickname_change_rejects_duplicate_and_invalid_value(client: TestClient):
    signup(client, email="first@example.com", nickname="첫사용자")
    signup(client, email="second@example.com", nickname="둘째사용자")
    login(client, email="second@example.com")

    duplicate = client.patch(
        "/api/users/me/nickname",
        json={"nickname": "첫사용자"},
    )
    invalid = client.patch(
        "/api/users/me/nickname",
        json={"nickname": "공백 닉네임"},
    )

    assert duplicate.status_code == 409
    assert invalid.status_code == 422
    assert client.get("/api/auth/me").json()["nickname"] == "둘째사용자"
