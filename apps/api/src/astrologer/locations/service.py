"""Geoapify adapter that exposes only location facts required for birth input."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from astrologer.locations.models import LocationSuggestion

_ENDPOINT = "https://api.geoapify.com/v1/geocode/autocomplete"
_MAX_RESULTS = 6


class LocationLookupError(RuntimeError):
    """Safe error raised when location search cannot be completed."""


class GeoapifyLocationService:
    """Normalize Geoapify autocomplete data without returning provider payloads."""

    def __init__(self, api_key: str | None) -> None:
        self._api_key = api_key

    def search(self, query: str) -> list[LocationSuggestion]:
        """Find worldwide locality/address suggestions for a human-entered query."""
        if not self._api_key:
            raise LocationLookupError("Location search is not configured.")
        params = urlencode(
            {
                "text": query,
                "limit": _MAX_RESULTS,
                "format": "json",
                "apiKey": self._api_key,
            }
        )
        try:
            with urlopen(f"{_ENDPOINT}?{params}", timeout=5) as response:  # noqa: S310
                payload: object = json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            raise LocationLookupError("Location search is temporarily unavailable.") from error
        return _normalize(payload)


def _normalize(payload: object) -> list[LocationSuggestion]:
    """Extract only valid coordinates, an IANA zone, a label, and a provider identifier."""
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise LocationLookupError("Location search is temporarily unavailable.")
    suggestions: list[LocationSuggestion] = []
    for item in payload["results"][:_MAX_RESULTS]:
        suggestion = _suggestion(item)
        if suggestion is not None:
            suggestions.append(suggestion)
    return suggestions


def _suggestion(item: object) -> LocationSuggestion | None:
    if not isinstance(item, dict):
        return None
    if item.get("result_type") == "amenity":
        return None
    timezone = item.get("timezone")
    timezone_name = timezone.get("name") if isinstance(timezone, dict) else None
    display_name = item.get("formatted")
    latitude = item.get("lat")
    longitude = item.get("lon")
    if not (
        isinstance(display_name, str)
        and isinstance(timezone_name, str)
        and isinstance(latitude, (int, float))
        and isinstance(longitude, (int, float))
    ):
        return None
    try:
        canonical_timezone = ZoneInfo(timezone_name).key
    except ZoneInfoNotFoundError:
        return None
    provider_id = item.get("place_id")
    return LocationSuggestion(
        display_name=display_name,
        latitude=latitude,
        longitude=longitude,
        timezone=canonical_timezone,
        provider_id=str(provider_id) if provider_id is not None else None,
    )
