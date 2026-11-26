"""NEXT-MARRIAGE-02: calculated D9 (Navamsa) factors for marriage answers (facts only).

Sentences are built only from the existing deterministic D9 chart (``VargaEngine``,
Parashari Navamsa) and its structural facts (``jyotish-d9-derived-facts-v1``):

* the D9 Lagna (``jyotish.d9.house.1.sign``);
* the D9 7th house's sign, its lord and the lord's D9 house.  The lord is read with the same
  classical seven-planet sign rulership the D1 facts use (``SIGN_RULERS``, a JyotAI-v1
  computational convention); Rahu and Ketu are never lords;
* Venus's D9 sign and house;
* whether the D1 7th lord is vargottama: the same sign in D1 and D9 (its D1 sign is the sign
  of the D1 house it occupies; both values are calculated, so the answer is TRUE or FALSE,
  and UNKNOWN only when a fact is missing).

No D9 interpretation is given: no reviewed method or wording exists for reading D9 for
marriage (an open methodology item), so the section ends with a fixed framing line.
"""

from collections.abc import Mapping
from typing import Final

from astrologer.astrology.chart import Chart, ZodiacSign
from astrologer.astrology.derived_facts import SIGN_RULERS
from astrologer.astrology.varga_derived_facts import VargaStructuralFactsEngine
from astrologer.astrology.vargas import DivisionalChartType, VargaEngine
from astrologer.composition.models import SynthesisSentence
from astrologer.knowledge.models import ChartScope

D9_METHODOLOGY_ID: Final = "jyotish-d9-derived-facts-v1"
D9_LORDSHIP_CONVENTION: Final = "classical seven-planet sign rulership (JyotAI-v1 convention)"
D9_FRAMING: Final = (
    "These are calculated D9 (Navamsa) positions; no reviewed interpretation of the D9 chart "
    "for marriage exists yet, so JyotAI reads no meaning into them."
)


def d9_marriage_factors(
    chart: Chart, d1_facts: Mapping[str, object]
) -> tuple[SynthesisSentence, ...]:
    """The calculated D9 sentences, then the framing line; empty if D9 is unavailable."""
    d9_chart = VargaEngine().calculate(chart, DivisionalChartType.D9)
    bundle = VargaStructuralFactsEngine().calculate(d9_chart, ChartScope.D9_NAVAMSA)
    d9 = {fact.fact_id: fact.value for fact in bundle.facts}
    methods = (D9_METHODOLOGY_ID,)
    sentences: list[SynthesisSentence] = []

    lagna = _sign(d9.get("jyotish.d9.house.1.sign"))
    if lagna is not None:
        sentences.append(
            SynthesisSentence(
                text=f"Your D9 Lagna is {lagna.value.title()}.",
                fact_ids=("jyotish.d9.house.1.sign",),
                calc_method_ids=methods,
            )
        )

    seventh_sign = _sign(d9.get("jyotish.d9.house.7.sign"))
    lord = SIGN_RULERS[seventh_sign].value if seventh_sign is not None else None
    if seventh_sign is not None and lord == "venus":  # Venus's own line carries its house
        sentences.append(
            SynthesisSentence(
                text=f"Your D9 7th house is {seventh_sign.value.title()}; its lord is Venus.",
                fact_ids=("jyotish.d9.house.7.sign",),
                calc_method_ids=(*methods, D9_LORDSHIP_CONVENTION),
            )
        )
    elif seventh_sign is not None and lord is not None:
        house_id = f"jyotish.d9.planet.{lord}.placement_house"
        house = _int(d9.get(house_id))
        if house is not None:
            sentences.append(
                SynthesisSentence(
                    text=(
                        f"Your D9 7th house is {seventh_sign.value.title()}; its lord, "
                        f"{lord.title()}, is in the {_ordinal(house)} house of your D9 chart."
                    ),
                    fact_ids=("jyotish.d9.house.7.sign", house_id),
                    calc_method_ids=(*methods, D9_LORDSHIP_CONVENTION),
                )
            )

    venus_sign = _sign(d9.get("jyotish.d9.planet.venus.sign"))
    venus_house = _int(d9.get("jyotish.d9.planet.venus.placement_house"))
    if venus_sign is not None and venus_house is not None:
        role = ", your D9 7th lord," if lord == "venus" else ""
        sentences.append(
            SynthesisSentence(
                text=(
                    f"Venus{role} is in {venus_sign.value.title()}, in the "
                    f"{_ordinal(venus_house)} house of your D9 chart."
                ),
                fact_ids=(
                    "jyotish.d9.planet.venus.sign",
                    "jyotish.d9.planet.venus.placement_house",
                ),
                calc_method_ids=methods,
            )
        )

    vargottama = _vargottama(d1_facts, d9)
    if vargottama is not None:
        sentences.append(vargottama)
    if not sentences:
        return ()
    return (*sentences, SynthesisSentence(text=D9_FRAMING))


def _vargottama(
    d1_facts: Mapping[str, object], d9: Mapping[str, object]
) -> SynthesisSentence | None:
    lord = d1_facts.get("jyotish.d1.house.7.lord")
    placed = _int(d1_facts.get("jyotish.d1.house_lord.7.placement_house"))
    if not isinstance(lord, str) or placed is None:
        return None
    d1_sign_id = f"jyotish.d1.house.{placed}.sign"
    d9_sign_id = f"jyotish.d9.planet.{lord}.sign"
    d1_sign, d9_sign = _sign(d1_facts.get(d1_sign_id)), _sign(d9.get(d9_sign_id))
    if d1_sign is None or d9_sign is None:
        return None
    same = d1_sign is d9_sign
    verdict = (
        "so it is vargottama (the same sign in D1 and D9)"
        if same
        else "so it is not vargottama (vargottama means the same sign in D1 and D9)"
    )
    return SynthesisSentence(
        text=(
            f"Your D1 7th lord, {lord.title()}, is in {d1_sign.value.title()} in D1 and in "
            f"{d9_sign.value.title()} in D9, {verdict}."
        ),
        fact_ids=(
            "jyotish.d1.house.7.lord",
            "jyotish.d1.house_lord.7.placement_house",
            d1_sign_id,
            d9_sign_id,
        ),
        calc_method_ids=("jyotish-derived-facts-v1", D9_METHODOLOGY_ID),
    )


def _sign(value: object) -> ZodiacSign | None:
    if not isinstance(value, str):
        return None
    try:
        return ZodiacSign(value)
    except ValueError:
        return None


def _int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _ordinal(number: int) -> str:
    suffix = (
        "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"
