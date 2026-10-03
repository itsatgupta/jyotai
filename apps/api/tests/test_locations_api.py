"""Location autocomplete stays a small, non-astrological external adapter."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from astrologer.api.locations import get_location_service
from astrologer.locations.service import GeoapifyLocationService, LocationLookupError
from astrologer.main import create_app


def _payload() -> dict[str, object]:
    return {
        "results": [
            {
                "formatted": "Gurugram, Haryana, India",
                "lat": 28.4595,
                "lon": 77.0266,
                "place_id": "geoapify-result-id",
                "timezone": {"name": "Asia/Kolkata", "offset_STD": "+05:30"},
                "unwanted_provider_field": "must not leak",
            }
        ]
    }


def test_location_search_normalizes_provider_data() -> None:
    service = GeoapifyLocationService("test-key")
    with patch("astrologer.locations.service.urlopen") as urlopen:
        response = urlopen.return_value.__enter__.return_value
        response.__iter__.return_value = iter(())
        with patch("astrologer.locations.service.json.load", return_value=_payload()):
            results = service.search("Gurgaon")

    assert results[0].model_dump() == {
        "display_name": "Gurugram, Haryana, India",
        "latitude": 28.4595,
        "longitude": 77.0266,
        "timezone": "Asia/Kolkata",
        "provider_id": "geoapify-result-id",
    }
    assert "test-key" in urlopen.call_args.args[0]


def test_location_search_missing_key_is_safe() -> None:
    try:
        GeoapifyLocationService(None).search("Gurgaon")
    except LocationLookupError as error:
        assert str(error) == "Location search is not configured."
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("missing key must fail safely")


def test_location_endpoint_validates_query_and_hides_raw_payload() -> None:
    app = create_app()
    app.dependency_overrides[get_location_service] = lambda: _Service()
    client = TestClient(app)

    assert client.get("/api/v1/locations/search", params={"q": "Gu"}).status_code == 422
    response = client.get("/api/v1/locations/search", params={"q": "Gurgaon"})

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "display_name": "Gurugram, Haryana, India",
                "latitude": 28.4595,
                "longitude": 77.0266,
                "timezone": "Asia/Kolkata",
                "provider_id": "geoapify-result-id",
            }
        ]
    }


def test_location_endpoint_returns_safe_provider_failure() -> None:
    app = create_app()
    app.dependency_overrides[get_location_service] = lambda: _FailingService()
    response = TestClient(app).get("/api/v1/locations/search", params={"q": "Gurgaon"})

    assert response.status_code == 503
    assert response.json() == {"detail": "Location search is temporarily unavailable."}


class _Service:
    def search(self, query: str):  # type: ignore[no-untyped-def]
        assert query == "Gurgaon"
        from astrologer.locations.models import LocationSuggestion

        return [
            LocationSuggestion(
                display_name="Gurugram, Haryana, India",
                latitude=28.4595,
                longitude=77.0266,
                timezone="Asia/Kolkata",
                provider_id="geoapify-result-id",
            )
        ]


class _FailingService:
    def search(self, query: str):  # type: ignore[no-untyped-def]
        raise LocationLookupError("Location search is temporarily unavailable.")
