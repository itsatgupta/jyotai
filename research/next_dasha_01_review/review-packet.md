# Independent review packet: natal Career completion, significations, and Dasha-for-Career principles (BPHS)

**Status: `REVIEW_REQUESTED` — nothing in this packet is approved or active.**
Prepared 2026-11-23 for an independent Jyotish/Sanskrit reviewer. The preparer (an AI
assistant) is **not** a reviewer, and nothing here counts as approval.

## How to use this packet

**Priority:** Part 0, then Part 1. Part 0 (0a: the 10th lord in houses 1, 2, 3, 7, 8;
0b: graha and bhava significations; X18) comes first. Part 1 (P1–P6, X1–X10 and X17)
follows. Part 2 (the appendix "Part 2 — comparison and promotion", X11, X12, X14, X15)
is optional and can wait until Parts 0 and 1 are decided.

Each principle below asks for one decision: **Approve / Reject / Amend**. Approval of a
principle admits *only* the formal condition and user-facing wording you sign off on. Your
decision is recorded on a governance record (`governance-record-template.md`), and only
that record can move a rule into production.

Please work from the **page images**, not from the text in this packet. The "OCR text"
blocks are the raw machine text layer of the PDF and contain visible corruption. The
"probable reading" blocks are the preparer's reconstruction from OCR and the edition's own
Hindi rendering. They are **not** transcriptions from the page images. Correct them freely.

## Source

| Field | Value |
| --- | --- |
| Work | *Bṛhat Parāśara Horā Śāstra* (बृहत्पाराशरहोराशास्त्रम्) |
| Edition | Ed. (late) Gaṇeśadatta Pāṭhaka, formerly head of the Jyotiṣa dept., Jokhīrām Maṭarūmal Goyankā Mahāvidyālaya, Kāśī; with Hindi rendering. Publisher: Sāvitrī Ṭhākura Prakāśana, Rathayātrā, Vārāṇasī; distributor Ṭhākura Prasāda Kailāśanātha Bookseller. Revised edition. Price ₹200. **Year: the title verso OCR reads "२००९". Whether that is CE 2009 or Vikrama Saṃvat 2009 (≈1952 CE) is unconfirmed. Please check the image (PDF pp. 1–2).** |
| Local artifact | `पराशरहोराशास्त्र Brihat Parashar Hora Shastra _text.pdf` (repo root), 800 PDF pages |
| Artifact SHA-256 | `d333ebe1a4c6ab16ba2ed18bf87ea3d02966a393e2dc2c04d5ccdd9107a66108` |
| Section | अथ दशाफलाध्यायः (Dasha-phala), sub-portion on house-lord Dashas (भावेशानां दशाफलम्) |
| Pages | printed pp. 438–440 = local PDF pp. 436–438 (printed = PDF + 2, consistent with existing project records) |
| Part 0 sources | Other chapters of the same edition, listed at the start of Part 0 (PDF pp. 24–25, 146–149, 193) |

This is the same artifact the project already uses for the dignity admission
(`docs/DIGNITY_SOURCE_ADMISSION.md`) and for the existing v.87 timing rule. Those earlier
reviews were **internal project-owner reviews, not independent scholarly certification**.

## Where this fits: current project state for this section

| Verse | Clause | Current state in code |
| --- | --- | --- |
| 87b | 10th lord in 4th → Dasha *rājya-pradāyinī* | **Production** (`timing_rules/models.py` `TimingSourceRecord`), Mahadasha only, internal review |
| 89b | 9th lord in 10th → Dasha *rājya-pradāyinī* | **Candidate only**, not production (`NinthLordInTenthTimingSourceRecord`) |
| 89a | 5th lord in 10th → Dasha *sampatkarī* | Explicitly **not admitted** |
| 88 | conjunction/aspect extension of 87 | Explicitly **not admitted** |
| 90–95 | relative-house and adverse clauses | Explicitly **not admitted** |

## Calculation conventions the conditions depend on

These are project computation conventions. Approving a principle does **not** certify them.
See CALC-02 below.

- Sidereal Lahiri; D1 Whole Sign houses; houses counted **from the D1 Lagna only**.
- Classical seven-planet sign rulers. Rahu and Ketu own no sign.
- "In house N" means the planet occupies the Nth Whole Sign from Lagna.
- "Joined with" (*saṃyuta*) means the same Whole Sign (proposed; see X4).
- Vimshottari Dasha, 365.25-day year, true nodes.
- **CALC-02: NO-GO for independent calculation certification.** Internal checks pass, but no
  independent numerical reference has been obtained. Any approved rule inherits this caveat.

---

## Part 0 — natal Career completion and significations (decide first)

Part 0 gives every chart a governed natal Career reading. Today a chart whose 10th lord sits
in house 1, 2, 3, 7 or 8 has **no** admitted Career rule (the admitted rules cover 4/10,
5/11, 6/12 and 9). Part 0 also proposes the per-graha and per-bhava significations that a
"Period themes" sentence could later use (gated on X18). Same edition and conventions as
the rest of this packet: printed page = PDF page + 2. The "Edition's Hindi rendering" lines
are the preparer's reading of the edition's own Hindi, summarized, never quoted.

| Item | Chapter | Verses | PDF pages (printed) |
| --- | --- | --- | --- |
| 0a | भावेशफलाध्यायः, अथ कर्मेशभावफलम् (10th lord in the houses) | 71, 72, 76 | 193 (195) |
| 0b grahas | ग्रहस्वरूपाध्यायः (ch. 3, nature of the grahas) | 1–4 | 24–25 (26–27) |
| 0b grahas (secondary) | द्वादशभावविचाराध्यायः (ch. 12), kāraka verse | 17–18 | 149 (151) |
| 0b bhavas | द्वादशभावेषु विचार्यत्वम् (ch. 12, what is judged from each house) | 1–12 | 146–148 (148–150) |

**Not located:** a fixed (*sthira*) bhāva-kāraka list (e.g. "Sun and Jupiter for the 10th").
The kāraka chapter mentions *sthira-kārakas* only in passing (v.20, PDF p. 106) and gives no
list in this edition. None is proposed.

### 0a. The 10th lord in houses 1, 2, 3, 7 and 8

These mirror the admitted 10th-lord rules (vv.73, 74, 75, 77; `career_pack_v1`): natal,
`CONTEXTUAL`, no polarity, one fact condition, fixed non-guarantee wording. All five missing
placements are located; v.72 groups three of them, as v.73–75 group pairs.

#### 0a-1. 10th lord in the 1st (v.71)

**Locator:** printed p. 195, PDF p. 193, verse 71 (first verse of अथ कर्मेशभावफलम्).

**OCR text (raw, as extracted):**
```
कर्मेशाधिपतौ लग्ने कवितागुणसंयुतः।
बाल्ये रोगी सुखी पश्न्चादर्थवृद्धि्दिने दिने।।७९।।
```
(The OCR verse number reads "७९"; its position between v.70 and v.72 and the Hindi
numbering give 71.)

