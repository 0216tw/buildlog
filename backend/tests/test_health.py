from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "buildlog-api",
    }


def test_cors_allows_only_configured_frontend() -> None:
    allowed_response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    blocked_response = client.options(
        "/api/health",
        headers={
            "Origin": "https://not-allowed.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert allowed_response.status_code == 200
    assert (
        allowed_response.headers["access-control-allow-origin"]
        == "http://localhost:5173"
    )
    assert "access-control-allow-origin" not in blocked_response.headers
