"""A process-wide engine and a separate session for each request."""

from collections.abc import Iterator

from fastapi import Request
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.config import Settings


def build_engine(settings: Settings) -> Engine:
    return create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        pool_timeout=5,
        connect_args={"connect_timeout": 3, "options": "-c statement_timeout=3000"},
    )


def get_session(request: Request) -> Iterator[Session]:
    with Session(request.app.state.engine) as session:
        yield session
        # Closing releases the connection and rolls back uncommitted work.
        # Writes must explicitly commit in the operation that owns them.