**Probable reading (unverified):** `कर्माधिपतौ लग्ने कवितागुणसंयुतः। बाल्ये रोगी सुखी पश्चादर्थवृद्धिर्दिने दिने॥`
("कर्मेशाधिपतौ" read as "कर्माधिपतौ": please check the image.)

**Edition's Hindi rendering:** PDF p. 193. As the preparer reads it, consistent with the
draft below (poetic ability, illness in childhood, comfort later, daily growth of wealth).

**Draft translation (preparer, unreviewed):** "When the lord of the tenth is in the Lagna, the
native is endowed with poetic gifts; sickly in childhood, happy afterwards, with wealth
growing day by day."

**Proposed formal condition** (natal rule):
```
jyotish.d1.house_lord.10.placement_house == 1
```

**Proposed domain / posture:** Career, `CONTEXTUAL`, no polarity (X11 applies later). The
childhood-illness clause is a health statement: the preparer proposes **leaving it out** of
user wording (high-stakes topic), keeping it only in the source record.

**Proposed user wording (for amendment):** "With the D1 tenth-house lord in the first house,
this is contextual evidence for career matters. The text associates this placement with
poetic or literary ability, more comfort later in life, and wealth that grows over time.
These broader life themes do not by themselves establish a profession, promotion, income,
or timing."

**Test cases:**
| ID | Chart | Expected |
| --- | --- | --- |
| T0a.1.1 | Aries Lagna (10th lord Saturn); Saturn in Aries | MATCH |
| T0a.1.2 | Aries Lagna; Saturn in Capricorn (10th) | NO_MATCH (v.73 applies instead) |
| T0a.1.3 | 10th-lord placement fact not resolvable | UNKNOWN |

#### 0a-2. 10th lord in the 2nd, 3rd or 7th (v.72)

**Locator:** printed p. 195, PDF p. 193, verse 72.

**OCR text (raw):**
```
धने मदे च सहजे कर्मेशो यदि संस्थितः ।
मनस्वी गुणवान्‌ वाग्मी सत्यधर्मसमन्वितः । ।७२।।
```

**Probable reading (unverified):** as OCR. मद (*mada*) is read as the 7th house; the
edition's Hindi lists the houses as 2, 3, 7.

**Edition's Hindi rendering:** PDF p. 193. As the preparer reads it, it gives the same
houses and the same qualities (high-minded, virtuous, articulate, truthful).

**Draft translation (unreviewed):** "If the tenth lord is placed in the second, the seventh
or the third, the native is high-minded, virtuous, eloquent, and endowed with truth and
dharma."

**Proposed formal condition:**
```
jyotish.d1.house_lord.10.placement_house in {2, 3, 7}
```

**Proposed domain / posture:** Career, `CONTEXTUAL`, no polarity.

**Proposed user wording:** "With the D1 tenth-house lord in the second, third or seventh
house, this is contextual evidence for career matters. The text associates this placement
with a high-minded, virtuous and articulate nature, and with truthfulness and dharma. These
broader life themes do not by themselves establish a profession, promotion, income, or
timing."

**Test cases:**
| ID | Chart | Expected |
| --- | --- | --- |
| T0a.2.1 | Aries Lagna; Saturn in Taurus (2nd) | MATCH |
| T0a.2.2 | Aries Lagna; Saturn in Gemini (3rd) | MATCH |
| T0a.2.3 | Aries Lagna; Saturn in Libra (7th) | MATCH |
| T0a.2.4 | Aries Lagna; Saturn in Leo (5th) | NO_MATCH (v.74 applies instead) |

#### 0a-3. 10th lord in the 8th (v.76)

**Locator:** printed p. 195, PDF p. 193, verse 76.

**OCR text (raw):**
```
कर्मेशो रन्ध्रगे जातो क्रूरो चौरोऽथवा धूत्तः
अल्पायुरसदक्तां मातृसखन्तापकारकः । 1७६ । ।
```

**Probable reading (unverified):** `कर्मेशे रन्ध्रगे जातः क्रूरश्चौरोऽथवा धूर्तः। अल्पायुरसदुक्तिश्च मातृसन्तापकारकः॥`
The second line is **uncertain**: "असदक्तां" may be असदुक्ति / असत्यवक्ता (untruthful
speech). Please check the image.

**Edition's Hindi rendering:** PDF p. 193. As the preparer reads it: cruel, a thief or a
rogue, untruthful in speech, causing distress to the mother. The preparer could not find the
short-life clause (*alpāyu*) in the Hindi line as OCR'd.

**Draft translation (unreviewed):** "If the tenth lord is in the eighth, the native is cruel, a
thief or a rogue, short-lived [uncertain], untruthful in speech [uncertain], and causes
distress to his mother."

**Proposed formal condition:**
```
jyotish.d1.house_lord.10.placement_house == 8
```

**Preparer's caution:** every quality in v.76 is adverse, and *alpāyu* (short life) is a
lifespan statement, which is a high-stakes topic. The preparer proposes either (a) admitting
the condition with **no** user wording beyond "the reviewed text describes this placement
in adverse terms; this does not establish character, conduct, lifespan or any outcome", or
(b) keeping it out of production until X11 (polarity) is decided. The lifespan clause should
not be shown under either option.

**Proposed domain / posture:** Career, `CONTEXTUAL` pending X11; adverse wording withheld
from users as above.

**Test cases:**
| ID | Chart | Expected |
| --- | --- | --- |
| T0a.3.1 | Aries Lagna; Saturn in Scorpio (8th) | MATCH |
| T0a.3.2 | Aries Lagna; Saturn in Sagittarius (9th) | NO_MATCH (v.77 applies instead) |

With 0a-1 to 0a-3 admitted, every resolvable 10th-lord placement (1–12) has exactly one
natal Career rule.

### 0b. Career-relevant significations (*kārakatva*) of the grahas and bhavas

One row per graha and per bhava. Only terms the text gives. "Proposed for Career" is the
preparer's suggestion of which terms a Career "Period themes" sentence may use; the reviewer
decides. Use the **Keep / strike** column per term (K = keep, S = strike, A = amend + text).
Terms marked **[uncertain]** come from a corrupted or ambiguous reading, and the preparer
proposes excluding them.

#### Grahas

