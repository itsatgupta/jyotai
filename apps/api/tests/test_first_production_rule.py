"""Tests for the single reviewed Task 09C2 production-rule pilot."""

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
from astrologer.astrology.derived_facts import DerivedFactsEngine, to_fact_set
from astrologer.astrology.ephemeris import (
    CelestialBody,
    EphemerisConfiguration,
    EphemerisProvenance,
    ProviderMetadata,
)
from astrologer.birth.models import BirthInput
from astrologer.knowledge.corpus import (
    EMPTY_PRODUCTION_MANIFEST,
    ProductionCorpusLoader,
    envelope_sha256,
)
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    fact_set_sha256,
)
from astrologer.knowledge.models import (
    EMPTY_SOURCE_REGISTRY,
    EvidenceDirection,
    FactContract,
    ReviewCategory,
    ReviewStatus,
)
from astrologer.knowledge.production import (
    FACT_CONTRACT,
    FACT_ID,
    PRODUCTION_MANIFEST,
    RULE_ENVELOPE,
    RULE_ID,
    RULE_VERSION,
    SOURCE_REGISTRY,
)
from astrologer.rules.models import EvaluationStatus, FactSet

_BODIES = tuple(CelestialBody)
_SIGNS = tuple(ZodiacSign)
_INSTANT = datetime(2000, 1, 1, tzinfo=UTC)


def _chart(saturn_sign: ZodiacSign) -> Chart:
    """Return an Aries D1 fixture with the 11th-house lord at a selected house."""
    configuration = EphemerisConfiguration()
    ascendant = ZodiacSign.ARIES
    signs = {body: ZodiacSign.PISCES for body in _BODIES}
    signs[CelestialBody.SATURN] = saturn_sign
    houses = tuple(
        WholeSignHouse(number=number, sign=_SIGNS[number - 1]) for number in range(1, 13)
    )
    planets = tuple(_planet(body, signs[body], ascendant) for body in _BODIES)
    return Chart(
        methodology=ChartMethodology(configuration=configuration),
        birth_input=BirthInput(
            birth_date=date(2000, 1, 1),
            birth_time=time(5, 30),
            timezone="Asia/Kolkata",
            latitude=0,
            longitude=0,
        ),
        calculation_instant=_INSTANT,
        ascendant=Ascendant(
            longitude=Decimal("0"),
            sign=ascendant,
            degree_in_sign=Decimal("0"),
            nakshatra=nakshatra_for_longitude(Decimal("0")),
        ),
        houses=houses,
        planets=planets,
        provenance=EphemerisProvenance(
            provider=ProviderMetadata(provider_name="synthetic", provider_version="1"),
            calculation_instant=_INSTANT,
            configuration=configuration,
        ),
    )


def _planet(body: CelestialBody, sign: ZodiacSign, ascendant: ZodiacSign) -> ChartPlanet:
    longitude = Decimal(_SIGNS.index(sign) * 30)
    return ChartPlanet(
        body=body,
        longitude=longitude,
        sign=sign,
        degree_in_sign=Decimal("0"),
        nakshatra=nakshatra_for_longitude(longitude),
        house_number=((_SIGNS.index(sign) - _SIGNS.index(ascendant)) % 12) + 1,
    )


def _evaluate(chart: Chart, facts: FactSet | None = None):
    bundle = DerivedFactsEngine().calculate(chart)
    supplied_facts = facts if facts is not None else to_fact_set(bundle)
    provenance = FactEvaluationProvenance.from_derived_fact_bundle(bundle).model_copy(
        update={"fact_set_sha256": fact_set_sha256(supplied_facts)}
    )
    return GovernedRuleEvaluator().evaluate(
        PRODUCTION_MANIFEST,
        (RULE_ENVELOPE,),
        SOURCE_REGISTRY,
        FACT_CONTRACT,
        supplied_facts,
        provenance,
    )[0]


def test_rule_one_source_review_interpretation_and_formalization_chain_resolve() -> None:
    source = SOURCE_REGISTRY.sources[0]
    passage = SOURCE_REGISTRY.passages[0]
    translation = SOURCE_REGISTRY.translations[0]
    interpretation = SOURCE_REGISTRY.interpretations[0]

    assert source.source_version == "v1"
    assert passage.source_id == source.source_id
    assert passage.excerpt is None
    assert passage.passage_reference is not None
    assert "82/83" in passage.locator
    assert translation.passage_id == passage.passage_id
    assert translation.language == "Hindi"
    assert interpretation.translation_id == translation.translation_id
    assert interpretation.translation_applicability.value == "required"
    assert passage.review is not None
    assert passage.review.category is ReviewCategory.SOURCE_VERIFICATION
    assert passage.review.status is ReviewStatus.REVIEWED
    assert translation.review.category is ReviewCategory.TRANSLATION_VERIFICATION
    assert translation.review.status is ReviewStatus.REVIEWED
    assert interpretation.review.category is ReviewCategory.INTERPRETATION_REVIEW
    assert interpretation.review.status is ReviewStatus.REVIEWED
    assert RULE_ENVELOPE.formalization_review is not None
    assert RULE_ENVELOPE.formalization_review.category is ReviewCategory.FORMALIZATION_REVIEW
    assert RULE_ENVELOPE.formalization_review.status is ReviewStatus.REVIEWED


