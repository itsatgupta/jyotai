"""Tests for environment-backed API configuration."""

from astrologer.common.config import Settings


def test_settings_reads_application_values_from_environment(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("APP_NAME", "Test API")
    monkeypatch.setenv("APP_VERSION", "9.9.9")
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setenv("APP_DEBUG", "true")

    settings = Settings()

    assert settings.app_name == "Test API"
    assert settings.app_version == "9.9.9"
    assert settings.environment == "test"
    assert settings.debug is True
