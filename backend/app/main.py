"""Application entry point and the first HTTP endpoint."""

from typing import Annotated, Literal

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from app.config import Settings, get_settings


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str


def create_app() -> FastAPI:
    application = FastAPI(title="KnowledgeHub AI API", version="0.1.0")

    @application.get("/health", response_model=HealthResponse, tags=["health"])
    def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
        """Report process liveness, without claiming dependencies are ready."""
        return HealthResponse(service=settings.app_name)

    return application


app = create_app()
