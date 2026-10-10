"""Production-equivalent logging coverage for safe application diagnostics."""

import subprocess
import sys


def test_application_info_diagnostics_are_visible_with_uvicorn_defaults() -> None:
    """Uvicorn's default root WARNING must not suppress astrologer INFO records."""
    script = """
import logging
import logging.config
from uvicorn.config import LOGGING_CONFIG

from astrologer.common.logging import configure_application_logging

logging.config.dictConfig(LOGGING_CONFIG)
configure_application_logging()

for name in (
    "astrologer.application.answer",
    "astrologer.timing_rules.service",
):
    logger = logging.getLogger(name)
    assert logger.getEffectiveLevel() == logging.INFO
    assert logger.propagate
    assert not logger.handlers

logging.getLogger("astrologer.application.answer").info(
    "ask_routing domain=career requires_timing=true"
)
logging.getLogger("astrologer.timing_rules.service").info(
    "career_timing_start release=jyotish.timing.production.career@v2"
)
"""
    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "INFO astrologer.application.answer ask_routing domain=career requires_timing=true" in (
        completed.stderr
    )
    assert (
        "INFO astrologer.timing_rules.service "
        "career_timing_start release=jyotish.timing.production.career@v2" in completed.stderr
    )
    for sensitive_field in (
        "birth_date",
        "birth_time",
        "latitude",
        "longitude",
        "question=",
        "api_key",
    ):
        assert sensitive_field not in completed.stderr
