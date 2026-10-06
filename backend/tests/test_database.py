import os
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import build_engine, get_session
from app.main import create_app


def test_readiness_failure_does_not_break_liveness() -> None:
    application = create_app(Settings(_env_file=None, environment="test"))
    session = Mock(spec=Session)
    session.execute.side_effect = OperationalError("SELECT 1", {}, Exception("secret details"))
    application.dependency_overrides[get_session] = lambda: session
    with TestClient(application) as client:
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Database unavailable"}
        assert client.get("/health").status_code == 200


@pytest.mark.integration
def test_postgres_readiness_and_uncommitted_rollback() -> None:
    url = os.environ.get("KNOWLEDGEHUB_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set KNOWLEDGEHUB_TEST_DATABASE_URL to run against PostgreSQL")
    settings = Settings(_env_file=None, environment="test", database_url=url)
    with TestClient(create_app(settings)) as client:
        assert client.get("/ready").status_code == 200

    engine = build_engine(settings)
    try:
        with engine.connect() as connection:
            # Temporary table exists only on this connection; no application schema changes.
            connection.execute(text("CREATE TEMP TABLE transaction_probe (value integer)"))
            connection.commit()
            with Session(bind=connection) as session:
                session.execute(text("INSERT INTO transaction_probe VALUES (1)"))
                # Deliberately no commit: closing must roll this back.
            assert connection.scalar(text("SELECT count(*) FROM transaction_probe")) == 0
            connection.rollback()
            with Session(bind=connection) as session:
                session.execute(text("INSERT INTO transaction_probe VALUES (2)"))
                session.commit()
            assert connection.scalar(text("SELECT count(*) FROM transaction_probe")) == 1
    finally:
        engine.dispose()
