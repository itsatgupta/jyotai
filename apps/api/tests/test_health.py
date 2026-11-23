"""Tests for service availability."""

import pytest
from fastapi.testclient import TestClient

from astrologer.main import create_app


def test_health_endpoint_returns_ok_and_unknown_commit_when_env_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "commit": "unknown"}


@pytest.mark.parametrize("value", ["", "   "])
def test_health_reports_unknown_for_blank_commit(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("RENDER_GIT_COMMIT", value)

    response = TestClient(create_app()).get("/health")

    assert response.json()["commit"] == "unknown"


def test_health_reports_render_git_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    sha = "0123456789abcdef0123456789abcdef01234567"
    monkeypatch.setenv("RENDER_GIT_COMMIT", sha)

    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "commit": sha}
