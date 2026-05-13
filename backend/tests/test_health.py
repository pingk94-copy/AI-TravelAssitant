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
