"""Production signification corpus: review packet 0b terms and the X18 lordship principle.

Admitted under a GENERAL expert approval (NEXT-ADMIT-01), "approved as proposed"; see
``docs/admissions/jyotish.signification.part0b.admission.v1.md`` and
``docs/admissions/jyotish.lordship-principle.x18.admission.v1.md``.

Terms are the packet's "Proposed for Career" column only, with its draft English as the
display.  Excluded: every term the packet marks [uncertain] (six: Mercury "बालत्वधीमतः",
Rahu "ऐश्वर्यदायकः", 2nd "मृत्युजाल", 8th "अङ्कुरादि" and "गत्यनूक", 12th "फलमन्त्यादिक"),
10th आकाशवृत्ति, 1st वर्ण, 5th राज्यापभ्रंश ("reading to confirm"), and the terms the packet
proposed as not for Career (Mars क्रोध, Venus वीर्य, Saturn दुःख).  Houses 4 and 8 have no
proposed term and so no entry.  6th शत्रु is included by owner decision (NEXT-ADMIT-01).

X18 approves the reviewed template ``period-themes-v1`` verbatim, for Mahadasha AND
Antardasha lords.  Rahu and Ketu rule no sign, so only their occupied house is used.
"""

from typing import Final

from astrologer.knowledge.career_part0_pack_v1 import (
    EXPERT_REVIEW_NOTES,
    EXPERT_REVIEWED_AT,
    EXPERT_REVIEWER,
)
from astrologer.knowledge.models import ReviewCategory, ReviewRecord, ReviewStatus
from astrologer.knowledge.signification import (
    PERIOD_THEMES_TEMPLATE_VERSION,
    ApprovedTerm,
    LordshipPrincipleRecord,
    SignificationCorpusManifest,
    SignificationEntry,
    admit_signification_corpus,
)

SIGNIFICATION_RECORD: Final = "docs/admissions/jyotish.signification.part0b.admission.v1.md"
X18_RECORD: Final = "docs/admissions/jyotish.lordship-principle.x18.admission.v1.md"

_REVIEW: Final = ReviewRecord(
    category=ReviewCategory.INTERPRETATION_REVIEW,
    status=ReviewStatus.REVIEWED,
    reviewer=EXPERT_REVIEWER,
    reviewed_at=EXPERT_REVIEWED_AT,
    notes=EXPERT_REVIEW_NOTES,
)

_CH3: Final = "BPHS ग्रहस्वरूपाध्यायः (ch. 3)"
_CH12_KARAKA: Final = "BPHS द्वादशभावविचाराध्यायः (ch. 12) v.18, PDF p. 149"
_CH12: Final = "BPHS द्वादशभावविचाराध्यायः (ch. 12)"

_RAJA: Final = ApprovedTerm(sanskrit="राजा", display="royal or sovereign role")
_SACIVA: Final = ApprovedTerm(sanskrit="सचिवः", display="minister or counsellor")
_SENA: Final = ApprovedTerm(sanskrit="सेना", display="army or forces")

# (graha, locator, terms)
_GRAHAS: Final[tuple[tuple[str, str, tuple[ApprovedTerm, ...]], ...]] = (
    ("sun", f"{_CH3} vv.1, 3, PDF pp. 24–25", (_RAJA,)),
    ("moon", f"{_CH3} vv.1, 3, PDF pp. 24–25", (_RAJA,)),
    (
        "mars",
        f"{_CH3} vv.1, 3, PDF pp. 24–25; {_CH12_KARAKA}",
        (
            ApprovedTerm(sanskrit="नेता", display="leader or commander"),
            ApprovedTerm(sanskrit="पराक्रमः", display="valour"),
        ),
    ),
    (
        "mercury",
        f"{_CH3} vv.1, 3, PDF pp. 24–25",
        (
            ApprovedTerm(sanskrit="वाणी", display="speech"),
            ApprovedTerm(sanskrit="राजकुमारः", display="prince or heir-apparent"),
        ),
    ),
    (
        "jupiter",
        f"{_CH3} vv.2, 3, PDF p. 25",
        (ApprovedTerm(sanskrit="ज्ञानम्", display="knowledge"), _SACIVA),
    ),
    ("venus", f"{_CH3} vv.2, 3, PDF p. 25", (_SACIVA,)),
    (
        "saturn",
        f"{_CH3} vv.2, 4, PDF p. 25",
        (ApprovedTerm(sanskrit="प्रेष्यकः", display="service"),),
    ),
    ("rahu", f"{_CH3} v.4, PDF p. 25", (_SENA,)),
    ("ketu", f"{_CH3} v.4, PDF p. 25", (_SENA,)),
)

