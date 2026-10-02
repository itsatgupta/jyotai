"""Hand-computable deterministic tests for Vimshottari Dasha v1."""

from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

import pytest

from astrologer.astrology.chart import (
    Ascendant,
    Chart,
    ChartMethodology,
    ChartPlanet,
    Nakshatra,
    WholeSignHouse,
    ZodiacSign,
    nakshatra_for_longitude,
)
from astrologer.astrology.dasha import DashaLord, VimshottariDashaEngine, lord_for_nakshatra
from astrologer.astrology.ephemeris import (
    CelestialBody,
    EphemerisConfiguration,
    EphemerisProvenance,
    ProviderMetadata,
)
from astrologer.birth.models import BirthInput

_BIRTH = datetime(2000, 1, 1, tzinfo=UTC)
_YEAR_US = 31_557_600_000_000
_NAKSHATRA_WIDTH = Decimal("40") / Decimal("3")


def _chart(moon_longitude: Decimal, *, moon_nakshatra_valid: bool = True) -> Chart:
    birth_input = BirthInput(
        birth_date=date(2000, 1, 1),
        birth_time=time(5, 30),
        timezone="Asia/Kolkata",
        latitude=0,
        longitude=0,
    )
    moon_nakshatra = nakshatra_for_longitude(moon_longitude)
    if not moon_nakshatra_valid:
        moon_nakshatra = moon_nakshatra.model_copy(update={"nakshatra": Nakshatra.BHARANI})
    configuration = EphemerisConfiguration()
    provenance = EphemerisProvenance(
        provider=ProviderMetadata(
            provider_name="hand-fixture",
            provider_version="1",
            ephemeris_data_version="Moshier internal ephemeris",
        ),
        calculation_instant=_BIRTH,
        configuration=configuration,
    )
    return Chart(
        methodology=ChartMethodology(configuration=configuration),
        birth_input=birth_input,
        calculation_instant=_BIRTH,
        ascendant=Ascendant(
            longitude=Decimal("0"),
            sign=ZodiacSign.ARIES,
            degree_in_sign=Decimal("0"),
            nakshatra=nakshatra_for_longitude(Decimal("0")),
        ),
        houses=tuple(
            WholeSignHouse(number=index + 1, sign=ZodiacSign.ARIES) for index in range(12)
        ),
        planets=(
            ChartPlanet(
                body=CelestialBody.MOON,
                longitude=moon_longitude,
                sign=ZodiacSign.ARIES,
                degree_in_sign=moon_longitude % Decimal("30"),
                nakshatra=moon_nakshatra,
                house_number=1,
            ),
        ),
        provenance=provenance,
    )


@pytest.mark.parametrize(
    ("nakshatra", "lord"),
    [(nakshatra, tuple(DashaLord)[index % 9]) for index, nakshatra in enumerate(Nakshatra)],
)
def test_all_27_nakshatras_repeat_the_vimshottari_lord_sequence(
    nakshatra: Nakshatra, lord: DashaLord
) -> None:
    assert lord_for_nakshatra(nakshatra) is lord


@pytest.mark.parametrize(
    ("longitude", "nakshatra", "lord"),
    [
        (Decimal("0"), Nakshatra.ASHWINI, DashaLord.KETU),
        (_NAKSHATRA_WIDTH - Decimal("0.000000000000000001"), Nakshatra.ASHWINI, DashaLord.KETU),
        (_NAKSHATRA_WIDTH, Nakshatra.BHARANI, DashaLord.VENUS),
    ],
)
def test_nakshatra_boundaries_select_the_correct_birth_lord(
    longitude: Decimal, nakshatra: Nakshatra, lord: DashaLord
) -> None:
    timeline = VimshottariDashaEngine().calculate(_chart(longitude), _BIRTH + timedelta(days=1))

    assert timeline.provenance.methodology.birth_nakshatra is nakshatra
    assert timeline.provenance.methodology.birth_nakshatra_lord is lord


