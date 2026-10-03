"""Privacy-preserving location autocomplete endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from astrologer.common.config import Settings
from astrologer.locations.models import LocationSearchResponse
from astrologer.locations.service import GeoapifyLocationService, LocationLookupError

router = APIRouter(prefix="/api/v1/locations", tags=["locations"])


def get_location_service(request: Request) -> GeoapifyLocationService:
    """Build the adapter from server-only environment configuration."""
    settings: Settings = request.app.state.settings
    return GeoapifyLocationService(settings.geoapify_api_key)


@router.get("/search", response_model=LocationSearchResponse)
async def search_locations(
    q: Annotated[str, Query(min_length=3, max_length=120)],
    service: Annotated[GeoapifyLocationService, Depends(get_location_service)],
) -> LocationSearchResponse:
    """Return a bounded, normalized set of selectable worldwide locations."""
    try:
        return LocationSearchResponse(results=service.search(q.strip()))
    except LocationLookupError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
