"""Service health endpoint."""

import os
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])

# Render sets this at build time and at runtime to the deployed commit SHA
# (https://render.com/docs/environment-variables, "All runtimes").
DEPLOYED_COMMIT_ENV_VAR = "RENDER_GIT_COMMIT"
UNKNOWN_COMMIT = "unknown"


class HealthResponse(BaseModel):
    """Stable response returned when the service is available."""

    status: Literal["ok"]
    commit: str


def deployed_commit() -> str:
    """Return the platform-supplied commit SHA, or ``"unknown"`` when it is absent."""
    value = os.environ.get(DEPLOYED_COMMIT_ENV_VAR, "").strip()
    return value or UNKNOWN_COMMIT


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return a minimal, dependency-free availability signal plus the deployed commit."""
    return HealthResponse(status="ok", commit=deployed_commit())