def test_rule_one_contract_manifest_and_admission_are_exact_and_deterministic() -> None:
    assert FACT_CONTRACT.available_fact_ids == (FACT_ID,)
    assert FACT_CONTRACT.available_fact_family_prefixes == ()
    assert RULE_ENVELOPE.lifecycle.value == "production_active"
    assert RULE_ENVELOPE.fact_dependencies[0].fact_id == FACT_ID
    assert PRODUCTION_MANIFEST.rules[0].rule_id == RULE_ID
    assert PRODUCTION_MANIFEST.rules[0].rule_version == RULE_VERSION
    assert PRODUCTION_MANIFEST.rules[0].envelope_sha256 == envelope_sha256(RULE_ENVELOPE)
    assert len(PRODUCTION_MANIFEST.rules) == 1
    assert ProductionCorpusLoader().load(
        PRODUCTION_MANIFEST, (RULE_ENVELOPE,), SOURCE_REGISTRY, FACT_CONTRACT
    ) == (RULE_ENVELOPE.rule,)
    with pytest.raises(ValueError, match="membership"):
        ProductionCorpusLoader().load(PRODUCTION_MANIFEST, (), SOURCE_REGISTRY, FACT_CONTRACT)


@pytest.mark.parametrize(
    ("saturn_sign", "expected"),
    [
        (ZodiacSign.SAGITTARIUS, EvaluationStatus.TRUE),
        (ZodiacSign.CAPRICORN, EvaluationStatus.TRUE),
        (ZodiacSign.PISCES, EvaluationStatus.FALSE),
    ],
)
def test_rule_one_evaluates_task09a_d1_fact_statuses(
    saturn_sign: ZodiacSign, expected: EvaluationStatus
) -> None:
    result = _evaluate(_chart(saturn_sign))

    assert result.evaluation.status is expected
    assert result.evaluation.condition.referenced_fact_ids == (FACT_ID,)
    assert result.evaluation.condition.resolved_fact_ids == (FACT_ID,)


def test_rule_one_preserves_unknown_for_an_absent_fact() -> None:
    chart = _chart(ZodiacSign.SAGITTARIUS)
    result = _evaluate(chart, FactSet())

    assert result.evaluation.status is EvaluationStatus.UNKNOWN
    assert result.evaluation.condition.referenced_fact_ids == (FACT_ID,)
    assert result.evaluation.condition.resolved_fact_ids == ()


def test_rule_one_governed_provenance_is_compact_and_deterministic() -> None:
    first = _evaluate(_chart(ZodiacSign.SAGITTARIUS))
    second = _evaluate(_chart(ZodiacSign.SAGITTARIUS))
    provenance = first.governance_provenance

    assert first == second
    assert first.evidence_direction is EvidenceDirection.CONTEXTUAL
    assert provenance.rule_id == RULE_ID
    assert provenance.rule_version == RULE_VERSION
    assert provenance.manifest_id == PRODUCTION_MANIFEST.manifest_id
    assert provenance.manifest_content_sha256 == PRODUCTION_MANIFEST.content_sha256()
    assert provenance.registry_version == SOURCE_REGISTRY.registry_version
    assert provenance.source_id == SOURCE_REGISTRY.sources[0].source_id
    assert provenance.passage_id == SOURCE_REGISTRY.passages[0].passage_id
    assert provenance.translation_id == SOURCE_REGISTRY.translations[0].translation_id
    assert provenance.interpretation_id == SOURCE_REGISTRY.interpretations[0].interpretation_id
    assert provenance.fact_contract_id == FACT_CONTRACT.contract_id
    assert FACT_ID not in str(first.governance_provenance)
    assert SOURCE_REGISTRY.translations[0].text not in first.model_dump_json()


def test_historical_empty_manifest_is_unchanged_and_evaluates_no_rules() -> None:
    assert (
        EMPTY_PRODUCTION_MANIFEST.content_sha256()
        == "f2b95924b75cf9d5abb4d644cb035199de447d7b666d226ae8b2ba9036b072ff"
    )
    facts = to_fact_set(DerivedFactsEngine().calculate(_chart(ZodiacSign.SAGITTARIUS)))
    bundle = DerivedFactsEngine().calculate(_chart(ZodiacSign.SAGITTARIUS))
    assert (
        GovernedRuleEvaluator().evaluate(
            EMPTY_PRODUCTION_MANIFEST,
            (),
            EMPTY_SOURCE_REGISTRY,
            FactContract(
                contract_id="jyotish.d1.structural",
                contract_version="v1",
                chart_scope=RULE_ENVELOPE.chart_scope,
                methodology_id="jyotish-derived-facts-v1",
            ),
            facts,
            FactEvaluationProvenance.from_derived_fact_bundle(bundle),
        )
        == ()
    )
