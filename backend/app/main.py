from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    fastapi_app = FastAPI(title=settings.app_name, version=settings.app_version)

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Base.metadata.create_all(bind=engine)
    fastapi_app.include_router(auth_router, prefix=settings.api_prefix)
    fastapi_app.include_router(chat_router, prefix=settings.api_prefix)
    fastapi_app.include_router(health_router, prefix=settings.api_prefix)
    return fastapi_app


app = create_app()
