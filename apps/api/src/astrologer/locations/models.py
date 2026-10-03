"""Safe, minimal location-search contracts returned to the browser."""

from pydantic import BaseModel, Field


class LocationSuggestion(BaseModel):
    """A normalized selectable location, independent of Geoapify's raw schema."""

    display_name: str = Field(min_length=1, max_length=256)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str = Field(min_length=1, max_length=128)
    provider_id: str | None = Field(default=None, max_length=256)


class LocationSearchResponse(BaseModel):
    """Bounded response for the public autocomplete endpoint."""

    results: list[LocationSuggestion]
