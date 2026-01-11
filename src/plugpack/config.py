"""
Application configuration using Pydantic Settings.

All configuration is loaded from environment variables with sensible defaults
for local development. Production requires explicit configuration.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field, model_validator
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

    # Database - Required in production, default for dev
    database_url: str = Field(
        default="postgresql+asyncpg://plugpack:plugpack_dev_password@localhost:5432/plugpack"
    )

    # Redis - Required in production, default for dev
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Meilisearch
    meilisearch_url: str = Field(default="http://localhost:7700")
    meilisearch_api_key: str = Field(default="plugpack_meili_dev_key")

    # GitHub
    github_client_id: str = ""
    github_client_secret: str = ""
    github_token: str = ""

    # CORS
    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Ensure required settings are provided in production."""
        if self.app_env == "production":
            # Check for dev defaults that shouldn't be in production
            if "dev-secret-key" in self.app_secret_key:
                raise ValueError("APP_SECRET_KEY must be set to a secure value in production")
            if "plugpack_dev_password" in self.database_url:
                raise ValueError("DATABASE_URL must be set to production database in production")
            if self.meilisearch_api_key == "plugpack_meili_dev_key":
                raise ValueError("MEILISEARCH_API_KEY must be set to production key in production")
        return self

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
