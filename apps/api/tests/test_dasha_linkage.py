"""Unit tests for jyotish.dasha_linkage.v1 (synthetic charts only; no real birth data)."""

import re

import pytest

from astrologer.astrology.chart import Chart, ChartEngine, ZodiacSign
from astrologer.astrology.dasha import DashaLord
from astrologer.astrology.dasha_linkage import (
    LORD_FACT_NAMES,
    LORDSHIP_NOTE,
    NODE_ASPECT_NOTE,
    DashaLinkageInputError,
    DashaLinkageMethodology,
    DashaLordLinkage,
    DashaPairLinkage,
    LinkageStatus,
    build_lord_linkage,
    build_pair_linkage,
    count_signs_inclusive,
    to_segment_fact_set,
)
from astrologer.astrology.derived_facts import DerivedFactBundle, DerivedFactsEngine
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput

# Synthetic noon-UTC profiles at (0, 0); none is a real person.
_SYNTHETIC_DATES = ("1978-01-01", "1965-01-01", "1990-07-01", "2001-03-15")
_NODES = (DashaLord.RAHU, DashaLord.KETU)
_CLASSICAL = tuple(lord for lord in DashaLord if lord not in _NODES)

BLOCKLIST = (
    "favourable",
    "favorable",
    "unfavourable",
    "unfavorable",
    "auspicious",
    "inauspicious",
    "strong",
    "weak",
    "good",
    "bad",
    "malefic",
    "benefic",
    "difficult",
    "challenging",
    "lucky",
    "promising",
    "6/8",
    "2/12",
    "shadashtaka",
    "dusthana",
    "kendra",
    "trikona",
    "friendly",
    "inimical",
    "enemy",
)


def blocklisted_terms(text: str) -> list[str]:
    lowered = text.lower()
    return [
        term
        for term in BLOCKLIST
        if (term in lowered if "/" in term else re.search(rf"\b{re.escape(term)}\b", lowered))
    ]


def _chart(birth_date: str) -> tuple[Chart, DerivedFactBundle]:
    birth = BirthInput(
        birth_date=birth_date, birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
    )
    chart = ChartEngine(SwissEphemerisProvider()).calculate(birth)
    return chart, DerivedFactsEngine().calculate(chart)


@pytest.fixture(scope="module", params=_SYNTHETIC_DATES)
def chart_and_facts(request: pytest.FixtureRequest) -> tuple[Chart, DerivedFactBundle]:
    return _chart(request.param)


def _values(derived: DerivedFactBundle) -> dict[str, bool | int | str]:
    return {fact.fact_id: fact.value for fact in derived.facts}


@pytest.mark.parametrize("lord", tuple(DashaLord))
def test_every_lord_projects_existing_d1_derived_facts(
    chart_and_facts: tuple[Chart, DerivedFactBundle], lord: DashaLord
) -> None:
    chart, derived = chart_and_facts
    facts = _values(derived)
    linkage = build_lord_linkage(chart, derived, lord)
    assert tuple(fact.name for fact in linkage.facts) == LORD_FACT_NAMES
    assert len({fact.fact_id for fact in linkage.facts}) == len(LORD_FACT_NAMES)
    for fact in linkage.facts:
        assert fact.fact_id.startswith(f"jyotish.dasha_linkage.v1.lord.{lord.value}.")
        assert all(source in facts for source in fact.source_fact_ids)

    tenth_lord = facts["jyotish.d1.house.10.lord"]
    placement = facts[f"jyotish.d1.planet.{lord.value}.placement_house"]
    expected_ruled = tuple(
        house for house in range(1, 13) if facts[f"jyotish.d1.house.{house}.lord"] == lord.value
    )
    assert linkage.fact("ruled_houses").value == expected_ruled
    assert linkage.fact("placement_house").value == placement
    assert linkage.fact("sign").value == facts[f"jyotish.d1.house.{placement}.sign"]
    assert linkage.fact("is_tenth_lord").value is (tenth_lord == lord.value)
    assert linkage.fact("occupies_tenth").value is (placement == 10)
    if lord in _CLASSICAL:
        for dignity in ("own_sign", "exaltation_sign"):
            assert (
                linkage.fact(dignity).value  # type: ignore[arg-type]
                is facts[f"jyotish.d1.planet.{lord.value}.{dignity}"]
            )
        assert (
            linkage.fact("aspects_tenth_house").value
            is facts[f"jyotish.d1.aspect.{lord.value}.house.10"]
        )
        if tenth_lord != lord.value:
            assert (
                linkage.fact("aspects_tenth_lord").value
                is facts[f"jyotish.d1.aspect.{lord.value}.planet.{tenth_lord}"]
            )


def test_debilitation_is_never_surfaced(chart_and_facts: tuple[Chart, DerivedFactBundle]) -> None:
    chart, derived = chart_and_facts
    for lord in DashaLord:
        linkage = build_lord_linkage(chart, derived, lord)
        assert "debilitation" not in linkage.model_dump_json()


