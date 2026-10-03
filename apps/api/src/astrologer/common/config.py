"""Application configuration loaded from environment variables."""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the API foundation.

    Values are intentionally limited to application concerns at this stage;
    astrology methodology and calculation settings are introduced with the
    deterministic astrology modules in later tasks.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="AI Astrologer API", validation_alias="APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    environment: str = Field(default="development", validation_alias="APP_ENVIRONMENT")
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    cors_allowed_origins: list[str] = Field(
        default_factory=list, validation_alias="CORS_ALLOWED_ORIGINS"
    )
    geoapify_api_key: str | None = Field(default=None, validation_alias="GEOAPIFY_API_KEY")
    llm_enabled: bool = Field(default=False, validation_alias="LLM_ENABLED")
    llm_provider: Literal["local", "openai_compatible"] = Field(
        default="local", validation_alias="LLM_PROVIDER"
    )
    llm_base_url: str = Field(default="http://localhost:1234/v1", validation_alias="LLM_BASE_URL")
    llm_model: str = Field(default="qwen", validation_alias="LLM_MODEL")
    llm_api_key: str | None = Field(default=None, validation_alias="LLM_API_KEY")
    llm_timeout_seconds: float = Field(
        default=20.0, gt=0, le=120, validation_alias="LLM_TIMEOUT_SECONDS"
    )

    @field_validator("cors_allowed_origins")
    @classmethod
    def cors_origins_must_be_exact(cls, value: list[str]) -> list[str]:
        if "*" in value:
            raise ValueError("CORS_ALLOWED_ORIGINS must not include wildcard origins")
        return value
