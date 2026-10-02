"""API coverage for the stateless deterministic staging chart endpoint."""

from fastapi.testclient import TestClient

from astrologer.astrology.ephemeris import CelestialBody
from astrologer.main import create_app

_VALID_BIRTH_REQUEST = {
    "birth_date": "1990-01-15",
    "birth_time": "09:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 19.076,
    "longitude": 72.8777,
    "place_name": "Mumbai",
}


def test_calculate_chart_returns_required_deterministic_facts() -> None:
    client = TestClient(create_app())

    response = client.post("/api/v1/charts/calculate", json=_VALID_BIRTH_REQUEST)

    assert response.status_code == 200
    payload = response.json()
    assert payload["birth_input"]["timezone"] == "Asia/Kolkata"
    assert payload["calculation_instant"] == "1990-01-15T04:00:00Z"
    assert payload["d1"]["ascendant"] is not None
    assert {planet["body"] for planet in payload["d1"]["planets"]} == {
        body.value for body in CelestialBody
    }
    for planet in payload["d1"]["planets"]:
        assert {"sign", "longitude", "degree_in_sign", "house_number", "retrograde"} <= set(planet)
        assert {"nakshatra", "pada"} <= set(planet["nakshatra"])
    assert payload["d2"]["methodology"]["chart_type"] == "d2"
    assert payload["d9"]["methodology"]["chart_type"] == "d9"
    assert payload["d10"]["methodology"]["chart_type"] == "d10"
    assert payload["calculation_methodology"]["configuration"]["zodiac"] == "sidereal"
    assert payload["ephemeris_provenance"]["provider"]["provider_name"] == "pyswisseph"


def test_calculate_chart_rejects_invalid_latitude() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/charts/calculate",
        json={**_VALID_BIRTH_REQUEST, "latitude": 90.1},
    )

    assert response.status_code == 422


def test_calculate_chart_rejects_invalid_date() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/charts/calculate",
        json={**_VALID_BIRTH_REQUEST, "birth_date": "1990-02-30"},
    )

    assert response.status_code == 422


def test_calculate_chart_rejects_invalid_time() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/charts/calculate",
        json={**_VALID_BIRTH_REQUEST, "birth_time": "24:00:00"},
    )

    assert response.status_code == 422


def test_calculate_chart_rejects_invalid_longitude() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/charts/calculate",
        json={**_VALID_BIRTH_REQUEST, "longitude": 180.1},
    )

    assert response.status_code == 422


def test_calculate_chart_rejects_invalid_timezone() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/charts/calculate",
        json={**_VALID_BIRTH_REQUEST, "timezone": "Invalid/Timezone"},
    )

    assert response.status_code == 422


def test_calculate_chart_is_reproducible() -> None:
    client = TestClient(create_app())

    first = client.post("/api/v1/charts/calculate", json=_VALID_BIRTH_REQUEST)
    second = client.post("/api/v1/charts/calculate", json=_VALID_BIRTH_REQUEST)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
