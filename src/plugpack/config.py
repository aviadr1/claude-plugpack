"""
Application configuration using Pydantic Settings.

All configuration is loaded from environment variables with sensible defaults
for local development.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    app_secret_key: str = Field(
        default="dev-secret-key-change-in-production-must-be-32-chars-long",
        min_length=32,
    )

    # Database
    database_url: str = (
        "postgresql+asyncpg://plugpack:plugpack_dev_password@localhost:5432/plugpack"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Meilisearch
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_api_key: str = "plugpack_meili_dev_key"

    # GitHub
    github_client_id: str = ""
    github_client_secret: str = ""
    github_token: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience export
settings = get_settings()
