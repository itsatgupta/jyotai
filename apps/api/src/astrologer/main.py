"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from astrologer.api.analyze import router as analyze_router
from astrologer.api.charts import router as charts_router
from astrologer.api.context import router as context_router
from astrologer.api.health import router as health_router
from astrologer.api.locations import router as locations_router
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
    if application_settings.cors_allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=application_settings.cors_allowed_origins,
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )
    app.include_router(health_router)
    app.include_router(charts_router)
    app.include_router(context_router)
    app.include_router(analyze_router)
    app.include_router(locations_router)
    return app


app = create_app()
