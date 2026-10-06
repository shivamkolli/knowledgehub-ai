"""Validated configuration loaded from the environment and backend/.env."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
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


@lru_cache
def get_settings() -> Settings:
    """Read configuration once per process; restart after changing settings."""
    return Settings()
