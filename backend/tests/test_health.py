from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_service_metadata():
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ai-travel-assistant-api",
        "version": "0.1.0",
    }


def test_cors_allows_vite_origin_on_loopback_ip():
    client = TestClient(app)

    response = client.options(
        "/api/auth/register",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
