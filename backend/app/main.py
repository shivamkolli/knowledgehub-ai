"""Application lifecycle and health endpoints."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import build_engine, get_session


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str


def create_app(settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        # Engine creation is lazy: it does not open a database connection.
        engine = build_engine(settings if settings is not None else get_settings())
        application.state.engine = engine
        try:
            yield
        finally:
            engine.dispose()

    application = FastAPI(title="KnowledgeHub AI API", version="0.1.0", lifespan=lifespan)
    if settings is not None:
        application.dependency_overrides[get_settings] = lambda: settings

    @application.get("/health", response_model=HealthResponse, tags=["health"])
    def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
        """Report process liveness, without claiming dependencies are ready."""
        return HealthResponse(service=settings.app_name)

    @application.get(
        "/ready",
        response_model=HealthResponse,
        tags=["health"],
        responses={503: {"description": "Database unavailable"}},
    )
    def ready(
        session: Annotated[Session, Depends(get_session)],
        settings: Annotated[Settings, Depends(get_settings)],
    ) -> HealthResponse:
        """Check database connectivity without exposing connection details."""
        try:
            session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            raise HTTPException(status_code=503, detail="Database unavailable") from None
        return HealthResponse(service=settings.app_name)

    return application


app = create_app()