@pytest.mark.parametrize("lord", _NODES)
def test_nodes_rule_no_sign_with_explicit_convention_note(
    chart_and_facts: tuple[Chart, DerivedFactBundle], lord: DashaLord
) -> None:
    chart, derived = chart_and_facts
    ruled = build_lord_linkage(chart, derived, lord).fact("ruled_houses")
    assert ruled.status is LinkageStatus.KNOWN
    assert ruled.value == ()
    assert ruled.note == LORDSHIP_NOTE
    assert "lordship_convention" in ruled.note
    assert "no lordship" not in ruled.note.lower()


@pytest.mark.parametrize("lord", _NODES)
def test_node_aspects_are_unknown_and_never_false(
    chart_and_facts: tuple[Chart, DerivedFactBundle], lord: DashaLord
) -> None:
    chart, derived = chart_and_facts
    linkage = build_lord_linkage(chart, derived, lord)
    for name in ("aspects_tenth_house", "aspects_tenth_lord"):
        fact = linkage.fact(name)  # type: ignore[arg-type]
        assert fact.status is LinkageStatus.UNKNOWN
        assert fact.value is None
        assert fact.value is not False
        assert fact.note == NODE_ASPECT_NOTE
    facts = to_segment_fact_set(build_pair_linkage(chart, derived, lord, lord)).by_id()
    assert not any("aspects_tenth" in fact_id for fact_id in facts)


def test_tenth_lord_relations_to_itself_are_not_applicable(
    chart_and_facts: tuple[Chart, DerivedFactBundle],
) -> None:
    chart, derived = chart_and_facts
    tenth_lord = DashaLord(str(_values(derived)["jyotish.d1.house.10.lord"]))
    linkage = build_lord_linkage(chart, derived, tenth_lord)
    assert linkage.fact("is_tenth_lord").value is True
    for name in ("same_sign_as_tenth_lord", "aspects_tenth_lord"):
        fact = linkage.fact(name)  # type: ignore[arg-type]
        assert fact.status is LinkageStatus.NOT_APPLICABLE
        assert fact.value is None
    others = [lord for lord in DashaLord if lord is not tenth_lord]
    for lord in others:
        same = build_lord_linkage(chart, derived, lord).fact("same_sign_as_tenth_lord")
        assert same.status is LinkageStatus.KNOWN
        assert isinstance(same.value, bool)


@pytest.mark.parametrize(
    ("from_sign", "to_sign", "expected"),
    [
        (ZodiacSign.LEO, ZodiacSign.LEO, 1),
        (ZodiacSign.ARIES, ZodiacSign.TAURUS, 2),
        (ZodiacSign.TAURUS, ZodiacSign.ARIES, 12),
        (ZodiacSign.PISCES, ZodiacSign.ARIES, 2),
        (ZodiacSign.SAGITTARIUS, ZodiacSign.GEMINI, 7),
    ],
)
def test_sign_count_is_inclusive_with_wrap_around(
    from_sign: ZodiacSign, to_sign: ZodiacSign, expected: int
) -> None:
    assert count_signs_inclusive(from_sign, to_sign) == expected


def test_ad_house_from_md_is_a_plain_number(
    chart_and_facts: tuple[Chart, DerivedFactBundle],
) -> None:
    chart, derived = chart_and_facts
    for md in DashaLord:
        assert build_pair_linkage(chart, derived, md, md).ad_house_from_md.value == 1
        for ad in DashaLord:
            pair = build_pair_linkage(chart, derived, md, ad)
            fact = pair.ad_house_from_md
            expected = count_signs_inclusive(
                ZodiacSign(str(pair.mahadasha.fact("sign").value)),
                ZodiacSign(str(pair.antardasha.fact("sign").value)),
            )
            assert type(fact.value) is int and fact.value == expected
            assert fact.note is None
            assert fact.fact_id == (
                f"jyotish.dasha_linkage.v1.pair.{md.value}.{ad.value}.ad_house_from_md"
            )


def test_methodology_counts_from_d1_lagna_only() -> None:
    methodology = DashaLinkageMethodology()
    assert methodology.reference_point == "d1_lagna"
    assert methodology.house_system == "whole_sign"
    assert methodology.rahu_ketu_aspects == "unmodeled"
    assert DashaLinkageMethodology.model_fields["reference_point"].annotation is not str


def test_mismatched_chart_and_derived_facts_are_rejected() -> None:
    chart, _ = _chart("1978-01-01")
    _, other = _chart("1965-01-01")
    with pytest.raises(DashaLinkageInputError):
        build_lord_linkage(chart, other, DashaLord.SUN)


def test_linkage_models_carry_no_evaluative_or_relationship_labels(
    chart_and_facts: tuple[Chart, DerivedFactBundle],
) -> None:
    chart, derived = chart_and_facts
    for md in DashaLord:
        for ad in DashaLord:
            pair = build_pair_linkage(chart, derived, md, ad)
            assert blocklisted_terms(pair.model_dump_json()) == []
    assert blocklisted_terms(DashaLinkageMethodology().model_dump_json()) == []


def test_models_are_frozen(chart_and_facts: tuple[Chart, DerivedFactBundle]) -> None:
    chart, derived = chart_and_facts
    pair = build_pair_linkage(chart, derived, DashaLord.SUN, DashaLord.MOON)
    assert isinstance(pair, DashaPairLinkage)
    assert isinstance(pair.mahadasha, DashaLordLinkage)
    with pytest.raises(ValueError):
        pair.mahadasha.facts[0].__setattr__("value", (1,))
