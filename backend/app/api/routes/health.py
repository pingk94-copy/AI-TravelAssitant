from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def read_health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/llm")
def read_llm_health() -> dict[str, bool | float | str]:
    key = settings.openai_api_key.strip()
    enabled = bool(key) and key != "your_api_key_here"
    return {
        "status": "configured" if enabled else "disabled",
        "enabled": enabled,
        "api_key_configured": enabled,
        "base_url": settings.openai_base_url,
        "model": settings.openai_model,
        "timeout_seconds": float(settings.openai_timeout_seconds),
    }
