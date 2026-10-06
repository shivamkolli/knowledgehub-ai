import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_read_prefixed_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KNOWLEDGEHUB_APP_NAME", "Configured service")
    monkeypatch.setenv("KNOWLEDGEHUB_ENVIRONMENT", "test")

    settings = Settings(_env_file=None)

    assert settings.app_name == "Configured service"
    assert settings.environment == "test"


def test_settings_reject_invalid_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KNOWLEDGEHUB_ENVIRONMENT", "typo")

    with pytest.raises(ValidationError, match="environment"):
        Settings(_env_file=None, app_name="Test service")


def test_settings_reject_non_postgres_database_url() -> None:
    with pytest.raises(ValidationError, match="postgresql"):
        Settings(_env_file=None, environment="test", database_url="sqlite:///local.db")