| Graha | Verse ref (PDF p.) | Sanskrit term(s) as given | Draft English (unreviewed) | Proposed for Career | Keep / strike |
| --- | --- | --- | --- | --- | --- |
| Sun | ch.3 v.1, v.3 (24–25) | कालात्मा; राजा (राजानौ भानुहिमगू) | soul of the Kālapuruṣa (self); king, sovereign | राजा: royal or sovereign role | आत्मा __ राजा __ |
| Moon | ch.3 v.1, v.3 (24–25) | मनः; राजा | mind; king, sovereign | राजा: royal or sovereign role | मनः __ राजा __ |
| Mars | ch.3 v.1, v.3 (24–25); ch.12 v.18 (149) | सत्त्वम्; नेता; पराक्रमः; क्रोधः | inner strength, fortitude; leader, commander; valour; anger | नेता, पराक्रम (क्रोध proposed **not** for Career) | सत्त्व __ नेता __ पराक्रम __ क्रोध __ |
| Mercury | ch.3 v.1, v.3 (24–25); ch.12 v.18 (149) | वाणी (वाणीप्रदायकः); राजकुमारः; "बालत्वधीमतः" **[uncertain]** | speech; prince, heir-apparent; intellect? [uncertain] | वाणी, राजकुमार | वाणी __ राजकुमार __ [uncertain] exclude __ |
| Jupiter | ch.3 v.2, v.3 (25) | ज्ञानम्, सुखम् (ज्ञानसुखदः); सचिवः | knowledge, happiness; minister, counsellor | ज्ञान, सचिव | ज्ञान __ सुख __ सचिव __ |
| Venus | ch.3 v.2, v.3 (25) | वीर्यम् (वीर्यप्रदायकः); सचिवः | vigour, potency; minister, counsellor | सचिव (वीर्य proposed **not** for Career) | वीर्य __ सचिव __ |
| Saturn | ch.3 v.2, v.4 (25) | दुःखम् (दुःखदः); प्रेष्यकः | sorrow; servant, attendant, one who is sent | प्रेष्यक, as "service" (दुःख proposed **not** for Career) | दुःख __ प्रेष्यक __ |
| Rahu | ch.3 v.4 (25); ch.12 v.18 (149) | सेना (with Ketu); "ऐश्वर्यदायकः" **[uncertain]** (OCR "राहुरैन्वर्यदायकः") | army, forces; lordship/prosperity? [uncertain] | सेना | सेना __ [uncertain] exclude __ |
| Ketu | ch.3 v.4 (25) | सेना (with Rahu) | army, forces | सेना | सेना __ |

Not proposed: varṇa (ch.3 v.10), physical descriptions (ch.3 vv.12–19), bodily tissues
(v.20), places (v.21) and other non-Career lists. These are text-given but not Career
significations. Descriptions such as Jupiter's सर्वशास्त्रविशारद (v.16) and Venus's
काव्यकर्ता (v.17) describe the graha's nature, not a *kārakatva* list, so they are not
proposed.

#### Bhavas (ch. 12, "what is to be judged from each house")

| Bhava | Verse ref (PDF p.) | Sanskrit term(s) as given | Draft English (unreviewed) | Proposed for Career | Keep / strike |
| --- | --- | --- | --- | --- | --- |
| 1 | v.1 (146) | तनु, रूप, ज्ञान, वर्ण, बलाबल, शील, प्रकृति | body, appearance, knowledge, complexion or class (ambiguous), strength and weakness, conduct, temperament | ज्ञान, शील (वर्ण proposed for exclusion: ambiguous, may mean caste) | ________ |
| 2 | v.2 (146) | धन, धान्य, कुटुम्ब, "मृत्युजाल" **[uncertain]**, अमित्र, धातु-रत्न | wealth, grain, family, death? [uncertain], enemies, metals and gems | धन | ________ |
| 3 | v.3 (147) | विक्रम, भृत्य, भ्रातृ, उपदेश, प्रयाण, पित्रोर्मरण | valour, servants or employees, siblings, instruction or counsel, journeys, death of the father | विक्रम, भृत्य, उपदेश | ________ |
| 4 | v.4 (147) | वाहन, बन्धु, मातृसौख्य, निधि, क्षेत्र, गृह | vehicles, relatives, mother's happiness, treasure, land, house | none proposed | ________ |
| 5 | v.5 (147) | यन्त्र, मन्त्र, विद्या, बुद्धि, प्रबन्ध, पुत्र, राज्यापभ्रंश | instruments, mantras, learning, intellect, composition, children, fall from position or authority | विद्या, बुद्धि (राज्यापभ्रंश: reading to confirm) | ________ |
| 6 | v.6 (147) | मातुल, अन्तकशङ्का, शत्रु, व्रण, सपत्नीमातृ | maternal uncle, fear of death, enemies, wounds, stepmother | शत्रु, as "adversaries" (reviewer to confirm Career use) | ________ |
| 7 | v.7 (147) | जाया, अध्वप्रयाण, व्यापार, हतवीक्षण, स्वदेहमरण | spouse, road journeys, trade or business, lost things, one's own death | व्यापार | ________ |
| 8 | v.8 (147) | ऋणदान-ग्रहण, गुद, "अङ्कुरादि" **[uncertain]**, "गत्यनूक" **[uncertain]** | lending and borrowing, the anus (ailments), [uncertain], past and future births? [uncertain] | none proposed | ________ |
| 9 | v.9 (147) | भाग्य, धर्म, श्याल, भ्रातृपत्नी, तीर्थयात्रा | fortune, dharma, wife's brother, brother's wife, pilgrimage | भाग्य, धर्म | ________ |
| 10 | v.10 (148) | राज्य, आकाशवृत्ति, मान, पितृ, प्रवास, ऋण | rulership or royal authority, "sky-livelihood" (meaning uncertain), honour or status, father, residence abroad, debt | राज्य, मान (आकाशवृत्ति: gloss uncertain, proposed for exclusion unless the reviewer supplies one) | ________ |
| 11 | v.11 (148) | नानावस्तुभव, पुत्र, जाया, लाभ, वृद्धि, पशु | acquisition of various things, children, spouse, gain, increase, cattle | लाभ, वृद्धि | ________ |
| 12 | v.12 (148) | व्यय, वैरिवृत्तान्त, "फलमन्त्यादिक" **[uncertain]** | expenditure, the affairs of enemies, final results? [uncertain] | व्यय | ________ |

A kept term becomes an approved signification only through a governance record. It is never
shown as an event, an outcome or a strength. Its use in a sentence depends on X18.

---

## Part 1 — Dasha-for-Career principles

## Cross-cutting decisions (apply to every principle)

Please decide these once. A principle cannot be activated while any decision it depends on
is still open.

