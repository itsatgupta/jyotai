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
    HISTORICAL_CAREER_RULE_ENVELOPES_V2,
    HISTORICAL_PRODUCTION_MANIFEST_V2,
    HISTORICAL_PRODUCTION_RELEASE_V2,
    HISTORICAL_SOURCE_REGISTRY_V2,
    PRODUCTION_MANIFEST,
    SOURCE_REGISTRY,
)
from astrologer.knowledge.corpus import envelope_sha256
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

_EXPECTED_USER_FACING_STATEMENTS = {
    "bphs.d1.house_lord.10.in_4_or_10.v1": (
        "With the D1 tenth-house lord in the fourth or tenth house, this is contextual "
        "evidence for career matters. The text associates this placement with knowledge, "
        "comfort, courage, devotion or worship, and dharmic and truth-oriented qualities. "
        "These broader life themes do not by themselves establish a profession, promotion, "
        "income, or timing."
    ),
    "bphs.d1.house_lord.10.in_5_or_11.v1": (
        "With the D1 tenth-house lord in the fifth or eleventh house, this is contextual "
        "evidence for career matters. The text associates this placement with wealth, "
        "children, contentment, truthfulness, and comfort. These are broader life themes, "
        "not a specific career outcome; they do not by themselves establish a profession, "
        "promotion, income, or timing."
    ),
    "bphs.d1.house_lord.10.in_6_or_12.v1": (
        "With the D1 tenth-house lord in the sixth or twelfth house, this is contextual "
        "evidence for career matters. The text associates this placement with adversarial "
        "difficulty or affliction, cleverness, and less comfort. These broader life themes "
        "do not by themselves establish a profession, promotion, income, or timing."
    ),
    "bphs.d1.house_lord.10.equals_9.v1": (
        "With the D1 tenth-house lord in the ninth house, this is contextual evidence for "
        "career matters. The text associates this placement with family support or protection, "
        "good companions or friends, maternal devotion, and worship. These are broader life "
        "themes, not a specific career outcome; they do not by themselves establish a "
        "profession, promotion, income, or timing."
    ),
}


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
        == "88b1650b62f4f05719707b8911d2cb2e748d11a5b9f924ca9fa481e97f0e0749"
    )
    assert (
        canonical_sha256(SOURCE_REGISTRY)
        == "d88ef9f482f50be6b602ea2f78ae0f6b935d3a62bccc29614a8baaf51826cd45"
    )
    assert (
        canonical_sha256(FACT_CONTRACT)
        == "aaf10bfcf7faf878a5330a67bc878b72b7fc079e62fbc4cd107c344acabc4a45"
    )
    assert HISTORICAL_MANIFEST.manifest_version == "v1"
    assert HISTORICAL_RULE.rule.domain == "general"


def test_historical_v2_release_remains_byte_identical_and_v3_admits_only_v2_wording() -> None:
    assert HISTORICAL_PRODUCTION_MANIFEST_V2.content_sha256() == (
        "4f08bf77a9d15eec8a068198d3fff4f4d6741777a8fd9ae9c155bd466f674dcf"
    )
    assert canonical_sha256(HISTORICAL_SOURCE_REGISTRY_V2) == (
        "5f03ceeb08c5490d5a7f5d2800fc02da99282797b640d8375594ef7a7653bca3"
    )
    assert canonical_sha256(HISTORICAL_PRODUCTION_RELEASE_V2) == (
        "65a88aaa03bbc71521d51ddf0b1ab1b7779f5f5dcf3f40ee78762625d32cd263"
    )
    assert HISTORICAL_PRODUCTION_RELEASE_V2.release_version == "v2"
    assert ACTIVE_PRODUCTION_RELEASE.release_version == "v3"
    assert set(
        (item.rule.rule_id, item.rule.rule_version)
        for item in HISTORICAL_PRODUCTION_RELEASE_V2.envelopes
    ) == set(
        (item.rule.rule_id, item.rule.rule_version) for item in ACTIVE_PRODUCTION_RELEASE.envelopes
    )
    historical_by_rule_id = {
        item.rule.rule_id: item for item in HISTORICAL_CAREER_RULE_ENVELOPES_V2
    }
    for current in CAREER_RULE_ENVELOPES:
        historical = historical_by_rule_id[current.rule.rule_id]
        assert current.rule.condition == historical.rule.condition
        assert current.interpretation_id != historical.interpretation_id
        assert envelope_sha256(current) != envelope_sha256(historical)
    historical_versions = {
        item.interpretation_id: item.interpretation_version
        for item in HISTORICAL_SOURCE_REGISTRY_V2.interpretations
        if item.interpretation_id.startswith("bphs.bhavesha-phala.10th-lord")
    }
    active_versions = {
        item.interpretation_id: item.interpretation_version
        for item in SOURCE_REGISTRY.interpretations
        if item.interpretation_id.startswith("bphs.bhavesha-phala.10th-lord")
    }
    assert set(historical_versions.values()) == {"v1"}
    assert set(active_versions.values()) == {"v1", "v2"}


def test_each_career_rule_maps_to_its_reviewed_user_facing_statement() -> None:
    interpretations = {
        interpretation.interpretation_id: interpretation
        for interpretation in SOURCE_REGISTRY.interpretations
    }

    assert {
        envelope.rule.rule_id: interpretations[envelope.interpretation_id].statement
        for envelope in CAREER_RULE_ENVELOPES
    } == _EXPECTED_USER_FACING_STATEMENTS