def test_moon_at_nakshatra_start_has_full_initial_mahadasha() -> None:
    timeline = VimshottariDashaEngine().calculate(_chart(Decimal("0")), _BIRTH + timedelta(days=1))
    period = timeline.mahadashas[0]

    assert period.lord is DashaLord.KETU
    assert period.start == _BIRTH
    assert period.end == _BIRTH + timedelta(microseconds=7 * _YEAR_US)


def test_moon_halfway_through_nakshatra_has_half_initial_mahadasha_remaining() -> None:
    timeline = VimshottariDashaEngine().calculate(
        _chart(_NAKSHATRA_WIDTH / Decimal("2")), _BIRTH + timedelta(days=1)
    )
    period = timeline.mahadashas[0]

    assert period.start == _BIRTH - timedelta(microseconds=7 * _YEAR_US // 2)
    assert period.end == _BIRTH + timedelta(microseconds=7 * _YEAR_US // 2)


def test_mahadasha_sequence_and_complete_cycle_are_exact() -> None:
    through = _BIRTH + timedelta(microseconds=120 * _YEAR_US)
    timeline = VimshottariDashaEngine().calculate(_chart(Decimal("0")), through)

    assert tuple(period.lord for period in timeline.mahadashas) == tuple(DashaLord)
    assert timeline.mahadashas[-1].end == through


def test_antardashas_follow_cumulative_proportions_without_gaps_or_drift() -> None:
    timeline = VimshottariDashaEngine().calculate(_chart(Decimal("0")), _BIRTH + timedelta(days=1))
    mahadasha = timeline.mahadashas[0]
    antardashas = mahadasha.antardashas

    assert tuple(period.lord for period in antardashas) == tuple(DashaLord)
    assert antardashas[0].end == _BIRTH + timedelta(microseconds=7 * _YEAR_US * 7 // 120)
    assert antardashas[-1].end == mahadasha.end
    assert all(
        left.end == right.start for left, right in zip(antardashas, antardashas[1:], strict=False)
    )
    assert all(period.start < period.end for period in antardashas)


def test_lookup_uses_half_open_boundaries_and_returns_new_period_at_transition() -> None:
    engine = VimshottariDashaEngine()
    chart = _chart(Decimal("0"))
    first = engine.at(chart, _BIRTH)
    second = engine.at(chart, first.antardasha.end)

    assert first.antardasha.lord is DashaLord.KETU
    assert second.antardasha.lord is DashaLord.VENUS
    assert second.instant.tzinfo is UTC


def test_results_are_reproducible_and_include_frozen_and_chart_provenance() -> None:
    engine = VimshottariDashaEngine()
    chart = _chart(Decimal("0"))
    through = _BIRTH + timedelta(days=500)

    first = engine.calculate(chart, through)
    second = engine.calculate(chart, through)
    provenance = first.provenance

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert provenance.methodology.methodology_id == "vimshottari-v1"
    assert provenance.methodology.dasha_year_days == Decimal("365.25")
    assert provenance.methodology.dasha_year_microseconds == _YEAR_US
    assert provenance.methodology.timestamp_resolution == "microsecond"
    assert provenance.methodology.fractional_microsecond_rounding == "ROUND_HALF_EVEN"
    assert provenance.inherited_ephemeris_provenance == chart.provenance
    assert provenance.source_birth_timezone == "Asia/Kolkata"


def test_engine_uses_chart_moon_only_and_rejects_invalid_inputs() -> None:
    engine = VimshottariDashaEngine()
    chart = _chart(Decimal("0"))

    with pytest.raises(ValueError, match="timezone-aware"):
        engine.calculate(chart, datetime(2001, 1, 1))
    with pytest.raises(ValueError, match="after"):
        engine.calculate(chart, _BIRTH)
    with pytest.raises(ValueError, match="before"):
        engine.at(chart, _BIRTH - timedelta(microseconds=1))
    with pytest.raises(ValueError, match="inconsistent"):
        engine.calculate(
            _chart(Decimal("0"), moon_nakshatra_valid=False),
            _BIRTH + timedelta(days=1),
        )
    with pytest.raises(ValueError, match="exactly one D1 Moon"):
        engine.calculate(chart.model_copy(update={"planets": ()}), _BIRTH + timedelta(days=1))
