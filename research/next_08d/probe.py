"""Reproduce research-only chart facts and current answers for synthetic profiles."""

import json
from datetime import UTC, datetime
from pathlib import Path

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.astrology.chart import ChartEngine, ZodiacSign
from astrologer.astrology.derived_facts import SIGN_RULERS
from astrologer.astrology.ephemeris import CelestialBody
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.astrology.vargas import DivisionalChartType, VargaEngine
from astrologer.birth.models import BirthInput
from astrologer.composition import DeterministicAnswerComposer
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.timing_rules.service import CareerTimingAnalysisService

PROFILE_PATH = Path(__file__).resolve().parents[2] / "apps/api/tests/fixtures/calc01_profiles.json"
PROFILE_IDS = ("india_ordinary", "ascendant_sign_boundary", "southern_hemisphere")
QUESTION = "What profession should I choose?"
AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
SIGNS = tuple(ZodiacSign)


def main() -> None:
    profiles = {profile["id"]: profile for profile in json.loads(PROFILE_PATH.read_text())}
    provider = SwissEphemerisProvider()
    service = AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
    )
    outputs = []
    for profile_id in PROFILE_IDS:
        profile = profiles[profile_id]
        birth = BirthInput(
            **{
                key: profile[key]
                for key in ("birth_date", "birth_time", "timezone", "latitude", "longitude")
            }
        )
        d1 = ChartEngine(provider).calculate(birth)
        d9 = VargaEngine().calculate(d1, DivisionalChartType.D9)
        d1_planets = {planet.body: planet for planet in d1.planets}
        d9_planets = {planet.body: planet for planet in d9.planets}
        branches = {}
        for reference, sign in (
            ("lagna", d1.ascendant.sign),
            ("moon", d1_planets[CelestialBody.MOON].sign),
            ("sun", d1_planets[CelestialBody.SUN].sign),
        ):
            tenth_sign = SIGNS[(SIGNS.index(sign) + 9) % 12]
            lord = SIGN_RULERS[tenth_sign]
            navamsa_sign = d9_planets[lord].sign
            branches[reference] = {
                "reference_sign": sign.value,
                "tenth_sign": tenth_sign.value,
                "tenth_lord": lord.value,
                "tenth_lord_d1_sign": d1_planets[lord].sign.value,
                "tenth_lord_d1_longitude": str(d1_planets[lord].longitude),
                "tenth_lord_d9_sign": navamsa_sign.value,
                "navamsa_ruler": SIGN_RULERS[navamsa_sign].value,
            }
        result = service.answer(
            DeterministicAnalysisRequest(birth_input=birth, as_of=AS_OF, question=QUESTION)
        )
        outputs.append(
            {
                "profile_id": profile_id,
                "utc": birth.utc_datetime.isoformat(),
                "question": QUESTION,
                "current_production_answer": result.answers[0].answer,
                "d1_ascendant_sign": d1.ascendant.sign.value,
                "d1_moon_sign": d1_planets[CelestialBody.MOON].sign.value,
                "d1_sun_sign": d1_planets[CelestialBody.SUN].sign.value,
                "branches_calculated_not_selected": branches,
                "d1_configuration": d1.methodology.configuration.model_dump(mode="json"),
                "d9_variant": d9.methodology.mapping_variant.value,
                "provider": d1.provenance.provider.model_dump(mode="json"),
            }
        )
    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
