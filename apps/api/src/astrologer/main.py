"""FastAPI application entry point."""

from fastapi import FastAPI

from astrologer.api.health import router as health_router
from astrologer.common.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the API application with explicit, environment-backed settings."""
    application_settings = settings or Settings()
    app = FastAPI(
        title=application_settings.app_name,
        version=application_settings.app_version,
        debug=application_settings.debug,
    )
    app.state.settings = application_settings
    app.include_router(health_router)
    return app


app = create_app()
