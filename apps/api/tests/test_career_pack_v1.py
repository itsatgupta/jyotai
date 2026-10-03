"""Synthetic deterministic coverage for the reviewed Career Pack v1 release."""

from datetime import UTC, date, datetime, time
from decimal import Decimal

import pytest

from astrologer.astrology.chart import (
    Ascendant,
    Chart,
    ChartMethodology,
    ChartPlanet,
    WholeSignHouse,
    ZodiacSign,
    nakshatra_for_longitude,
)
from astrologer.astrology.derived_facts import DerivedFactsEngine
from astrologer.astrology.ephemeris import (
    CelestialBody,
    EphemerisConfiguration,
    EphemerisProvenance,
    ProviderMetadata,
)
from astrologer.birth.models import BirthInput
from astrologer.knowledge.career_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE,
    CAREER_RULE_ENVELOPES,
    FACT_CONTRACT,
    FACT_ID,
    PRODUCTION_MANIFEST,
    SOURCE_REGISTRY,
)
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    canonical_sha256,
    fact_set_sha256,
)
from astrologer.knowledge.models import EvidenceDirection, JyotishDomain, RulePosture
from astrologer.knowledge.production import (
    PRODUCTION_MANIFEST as HISTORICAL_MANIFEST,
)
from astrologer.knowledge.production import (
    RULE_ENVELOPE as HISTORICAL_RULE,
)
from astrologer.rules.models import EvaluationStatus, Fact, FactSet

_INSTANT = datetime(2000, 1, 1, tzinfo=UTC)
_SIGNS = tuple(ZodiacSign)


def _synthetic_bundle():
    configuration = EphemerisConfiguration()
    ascendant = ZodiacSign.ARIES
    longitude = Decimal("0")
    planets = tuple(
        ChartPlanet(
            body=body,
            longitude=longitude,
            sign=ascendant,
            degree_in_sign=longitude,
            nakshatra=nakshatra_for_longitude(longitude),
            house_number=1,
        )
        for body in CelestialBody
    )
    chart = Chart(
        methodology=ChartMethodology(configuration=configuration),
        birth_input=BirthInput(
            birth_date=date(2000, 1, 1), birth_time=time(0), timezone="UTC", latitude=0, longitude=0
        ),
        calculation_instant=_INSTANT,
        ascendant=Ascendant(
            longitude=longitude,
            sign=ascendant,
            degree_in_sign=longitude,
            nakshatra=nakshatra_for_longitude(longitude),
        ),
        houses=tuple(
            WholeSignHouse(number=index + 1, sign=sign) for index, sign in enumerate(_SIGNS)
        ),
        planets=planets,
        provenance=EphemerisProvenance(
            provider=ProviderMetadata(provider_name="synthetic", provider_version="1"),
            calculation_instant=_INSTANT,
            configuration=configuration,
        ),
    )
    return DerivedFactsEngine().calculate(chart)


def _evaluate(value: int | None):
    bundle = _synthetic_bundle()
    facts = FactSet() if value is None else FactSet(facts=(Fact(fact_id=FACT_ID, value=value),))
    provenance = FactEvaluationProvenance.from_derived_fact_bundle(bundle).model_copy(
        update={"fact_set_sha256": fact_set_sha256(facts)}
    )
    return GovernedRuleEvaluator().evaluate(
        PRODUCTION_MANIFEST,
        ACTIVE_PRODUCTION_RELEASE.envelopes,
        SOURCE_REGISTRY,
        FACT_CONTRACT,
        facts,
        provenance,
    )


@pytest.mark.parametrize(
    ("rule_id", "true_value", "false_value"),
    [
        ("bphs.d1.house_lord.10.in_4_or_10.v1", 4, 9),
        ("bphs.d1.house_lord.10.in_5_or_11.v1", 5, 9),
        ("bphs.d1.house_lord.10.in_6_or_12.v1", 6, 9),
        ("bphs.d1.house_lord.10.equals_9.v1", 9, 4),
    ],
)
def test_each_career_rule_has_true_false_unknown_and_governed_provenance(
    rule_id: str, true_value: int, false_value: int
) -> None:
    for value, expected in (
        (true_value, EvaluationStatus.TRUE),
        (false_value, EvaluationStatus.FALSE),
        (None, EvaluationStatus.UNKNOWN),
    ):
        result = next(item for item in _evaluate(value) if item.evaluation.rule_id == rule_id)
        assert result.evaluation.status is expected
        assert result.evaluation.condition.referenced_fact_ids == (FACT_ID,)
        assert result.evaluation.condition.resolved_fact_ids == (
            () if value is None else (FACT_ID,)
        )
        assert result.governance_provenance.source_id == "bphs.selected-edition"
        assert result.governance_provenance.domain is JyotishDomain.CAREER
        assert result.governance_provenance.posture is RulePosture.STATIC
        assert result.evidence_direction is EvidenceDirection.CONTEXTUAL


def test_career_release_has_only_the_reviewed_cumulative_contents() -> None:
    ids = {item.rule.rule_id for item in ACTIVE_PRODUCTION_RELEASE.envelopes}
    assert len(ids) == 5
    assert HISTORICAL_RULE.rule.rule_id in ids
    assert len(CAREER_RULE_ENVELOPES) == 4
    assert "career-candidate-01" not in ids and "career-candidate-05" not in ids
    assert all(item.domain is JyotishDomain.CAREER for item in CAREER_RULE_ENVELOPES)
    assert all(item.posture is RulePosture.STATIC for item in CAREER_RULE_ENVELOPES)
    assert all(
        item.evidence_direction is EvidenceDirection.CONTEXTUAL for item in CAREER_RULE_ENVELOPES
    )
    assert all(
        item.domain is not JyotishDomain.HEALTH for item in ACTIVE_PRODUCTION_RELEASE.envelopes
    )
    assert all(
        item.posture is not RulePosture.TIMING_REQUIRED
        for item in ACTIVE_PRODUCTION_RELEASE.envelopes
    )
    assert FACT_CONTRACT.available_fact_ids == (FACT_ID, "jyotish.d1.house_lord.11.placement_house")
    assert (
        PRODUCTION_MANIFEST.content_sha256()
        == "4f08bf77a9d15eec8a068198d3fff4f4d6741777a8fd9ae9c155bd466f674dcf"
    )
    assert (
        canonical_sha256(SOURCE_REGISTRY)
        == "5f03ceeb08c5490d5a7f5d2800fc02da99282797b640d8375594ef7a7653bca3"
    )
    assert (
        canonical_sha256(FACT_CONTRACT)
        == "aaf10bfcf7faf878a5330a67bc878b72b7fc079e62fbc4cd107c344acabc4a45"
    )
    assert HISTORICAL_MANIFEST.manifest_version == "v1"
    assert HISTORICAL_RULE.rule.domain == "general"
