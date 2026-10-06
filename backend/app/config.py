"""Validated configuration loaded from the environment and backend/.env."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from sqlalchemy.engine import make_url
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KNOWLEDGEHUB_",
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="KnowledgeHub AI", min_length=1)
    environment: Literal["development", "test", "production"] = "development"

    database_url: SecretStr = SecretStr(
        "postgresql+psycopg://knowledgehub:knowledgehub_local@127.0.0.1:55432/knowledgehub"
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        try:
            url = make_url(value.get_secret_value())
            valid = url.drivername == "postgresql+psycopg" and bool(url.database)
        except Exception:
            valid = False
        if not valid:
            raise ValueError("Use a postgresql+psycopg URL with a database name")
        return value


@lru_cache
def get_settings() -> Settings:
    """Read configuration once per process; restart after changing settings."""
    return Settings()