| ID | Question | Options | Preparer's note |
| --- | --- | --- | --- |
| X1 | Does "the Dasha of lord L" mean the **Mahadasha** only, or also **Antardasha**? | MD only · MD and AD · MD, and AD only under a stated condition | The existing v.87 rule is MD-only. Elsewhere in the chapter (v.76, Venus section) "स्वभक्तौ फलमेवं स्यात्" extends results to the planet's own bhukti. Is that general or Venus-specific? |
| X2 | Does **v.80** limit these principles? v.80: a house lord that is strong, in own/exaltation/mūlatrikoṇa or benefic varga gives full results; one in an enemy or debilitation sign, or weak, gives adverse results. | (a) principles fire unconditionally, with v.80 as a separate future rule · (b) withhold (UNKNOWN) when the lord is in debilitation/enemy sign · (c) principle cannot be admitted until a strength model exists · **(d) minimal convention: use only the existing dignity flags (exaltation sign, own sign, debilitation sign) as the v.80 qualifier, and nothing heavier** | **First question for the reviewer: is (d) enough?** That is, is a three-flag sign-only convention a faithful minimum for v.80, or does v.80 inherently need enemy-sign, mūlatrikoṇa, varga or degree-based strength? Please answer this before anything heavier is proposed. Status of the flags: own sign and exaltation sign are source-admitted (`docs/DIGNITY_SOURCE_ADMISSION.md`, BPHS vv. 7–24 and 38). Debilitation sign is computed but **not** admitted. Its source, v.39 on the same page (printed p. 32), was explicitly left out, so (d) also needs that small admission. Under (d), every other case (enemy sign, mūlatrikoṇa, "weak") stays UNKNOWN, not FALSE. |
| X3 | Is counting **from the D1 Lagna** the correct reading for this section (तन्वादिभावेशजम्, "arising from the lords of the houses beginning with the body")? | Lagna only · Lagna and other references | The planned implementation (NEXT-DASHA-01) is Lagna-only. vv.90ff (यस्मात्…) count *from other points* and are out of scope. |
| X4 | Is *saṃyuta* (joined) satisfied by **same Whole Sign**, or does it need a degree orb? | Same sign · orb of N° · other | Affects P6 only. |
| X5 | How should **rājya**, **nṛpāśraya**, **śubha**, **sampat** be rendered for modern users? | Literal with limits · bounded paraphrase · no user wording | The existing v.87 wording is "rājya-related results", with explicit non-guarantees (no promotion, office, income, date). |
| X6 | **Domain mapping for non-wealth results:** is *rājya* (P1 status clause, P3) Career evidence? Is *śubha* (P5, P6) Career evidence at all? | Per principle | A *śubha* (auspicious) Dasha is not automatically a Career claim. Wealth and gain results are handled separately in X8. |
| X7 | When several principles fire for one Dasha (e.g. Saturn as both 10th and 11th lord for Aries Lagna), are they shown as **separate attributed claims**? | Separate, no aggregation · a reviewed combination policy | The proposal is separate and unaggregated. No scoring. |
| X8 | **Domain mapping for "wealth" and "gain" results**, applying to every principle with such a result: P1 *vitta* (wealth through patronage), P2 *lābha* (gain), P4 *sampat* (prosperity), and any future principle of this kind. | For each: **Career** · **Income** · **both** · neither | Decides which questions may cite the result. "Career" means questions about work, status and direction. "Income" means questions about earnings and money. "Both" allows each, and the wording must not convert a gain claim into a salary, amount or date. |
| X9 | Does a period lord's **dispositorship of the 10th lord** (ruling the sign the 10th lord occupies) carry **Career** meaning in Dasha? | No: a calculated relationship only · Yes, but only as a separate principle with its own cited verse and review · Defer until a source is identified | Raised by the Career year synthesis (`career-synthesis-v1`), which already shows this relationship as a calculated shared-house reference (the period lord rules the house the 10th lord occupies) and states no meaning for it. No verse in this packet has been identified as covering it, and the preparer proposes none. Until reviewed, the relationship stays a calculated fact with no Career interpretation: UNKNOWN, not FALSE. |
| X10 | **Plain-language display text.** For each admitted or proposed rule, approve a plain-language `display_text` (e.g. a gloss of *rājya-pradāyinī*), or reject it and keep the verbatim text. | Per rule: **approve** the proposed `display_text` · **amend** (state the wording) · **reject** and keep the verbatim admitted text | Raised by the plain-language Career answer (NEXT-CAREER-02c). Today the user-facing direct line quotes the admitted wording byte-for-byte (e.g. "that lord’s Dasha is described as rājya-pradāyinī—giving rājya-related results"); the application never rewords admitted rule text. A `display_text` would be a separate, reviewer-approved field shown alongside or instead of the verbatim text; the verbatim text and its non-guarantee sentence stay the source of record. Until a rule's `display_text` is approved, only the verbatim text is shown. Applies to the admitted v.87 rule and to every principle in this packet. |
| X17 | Do P1 and P2 (Dasha of the 10th / 11th lord) apply when that lord is the Antardasha lord, or only the Mahadasha lord? | Mahadasha lord only · Mahadasha or Antardasha lord · Antardasha lord only under a stated condition (state it and cite it) | The specific case of X1 for P1 and P2. Raised by the Career year view, which already shows, as calculated facts with no meaning, when an Antardasha lord is the 10th lord or shares the 10th lord's sign. Until this is decided, an Antardasha of the 10th or 11th lord gets no P1/P2 interpretation: UNKNOWN, not FALSE. |
| X18 | May a Dasha lord be described as bringing forward the significations of the houses it rules and occupies (Parashari lordship principle)? Approve / amend / reject, with the exact wording to use. | **Approve** the proposed wording · **amend** (state the exact wording) · **reject** | Gates the planned "Period themes" sentence (Part 0b). The preparer has **not** located a single verse that states this principle in general form in this edition; the preparer believes it underlies the house-lord Dasha verses (vv.78–79, P1, P2), but that is the preparer's reading, not a cited source. Please cite a verse if you approve. Proposed template, for amendment: "During your <Lord> <Mahadasha/Antardasha>, the reviewed significations associated with <Lord> (<terms>) and with the houses it rules and occupies (<house>: <terms>; …) are the themes the texts associate with this period. This does not predict an event or an outcome." Until X18 is approved **and** the 0b terms are kept, no period-themes text is shown (UNKNOWN, not FALSE). |

### Dasha-conditioning summary

| Principle | Verse | Dasha-conditioned? | Natal precondition |
| --- | --- | --- | --- |
| P1 | 79 | Yes, inherited from v.78's frame (to confirm) | none |
| P2 | 79 | Yes, inherited from v.78's frame (to confirm) | none |
| P3 | 89b | Yes, explicit (`धर्मेशदशा`) | 9th lord in 10th |
| P4 | 89a | Yes, explicit (`पञ्चमेशदशा`) | 5th lord in 10th |
| P5 | 85 | Yes, explicit (`तयोर्दशां`) | 4th lord in 10th AND 10th lord in 4th |
| P6 | 83b | Yes, explicit (`सुतेश्वरस्यापि दशा`) | 5th lord in same sign as 10th lord |

No principle in this packet is a purely natal rule. If the reviewer finds that v.78's frame
does not govern v.79, P1 and P2 must be relabelled as natal and re-reviewed as natal rules.

---

## P1. Dasha of the tenth-house lord (v.79, clause)

**Locator:** printed p. 438, PDF p. 436, verse 79 (a single verse listing the Dasha results of
the lords of houses 1–12 in order; vv.78–79 together).

