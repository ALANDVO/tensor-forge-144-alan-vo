"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="sqlite:///./data/tensorforge.db",
        description="SQLAlchemy database URL",
    )

    # Security
    secret_key: str = Field(
        default="dev-secret-change-in-production",
        description="Secret key for JWT signing",
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiry")

    # LLM Provider Settings
    llm_api_key: Optional[str] = Field(default=None, description="LLM API key (server-side only)")
    llm_provider: str = Field(default="openai-compatible", description="LLM provider type")
    llm_model: Optional[str] = Field(default=None, description="LLM model name")
    llm_base_url: Optional[str] = Field(default=None, description="LLM base URL")

    # Keycloak / OIDC
    keycloak_url: str = Field(default="http://keycloak:8080", description="Keycloak server URL")
    keycloak_realm: str = Field(default="tensorforge", description="Keycloak realm")
    keycloak_client_id: str = Field(default="tensorforge-backend", description="Keycloak client ID")
    keycloak_client_secret: Optional[str] = Field(default=None, description="Keycloak client secret")
    keycloak_admin_user: str = Field(default="admin", description="Keycloak admin user")
    keycloak_admin_password: Optional[str] = Field(default=None, description="Keycloak admin password")

    # Demo mode
    demo_mode: bool = Field(default=False, description="Enable demo mode (localhost only)")

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()