# (house, verse, PDF page, terms)
_BHAVAS: Final[tuple[tuple[int, int, int, tuple[ApprovedTerm, ...]], ...]] = (
    (
        1,
        1,
        146,
        (
            ApprovedTerm(sanskrit="ज्ञान", display="knowledge"),
            ApprovedTerm(sanskrit="शील", display="conduct"),
        ),
    ),
    (2, 2, 146, (ApprovedTerm(sanskrit="धन", display="wealth"),)),
    (
        3,
        3,
        147,
        (
            ApprovedTerm(sanskrit="विक्रम", display="valour"),
            ApprovedTerm(sanskrit="भृत्य", display="servants or employees"),
            ApprovedTerm(sanskrit="उपदेश", display="instruction or counsel"),
        ),
    ),
    (
        5,
        5,
        147,
        (
            ApprovedTerm(sanskrit="विद्या", display="learning"),
            ApprovedTerm(sanskrit="बुद्धि", display="intellect"),
        ),
    ),
    (6, 6, 147, (ApprovedTerm(sanskrit="शत्रु", display="adversaries"),)),
    (7, 7, 147, (ApprovedTerm(sanskrit="व्यापार", display="trade or business"),)),
    (
        9,
        9,
        147,
        (
            ApprovedTerm(sanskrit="भाग्य", display="fortune"),
            ApprovedTerm(sanskrit="धर्म", display="dharma"),
        ),
    ),
    (
        10,
        10,
        148,
        (
            ApprovedTerm(sanskrit="राज्य", display="rulership or royal authority"),
            ApprovedTerm(sanskrit="मान", display="honour or status"),
        ),
    ),
    (
        11,
        11,
        148,
        (
            ApprovedTerm(sanskrit="लाभ", display="gain"),
            ApprovedTerm(sanskrit="वृद्धि", display="increase"),
        ),
    ),
    (12, 12, 148, (ApprovedTerm(sanskrit="व्यय", display="expenditure"),)),
)

SIGNIFICATION_ENTRIES: Final = (
    *(
        SignificationEntry(
            subject_kind="graha",
            subject=graha,
            terms=terms,
            rule_id=f"bphs.signification.graha.{graha}",
            rule_version="v1",
            source_locator=locator,
            governance_record_ref=SIGNIFICATION_RECORD,
            review=_REVIEW,
        )
        for graha, locator, terms in _GRAHAS
    ),
    *(
        SignificationEntry(
            subject_kind="bhava",
            subject=str(house),
            terms=terms,
            rule_id=f"bphs.signification.bhava.{house}",
            rule_version="v1",
            source_locator=f"{_CH12} v.{verse}, PDF p. {page}",
            governance_record_ref=SIGNIFICATION_RECORD,
            review=_REVIEW,
        )
        for house, verse, page, terms in _BHAVAS
    ),
)

LORDSHIP_PRINCIPLE: Final = LordshipPrincipleRecord(
    rule_id="jyotish.lordship-principle.x18",
    rule_version="v1",
    approved_template_version=PERIOD_THEMES_TEMPLATE_VERSION,
    scope="MAHADASHA_AND_ANTARDASHA",
    source_locator=(
        "Review packet X18 (research/next_dasha_01_review/review-packet.md). No single verse "
        "stating the principle was located in this edition; none was cited at approval."
    ),
    governance_record_ref=X18_RECORD,
    review=_REVIEW,
)

PRODUCTION_SIGNIFICATION_MANIFEST: Final = SignificationCorpusManifest(
    manifest_id="jyotish.signification.production",
    manifest_version="v1",
    entries=SIGNIFICATION_ENTRIES,
    lordship_principle=LORDSHIP_PRINCIPLE,
)

ACTIVE_SIGNIFICATION_CORPUS: Final = admit_signification_corpus(PRODUCTION_SIGNIFICATION_MANIFEST)