**OCR text (raw, as extracted):**
```
त्यु ृतयुतेः करोति नियतं धर्मेशितुः सल्क्रियाम्‌-
-वित्तं राजपतेर्मपाश्रयमथोलाभं हिलाभेशितु
रोगं द्रव्यविना्नं च वहुधा कष्ट॒व्ययेशस्य वै-पूर्वङ्गभृतामुदीरितमिदं
तन्वादिभावेशजम्‌ ।। ७ ९।।
```

**Probable reading of the cited clause (unverified):** `वित्तं राज्यपतेर्नृपाश्रयम्`
(OCR "राजपते" vs "राज्यपते", and "र्मपाश्रयम" read as "र्नृपाश्रयम्": please check the image.)

**Edition's Hindi rendering:** PDF p. 436. As the preparer reads it, the Hindi assigns wealth
through royal shelter to the 10th lord. Its OCR looks truncated around the 8th- and
9th-lord clauses. Please check the image.

**Draft translation (preparer, unreviewed):** "[The Dasha] of the lord of the tenth (*rājya*)
house gives wealth through the shelter/patronage of the king."

**Why it is a candidate:** it applies to every chart, since every chart has a 10th lord. The
condition is a single deterministic fact. Its position in the 1→12 list identifies the lord.

**Dasha-conditioned?** **Yes, by inheritance.** v.79 does not itself repeat दशा. It continues
the list that v.78 opens with `लग्नेशस्य दशा…`, and closes with तन्वादिभावेशजम्. *Reviewer:
confirm that the Dasha frame of v.78 governs every clause of v.79.* If it does not, P1 is a
natal statement and must be relabelled.

**Proposed formal condition** (timing rule, evaluated per Vimshottari interval):
```
jyotish.timing.vimshottari.mahadasha.lord == jyotish.d1.house.10.lord
  [X1: or jyotish.timing.vimshottari.antardasha.lord == jyotish.d1.house.10.lord]
```
No natal precondition: the claim exists only inside a matching Dasha interval.

**Proposed domain:** status/patronage (rājya) → X6; the wealth (*vitta*) result → X8.

**Proposed user wording (for amendment):** "In the reviewed BPHS Dasha-phala passage, the
Dasha of the tenth-house lord is described as bringing gain through patronage or authority.
Within JyotishAI this is broad period context for career and status matters. It does not
guarantee employment, promotion, office, income, or any specific event or date."

**Test cases:**
| ID | Chart / period | Expected |
| --- | --- | --- |
| T1.1 | Aries Lagna (10th = Capricorn, lord Saturn); Saturn MD | MATCH |
| T1.2 | Aries Lagna; Jupiter MD (Jupiter rules 9th, 12th) | NO_MATCH |
| T1.3 | Any Lagna; Rahu MD | NO_MATCH: Rahu rules no sign under the seven-ruler convention. *Reviewer: confirm no node co-lordship.* |
| T1.4 | Lagna not established (birth time unknown) | UNKNOWN |
| T1.5 | Aries Lagna; Venus MD / Saturn AD | Depends on X1: MATCH if AD is included, else NO_MATCH |

**Decision:** see the decision block at the end (P1).

---

## P2. Dasha of the eleventh-house lord (v.79, clause)

**Locator:** same verse as P1 (printed p. 438, PDF p. 436).

**OCR text:** see P1 (`…मथोलाभं हिलाभेशितु…`).

**Probable reading of the cited clause (unverified):** `अथो लाभं हि लाभेशितुः`

**Edition's Hindi rendering:** PDF p. 436; consistent with the probable reading.

**Draft translation (unreviewed):** "…and [the Dasha] of the lord of the eleventh (*lābha*)
house, gain."

**Dasha-conditioned?** **Yes, by inheritance** from v.78, as for P1. The same confirmation is
needed.

**Proposed formal condition** (timing rule, evaluated per Vimshottari interval):
```
jyotish.timing.vimshottari.mahadasha.lord == jyotish.d1.house.11.lord
  [X1: or jyotish.timing.vimshottari.antardasha.lord == jyotish.d1.house.11.lord]
```
No natal precondition.

**Proposed domain:** the gain (*lābha*) result → X8 (Career / Income / both).

**Proposed user wording:** "The reviewed passage describes the Dasha of the eleventh-house
lord as a period of gain (*lābha*). This is broad context only. It does not establish an
income amount, a salary change, investment returns, or a date."

**Test cases:**
| ID | Chart / period | Expected |
| --- | --- | --- |
| T2.1 | Taurus Lagna (11th = Pisces, lord Jupiter); Jupiter MD | MATCH |
| T2.2 | Taurus Lagna; Mars MD (Mars rules 7th, 12th) | NO_MATCH |
| T2.3 | Aries Lagna; Saturn MD (Saturn rules both 10th and 11th) | P1 MATCH **and** P2 MATCH as two separate attributed claims (X7) |
| T2.4 | Lagna not established | UNKNOWN |

---

## P3. Dasha of the ninth lord placed in the tenth (v.89b): production decision

**Locator:** printed p. 440, PDF p. 438, verse 89, second line.

**OCR text (raw):**
```
कर्मस्थानस्थ वुद्धीशदशा सम्पत्करी भवेत्‌ ।
मास्ति तपोधीश दशा राज्यप्रदायिनी ।। ८ ९।।
```

**Existing project reading** (`NinthLordInTenthTimingSourceRecord`, internal):
`दशमस्थ धर्मेशदशा राज्यप्रदायिनी ॥ ८९ ॥`. The OCR reads "मास्ति तपोधीश". Is the original
`मानस्थित-तपोधीश…` (मान = 10th, तपोधीश = 9th lord)? The edition's Hindi rendering (PDF
p. 438) describes the ninth lord placed in the tenth. Please authenticate the exact wording.

**Existing translation (internal):** "The Dasha of the ninth-house lord placed in the tenth
house gives rājya-related results."

**Question:** this clause is already implemented as a **candidate**. Should it be promoted to
production on the same terms as v.87b (MD only, broad context, non-guarantee wording)?

**Dasha-conditioned?** **Yes, explicitly** (`धर्मेशदशा`, "the Dasha of the ninth lord"). The
placement is a natal precondition. On its own it is not a claim.

**Proposed formal condition** (timing rule):
```
natal:  jyotish.d1.house_lord.9.placement_house == 10
Dasha:  jyotish.timing.vimshottari.mahadasha.lord == jyotish.d1.house.9.lord
        [X1: or ...antardasha.lord == jyotish.d1.house.9.lord]
```
This matches the existing candidate (MD only).

