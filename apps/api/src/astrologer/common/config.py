"""Application configuration loaded from environment variables."""

from pydantic import Field
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
