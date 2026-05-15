from fastapi.testclient import TestClient

from app.core.config import settings
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


def test_llm_health_reports_disabled_status_without_key(client: TestClient):
    response = client.get("/api/health/llm")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "disabled"
    assert body["enabled"] is False
    assert body["api_key_configured"] is False
    assert body["model"] == settings.openai_model
    assert "api_key" not in body


def test_llm_health_reports_configured_provider_without_exposing_key(client: TestClient):
    settings.openai_api_key = "sk-test-secret"
    settings.openai_base_url = "https://api.siliconflow.cn/v1"
    settings.openai_model = "deepseek-ai/DeepSeek-V4-Flash"
    settings.openai_timeout_seconds = 12

    response = client.get("/api/health/llm")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "status": "configured",
        "enabled": True,
        "api_key_configured": True,
        "base_url": "https://api.siliconflow.cn/v1",
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "timeout_seconds": 12.0,
    }
