"""Production signification corpus v3 and X18 v2 (NEXT-ADMIT-02).

Source: the reviewer's Sitting 1 + 2 written verdicts (``pandit-ji-verdicts-2026-11-24.md``),
recorded in ``docs/admissions/jyotish.admit02.sitting-1-2.admission.v1.md``.  The
NEXT-ADMIT-01 corpora (v1, v2) and X18 v1 stay unchanged in ``signification_part0b_v1``.

Changes relative to corpus v2:

* Sitting 2 items 1–9: the reviewer's modern glosses become the English display.  The
  Sanskrit term of every entry stays exactly as admitted (``ApprovedTerm.sanskrit``), so the
  evidence keeps the source word; only the display text changes.  An entry with a changed
  gloss gets a new record (``rule_version`` "v2"); entries without one keep their v1 record.
* Sitting 1 item 28: 6th-house शत्रु is restored as "adversaries, opposition, competition"
  (new record, ``rule_version`` "v2").  It is a signification term only, never a Career rule.
* X18 v2: the compact Period-themes template ``period-themes-v2`` (Sitting 2 item 10) with
  one closing at the end of the section; Mahadasha primary and Antardasha secondary (Sitting 1
  item 27, Sitting 2 item 17); its basis is labelled a project interpretive convention with no
  source verse identified (Sitting 2 item 30).
"""

from typing import Final

from astrologer.knowledge.admit02_pack_v1 import ADMIT02_RECORD, admit02_review
from astrologer.knowledge.models import ReviewCategory
from astrologer.knowledge.signification import (
    PERIOD_THEMES_COMPACT_TEMPLATE_VERSION,
    ApprovedTerm,
    LordshipPrincipleRecord,
    SignificationCorpusManifest,
    SignificationEntry,
    admit_signification_corpus,
)
from astrologer.knowledge.signification_part0b_v1 import SIGNIFICATION_ENTRIES

# Sitting 2 items 1–9: Sanskrit term → the reviewer's display gloss.
GLOSSES_ADMIT02: Final[dict[str, str]] = {
    "राजकुमारः": "heir, successor or senior/deputy role",
    "राज्य": "authority or office",
    "राजा": "head, authority or governing role",
    "सेना": "forces, personnel or organized workforce",
    "सचिवः": "adviser or counsellor",
    "भृत्य": "employees or staff",
    "नेता": "leader",
    "पराक्रमः": "courage",
    "विक्रम": "courage, initiative or enterprise",
}
# Sitting 1 item 28.
SHATRU_DISPLAY: Final = "adversaries, opposition, competition"
X18_BASIS_LABEL: Final = (
    "project interpretive convention, reviewer-approved; no source verse identified"
)
PERIOD_THEMES_CLOSING_V2: Final = (
    "These are the reviewed themes associated with this period; actual results depend on the "
    "full chart and other active factors."
)

_GLOSS_REVIEW: Final = admit02_review(ReviewCategory.INTERPRETATION_REVIEW, "Sitting 2 items 1-9")
_SHATRU_REVIEW: Final = admit02_review(ReviewCategory.INTERPRETATION_REVIEW, "Sitting 1 item 28")


def _superseding(entry: SignificationEntry) -> SignificationEntry:
    """A v2 record when a term's display changes (gloss or शत्रु), else the v1 record."""
    terms = tuple(
        ApprovedTerm(
            sanskrit=term.sanskrit,
            display=SHATRU_DISPLAY
            if term.sanskrit == "शत्रु"
            else GLOSSES_ADMIT02.get(term.sanskrit, term.display),
        )
        for term in entry.terms
    )
    if terms == entry.terms:
        return entry
    shatru = any(term.sanskrit == "शत्रु" for term in entry.terms)
    return entry.model_copy(
        update={
            "terms": terms,
            "rule_version": "v2",
            "governance_record_ref": ADMIT02_RECORD,
            "review": _SHATRU_REVIEW if shatru else _GLOSS_REVIEW,
        }
    )


# Built from the v1 entry list, which still holds the 6th-house entry that v2 removed.
SIGNIFICATION_ENTRIES_V3: Final = tuple(_superseding(entry) for entry in SIGNIFICATION_ENTRIES)

LORDSHIP_PRINCIPLE_V2: Final = LordshipPrincipleRecord(
    rule_id="jyotish.lordship-principle.x18",
    rule_version="v2",
    approved_template_version=PERIOD_THEMES_COMPACT_TEMPLATE_VERSION,
    scope="MAHADASHA_PRIMARY_ANTARDASHA_SECONDARY",
    source_locator=f"X18: {X18_BASIS_LABEL} (Sitting 2 item 30).",
    governance_record_ref=ADMIT02_RECORD,
    review=admit02_review(
        ReviewCategory.INTERPRETATION_REVIEW,
        "Sitting 2 items 10, 17 and 30; Sitting 1 item 27",
    ),
)

PRODUCTION_SIGNIFICATION_MANIFEST_V3: Final = SignificationCorpusManifest(
    manifest_id="jyotish.signification.production",
    manifest_version="v3",
    entries=SIGNIFICATION_ENTRIES_V3,
    lordship_principle=LORDSHIP_PRINCIPLE_V2,
)

ACTIVE_SIGNIFICATION_CORPUS: Final = admit_signification_corpus(
    PRODUCTION_SIGNIFICATION_MANIFEST_V3
)
