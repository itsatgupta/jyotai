"""Run the internal CALC-01 factual perturbation report from apps/api.

Usage: uv run python tests/calc01_report.py
"""

import json

from calc01_support import load_fixtures, sensitivity


def _changed_keys(before: object, after: object) -> list[str]:
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise TypeError("sensitivity placement snapshots must be dictionaries")
    return sorted(str(key) for key in before if before[key] != after[key])


def main() -> None:
    """Emit machine-readable observations with explicit internal-only status."""
    for fixture in load_fixtures():
        snapshots = sensitivity(fixture)
        baseline = snapshots[0]
        rows = []
        for offset, current in snapshots.items():
            rows.append(
                {
                    "offset_minutes": offset,
                    "utc": current["utc"],
                    "ascendant_longitude": current["ascendant_longitude"],
                    "ascendant_sign": current["ascendant_sign"],
                    "ascendant_sign_changed": (
                        current["ascendant_sign"] != baseline["ascendant_sign"]
                    ),
                    "d1_sign_changed": _changed_keys(baseline["d1_signs"], current["d1_signs"]),
                    "d1_house_changed": _changed_keys(baseline["d1_houses"], current["d1_houses"]),
                    "house_lord_changed": _changed_keys(
                        baseline["house_lords"], current["house_lords"]
                    ),
                    "d9_ascendant_sign": current["d9_ascendant_sign"],
                    "d9_sign_changed": _changed_keys(baseline["d9_signs"], current["d9_signs"]),
                    "d9_house_changed": _changed_keys(baseline["d9_houses"], current["d9_houses"]),
                    "d10_ascendant_sign": current["d10_ascendant_sign"],
                    "d10_sign_changed": _changed_keys(baseline["d10_signs"], current["d10_signs"]),
                    "d10_house_changed": _changed_keys(
                        baseline["d10_houses"], current["d10_houses"]
                    ),
                    "moon_longitude": current["moon_longitude"],
                    "moon_nakshatra": current["moon_nakshatra"],
                    "birth_mahadasha_lord": current["birth_mahadasha_lord"],
                    "birth_antardasha_lord": current["birth_antardasha_lord"],
                    "birth_mahadasha_balance_microseconds": current[
                        "birth_mahadasha_balance_microseconds"
                    ],
                    "birth_mahadasha_end_utc": current["birth_mahadasha_end_utc"],
                    "birth_antardasha_end_utc": current["birth_antardasha_end_utc"],
                }
            )
        print(
            json.dumps(
                {
                    "id": fixture.id,
                    "input_utc": fixture.utc.isoformat(),
                    "reference_status": fixture.reference_status.value,
                    "provider": baseline["provider"],
                    "rows": rows,
                },
                separators=(",", ":"),
            )
        )


if __name__ == "__main__":
    main()
