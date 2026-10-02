"""Service health endpoint."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Stable response returned when the service is available."""

    status: Literal["ok"]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return a minimal, dependency-free availability signal."""
    return HealthResponse(status="ok")