**Test cases:**
| ID | Chart / period | Expected |
| --- | --- | --- |
| T3.1 | Leo Lagna (9th = Aries, lord Mars); Mars in Taurus (10th); Mars MD | MATCH |
| T3.2 | Leo Lagna; Mars in Aries (9th); Mars MD | NO_MATCH |
| T3.3 | Aries Lagna (9th lord Jupiter); Jupiter in Capricorn (10th, Jupiter's traditional debilitation sign); Jupiter MD | MATCH on the bare verse. **This tests X2:** should v.80 withhold or modify it? |
| T3.4 | Lagna not established | UNKNOWN |

---

## P4. Dasha of the fifth lord placed in the tenth (v.89a)

**Locator:** printed p. 440, PDF p. 438, verse 89, first line (OCR above).

**Existing project reading:** `कर्मस्थानस्थ पञ्चमेशदशा सम्पत्करी भवेत् ।`. The OCR has
`वुद्धीश` (= बुद्धीश, lord of the 5th, the house of intellect). Please confirm which word the
edition prints. The edition's Hindi rendering (PDF p. 438) describes the fifth lord in the
tenth house.

**Existing translation (internal):** "The Dasha of the fifth-house lord placed in the tenth
house gives prosperity."

**Dasha-conditioned?** **Yes, explicitly** (`पञ्चमेशदशा` / `बुद्धीशदशा`). The placement is a
natal precondition.

**Proposed formal condition** (timing rule):
```
natal:  jyotish.d1.house_lord.5.placement_house == 10
Dasha:  jyotish.timing.vimshottari.mahadasha.lord == jyotish.d1.house.5.lord
        [X1: or ...antardasha.lord == jyotish.d1.house.5.lord]
```

**Proposed domain:** the prosperity (*sampat*) result → X8 (Career / Income / both).

**Test cases:**
| ID | Chart / period | Expected |
| --- | --- | --- |
| T4.1 | Leo Lagna (5th = Sagittarius, lord Jupiter); Jupiter in Taurus (10th); Jupiter MD | MATCH |
| T4.2 | Gemini Lagna (5th = Libra, lord Venus); Venus in Pisces (10th); Venus MD | MATCH (Venus is also exaltation-sign. The admitted fact is shown; no strength is inferred.) |
| T4.3 | Cancer Lagna: Mars rules both 5th (Scorpio) and 10th (Aries); Mars in Aries; Mars MD | Literal MATCH. *Reviewer: does the 5th lord placed in its own 10th-house sign count?* |
| T4.4 | Leo Lagna; Jupiter in Sagittarius (5th); Jupiter MD | NO_MATCH |

---

## P5. Exchange of the fourth and tenth lords (v.85)

**Locator:** printed p. 439, PDF p. 437, verse 85.

**OCR text (raw):**
```
सुखेशो मानभावस्थो मानेशो सुखराशिगः ।
तयोर्दशां शुभां प्राहुज्योतिः शाख्रविदोजनाः \। ८५।।
```

**Probable reading (unverified):**
`सुखेशो मानभावस्थो मानेशः सुखराशिगः । तयोर्दशां शुभां प्राहुर्ज्योतिःशास्त्रविदो जनाः ॥ ८५ ॥`

**Edition's Hindi rendering:** PDF p. 437. It reads the verse as both placements together
making both Dashas favourable.

**Draft translation (unreviewed):** "When the lord of the fourth is in the tenth house and the
lord of the tenth is in the fourth, the knowers of jyotiṣa declare the Dashas of both to be
auspicious."

**Interpretive questions:**
1. Are both placements required (a mutual exchange), or does each placement suffice
   separately? The proposal reads तयोः ("of those two") as requiring both.
2. *śubha* (auspicious) is general. Is this Career evidence at all (X6)?
3. This overlaps v.87b, which is in production: 10th lord in 4th → *rājya-pradāyinī* on its own.
   v.85 would add the **4th lord's** Dasha under exchange. Please confirm the two are
   independent claims.

**Dasha-conditioned?** **Yes, explicitly** (`तयोर्दशां`, "the Dashas of those two"). The
exchange is a natal precondition.

**Proposed formal condition** (timing rule; two separate claims, one per lord):
```
natal:  jyotish.d1.house_lord.4.placement_house == 10
        AND jyotish.d1.house_lord.10.placement_house == 4
Dasha:  jyotish.timing.vimshottari.mahadasha.lord == jyotish.d1.house.4.lord
     OR jyotish.timing.vimshottari.mahadasha.lord == jyotish.d1.house.10.lord
        [X1: same with ...antardasha.lord]
```

**Test cases:**
| ID | Chart / period | Expected |
| --- | --- | --- |
| T5.1 | Aries Lagna (4th lord Moon, 10th lord Saturn); Moon in Capricorn, Saturn in Cancer; Moon MD, and separately Saturn MD | MATCH, MATCH |
| T5.2 | Aries Lagna; Saturn in Cancer, Moon in Leo; Saturn MD | P5 NO_MATCH (one-way only); the existing v.87b production rule still MATCHES separately |
| T5.3 | Aries Lagna; exchange present; Jupiter MD | NO_MATCH |
| T5.4 | Lagna not established | UNKNOWN |

---

## P6. Fifth lord joined with the tenth lord (v.83b)

**Locator:** printed p. 439, PDF p. 437. The OCR prints the verse number as "४३" between
vv.82 and 84. Please confirm it is v.83.

**OCR text (raw):**
```
स पचमेशस्य तपोधिपस्य दशा भवेद्राज्यसुखार्थलाभदा ।
तथैव मानाधिपसंयुतस्य सुतेश्वरस्यापि दशाशुभास्यात्‌ ।।४३।।
```

**Probable reading (unverified):**
`सपञ्चमेशस्य तपोऽधिपस्य दशा भवेद्राज्यसुखार्थलाभदा । तथैव मानाधिपसंयुतस्य सुतेश्वरस्यापि दशा शुभा स्यात् ॥ ८३ ॥`

**Critical sandhi question:** `दशाशुभास्यात्` can split as **दशा शुभा स्यात्** ("is
auspicious") or **दशा अशुभा स्यात्** ("is inauspicious"). The preparer reads शुभा because of
तथैव ("likewise", following a favourable first line) and because the edition's Hindi
rendering (PDF p. 437) reads it as favourable. **This must be decided from the Sanskrit, not
inferred.** If the split is unresolved, the principle must be rejected.

**Draft translation (unreviewed):** "Likewise, the Dasha of the fifth lord joined with the
lord of the tenth (*māna*) is also auspicious."

**Dasha-conditioned?** **Yes, explicitly** (`सुतेश्वरस्यापि दशा`, "the Dasha of the fifth lord,
too"). The conjunction is a natal precondition.

**Proposed formal condition** (timing rule):
```
natal:  jyotish.d1.house.5.lord != jyotish.d1.house.10.lord            (else T6.4)
        AND jyotish.d1.same_sign.<A>.<B> == true                         (X4)
            where {A, B} = {house.5.lord, house.10.lord}, in emitted order
Dasha:  jyotish.timing.vimshottari.mahadasha.lord == jyotish.d1.house.5.lord
        [X1: or ...antardasha.lord == jyotish.d1.house.5.lord]
```
The literal verse names only the 5th lord's Dasha.

**Out of scope here:** the first line of v.83 (5th lord with 9th lord → *rājya-sukha-artha-lābha*).
It is not Career-specific without a decision; it can be raised separately.

**Test cases:**
| ID | Chart / period | Expected |
| --- | --- | --- |
| T6.1 | Aries Lagna (5th lord Sun, 10th lord Saturn); Sun and Saturn both in Aquarius; Sun MD | MATCH |
| T6.2 | Same chart; Saturn MD | NO_MATCH on the literal reading. *Reviewer may extend to the 10th lord's Dasha.* |
| T6.3 | Aries Lagna; Sun in Aquarius, Saturn in Pisces (adjacent signs, however close in degrees); Sun MD | NO_MATCH under the same-sign convention (X4) |
| T6.4 | Cancer Lagna: Mars is both 5th and 10th lord | Not applicable → withhold (UNKNOWN) pending a decision: can a planet be "joined with" itself? |

---

## Considered and deferred (not proposed in this packet)

| Verse | Why deferred |
| --- | --- |
| 80 | Strength modifier. Needs enemy-sign, debilitation and strength models, none of which are admitted. Handled as decision X2, not as a rule. |
| 86 | 4th/5th/9th/10th lords "एकत्र युक्ता" give *rājya*. Unclear whether all four must be together or any subset; the second half extends to planets joined with them. Too ambiguous for this packet. |
| 88 | ताभ्यां ("with those two"): the antecedent is unclear. Already explicitly not admitted. |
| 90–98 | यस्मात्… clauses count houses *from the Dasha lord / other points*. This conflicts with the Lagna-only scope (X3) and needs a benefic/malefic classification that is not admitted. |
| 78, remaining 79 clauses | House lords other than the 10th and 11th; not Career. |
| 84 | 6/8/12 lords joined with the 5th lord; not Career-specific. |
| Planet-specific Dasha results (vv. ~1–75) | Multi-condition (strength, benefic aspect, varga) and evaluative; require models that are not admitted. |

---

## Decision blocks

Fill one block per principle. "Amend" must state the amended condition and wording.

### Part 0
```
0a-1 10th lord in 1st (v.71):        [ ] approve  [ ] reject  [ ] amend: ______________
     leave out the childhood-illness clause?  [ ] yes  [ ] no
     probable reading कर्माधिपतौ confirmed?   [ ] yes  [ ] other: ____________
0a-2 10th lord in 2/3/7 (v.72):      [ ] approve  [ ] reject  [ ] amend: ______________
     मद = 7th house confirmed?               [ ] yes  [ ] other: ____________
0a-3 10th lord in 8th (v.76):        [ ] (a) admit, adverse wording withheld
                                     [ ] (b) hold until X11   [ ] reject  [ ] amend: ______
     reading of line 2 (असदुक्ति / alpāyu): ______________________________
0b   graha terms: mark K / S / A in the graha table; amended terms: ______________
     bhava terms: mark K / S / A in the bhava table; amended terms: ______________
     [uncertain] terms: [ ] exclude all  [ ] keep, with readings: ______________
     fixed bhāva-kāraka list: source to add, if any: ______________________
X18  Dasha lord brings forward the significations of the houses it rules/occupies:
                                     [ ] approve proposed wording  [ ] reject
                                     [ ] amend, exact wording: ________________________
     source verse(s): ______________________
     scope: [ ] Mahadasha lord only  [ ] Mahadasha and Antardasha lords (see X1)
Reviewer: __________  Qualification: __________  Date: ____-__-__
```

### Cross-cutting (X1–X10, X17)
```
X1 MD/AD scope:          ____________________________
X2 v.80 handling:        [ ] a  [ ] b  [ ] c  [ ] d   notes: ______________
   Is (d), exalted/own/debilitated flags only, sufficient?
                         [ ] yes  [ ] no, because: ______________________
   Admit debilitation (v.39) for this purpose? [ ] yes  [ ] no
X3 Lagna-only:           [ ] confirmed  [ ] other: ______________
X4 saṃyuta convention:   [ ] same sign  [ ] orb ____°  [ ] other
X5 modern wording rules: ____________________________
X6 rājya / śubha domain: P1 ____  P3 ____  P5 ____  P6 ____
X7 multiple claims:      [ ] separate, unaggregated  [ ] other: ______
X8 wealth/gain domain:   P1 vitta  [ ] Career [ ] Income [ ] both [ ] neither
                         P2 lābha  [ ] Career [ ] Income [ ] both [ ] neither
                         P4 sampat [ ] Career [ ] Income [ ] both [ ] neither
X9 dispositor of 10th lord: [ ] no, calculated only  [ ] yes, separate cited principle
                         [ ] defer   source/notes: ______________________
X10 display_text, per rule (approve / amend / reject → keep verbatim):
                         v.87 (admitted) [ ] approve [ ] amend [ ] reject  text: ____________
                         P1 [ ] approve [ ] amend [ ] reject  text: ______________________
                         P2 [ ] approve [ ] amend [ ] reject  text: ______________________
                         P3 [ ] approve [ ] amend [ ] reject  text: ______________________
                         P4 [ ] approve [ ] amend [ ] reject  text: ______________________
                         P5 [ ] approve [ ] amend [ ] reject  text: ______________________
                         P6 [ ] approve [ ] amend [ ] reject  text: ______________________
X17 P1/P2 Antardasha scope: [ ] MD lord only  [ ] MD or AD lord
                         [ ] AD only under condition: ______________________  source: ______
v.78 frame governs v.79 (P1, P2 Dasha-conditioned)? [ ] yes  [ ] no → natal
Reviewer: __________  Qualification: __________  Date: ____-__-__
```

### P1 — tenth-lord Dasha (v.79)
```
Decision:  [ ] Approve  [ ] Reject  [ ] Amend
Page images examined (PDF pp., SHA-256 confirmed?): ______________
Authenticated Sanskrit: ____________________________________________
Translation ruling: ________________________________________________
Approved condition: ________________________________________________
Approved user wording: _____________________________________________
Domain: ________   Depends on X: ________
Reasons: ___________________________________________________________
Reviewer: __________  Qualification: __________  Date: ____-__-__
```

### P2 — eleventh-lord Dasha (v.79)
```
Decision:  [ ] Approve  [ ] Reject  [ ] Amend
Page images examined: ______________
Authenticated Sanskrit: ____________________________________________
Translation ruling: ________________________________________________
Approved condition: ________________________________________________
Approved user wording: _____________________________________________
Domain: ________   Depends on X: ________
Reasons: ___________________________________________________________
Reviewer: __________  Qualification: __________  Date: ____-__-__
```

### P3 — ninth lord in tenth (v.89b), promote candidate to production?
```
Decision:  [ ] Approve  [ ] Reject  [ ] Amend
Page images examined: ______________
Authenticated Sanskrit (incl. "मास्ति"/"मानस्थित"): __________________
Translation ruling: ________________________________________________
Approved condition: ________________________________________________
Approved user wording: _____________________________________________
Domain: ________   Depends on X: ________
Reasons: ___________________________________________________________
Reviewer: __________  Qualification: __________  Date: ____-__-__
```

### P4 — fifth lord in tenth (v.89a)
```
Decision:  [ ] Approve  [ ] Reject  [ ] Amend
Page images examined: ______________
Authenticated Sanskrit (incl. "बुद्धीश"/"पञ्चमेश"): __________________
Translation ruling: ________________________________________________
Approved condition: ________________________________________________
Approved user wording: _____________________________________________
Domain: ________   Ruling on T4.3: ________   Depends on X: ________
Reasons: ___________________________________________________________
Reviewer: __________  Qualification: __________  Date: ____-__-__
```

### P5 — fourth/tenth exchange (v.85)
```
Decision:  [ ] Approve  [ ] Reject  [ ] Amend
Page images examined: ______________
Authenticated Sanskrit: ____________________________________________
Exchange required? [ ] both placements  [ ] each separately
Relationship to v.87b: _____________________________________________
Approved condition: ________________________________________________
Approved user wording: _____________________________________________
Domain: ________   Depends on X: ________
Reasons: ___________________________________________________________
Reviewer: __________  Qualification: __________  Date: ____-__-__
```

### P6 — fifth lord joined with tenth lord (v.83b)
```
Decision:  [ ] Approve  [ ] Reject  [ ] Amend
Page images examined: ______________
Verse number confirmed as 83? [ ] yes  [ ] no: ____
Sandhi ruling "दशाशुभा": [ ] दशा शुभा  [ ] दशा अशुभा  [ ] unresolved (→ reject)
Approved condition (whose Dasha?): __________________________________
Ruling on T6.4: ________
Approved user wording: _____________________________________________
Domain: ________   Depends on X: ________
Reasons: ___________________________________________________________
Reviewer: __________  Qualification: __________  Date: ____-__-__
```

---

## Appendix: Part 2 — comparison and promotion

**Optional. Part 0, then Part 1 (P1–P6, X1–X10, X17) come first; please decide those first.**
Nothing in this appendix is approved or active. It was added 2026-11-23 for NEXT-COMPARE-02.

### Why these questions exist

Users ask "Which is better for my career, 2027 or 2028?" JyotishAI now answers with a
**factual side-by-side** (`comparison-view-v1`): for each calendar year, the calculated MD/AD
periods with dates, which reviewed timing indications apply (quoted verbatim), and the
co-reference links. It never ranks the years. It states: "An indication not applying in a
year is not evidence against that year." Promotion questions still return "No approved
Career rule establishes whether or when a promotion will occur."

Every admitted Career rule (natal and timing) is currently treated as **contextual**: no rule
carries a reviewed direction or a reviewed dimension. Ranking stays disabled until the
questions below are decided, together with a conflict convention and expert sign-off
(see `docs/design/NEXT-COMPARE-01.md` §c). The comparison unit is fixed by the product as the
calendar year, with MD/AD boundaries shown inside each year; comparing by Dasha period is
out of scope for now.

| ID | Question | Options | Preparer's note |
| --- | --- | --- | --- |
| X11 | **Polarity per rule.** For v.87, v.140, each of P1–P6, and each admitted natal Career rule (10th lord in 4/10, 5/11, 6/12, 9; 11th lord in 9/10): is the stated result **favourable**, **adverse**, **contextual** (no direction), or **conditional/mixed** (direction depends on a stated condition)? | Per rule: favourable · adverse · contextual · conditional/mixed (state the condition and cite it) | Today every rule is used as contextual. A contextual rule would never contribute to any ranking. "Conditional/mixed" is for results whose direction depends on, e.g., v.80 strength (see X2). |
| X12 | **Dimensions per rule.** Which of these does each rule's result speak to: career opportunity, stability, income, recognition, change, business potential, risk? | Per rule: one or more dimensions · none | Overlaps X6 and X8; X12 is the comparison-facing form. Any future ranking would be per dimension only, never "overall". |
| X14 | **Absence vs adverse.** If a reviewed favourable indication applies in year A and none applies in year B, may that ever support "A is preferable on this dimension"? Or does absence of a match carry no comparative weight? | Absence carries no weight · absence may count only under a cited convention (state it) | The product currently treats absence as carrying no weight, and says so in every one-sided comparison. |
| X15 | **Rājya as promotion context.** May *rājya-pradāyinī* (v.87, P3) and *rājya-lābha* (v.140) be cited in answer to a promotion question, as context only, under fixed non-guarantee wording? | Yes, context only, with approved wording · no | Depends on X5 and X6. Even if yes, the answer would never say a promotion will occur. |

### Decision blocks (Part 2)

#### X11 — polarity per rule
```
Options: F = favourable · A = adverse · C = contextual · M = conditional/mixed (state condition)
v.87 (admitted timing)      [ ] F [ ] A [ ] C [ ] M  condition/cite: ______________
v.140 (admitted timing)     [ ] F [ ] A [ ] C [ ] M  condition/cite: ______________
P1 [ ] F [ ] A [ ] C [ ] M   P2 [ ] F [ ] A [ ] C [ ] M   P3 [ ] F [ ] A [ ] C [ ] M
P4 [ ] F [ ] A [ ] C [ ] M   P5 [ ] F [ ] A [ ] C [ ] M   P6 [ ] F [ ] A [ ] C [ ] M
Natal: 10th lord in 4/10 ____  5/11 ____  6/12 ____  9 ____  11th lord in 9/10 ____
Reasons: ___________________________________________________________
Reviewer: __________  Qualification: __________  Date: ____-__-__
```

#### X12 — dimensions per rule
```
Dimensions: opportunity · stability · income · recognition · change · business · risk · none
v.87: ______________   v.140: ______________
P1: ______  P2: ______  P3: ______  P4: ______  P5: ______  P6: ______
Natal: 10th lord in 4/10 ____  5/11 ____  6/12 ____  9 ____  11th lord in 9/10 ____
Reasons: ___________________________________________________________
Reviewer: __________  Qualification: __________  Date: ____-__-__
```

#### X14 — absence vs adverse
```
[ ] Absence of a match carries no comparative weight
[ ] Absence may count only under this cited convention: ______________________
Source / reasons: __________________________________________________
Reviewer: __________  Qualification: __________  Date: ____-__-__
```

#### X15 — rājya as promotion context
```
[ ] Yes, context only. Approved wording: ____________________________
    Applies to: [ ] v.87  [ ] P3 (v.89b)  [ ] v.140
[ ] No
Depends on X5 / X6 decisions: ______________
Reasons: ___________________________________________________________
Reviewer: __________  Qualification: __________  Date: ____-__-__
```
