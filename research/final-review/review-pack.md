# JyotAI final expert review pack: provisional rules

Corpus `jyotish.provisional@v5` · 22 provisional rules · generated 2026-11-27 by `python -m astrologer.knowledge.review_pack`.

**Nothing in this pack is reviewed.** Every rule below is a provisional rule pending this review. Its author line says who wrote it: "drafted_by: AI agent; adopted_by: project owner (pending)" means an AI agent drafted it and the project owner has not yet adopted it; "project owner, provisional" means the project owner wrote it. In the app a provisional rule is shown only when the user turns on "Show provisional interpretations (beta)", and always with a badge naming the author's confidence, e.g. "Provisional · medium confidence".

## How to decide

For each rule, tick one box:

- **Approve:** the source reading, translation, condition and statement are right as written. The rule is then admitted as REVIEWED under your name.
- **Change:** write the corrected wording or condition. The rule is admitted with your wording.
- **Reject:** the rule is removed from the provisional corpus.

A rule marked **Wording: held** has a located verse whose domain clause is fear-based, accusatory or a health statement. The app shows only the held notice in its place. To approve it, write the wording the app should show (Change).

Ticking a box admits nothing by itself: engineering records your decision and runs the existing admission flow with your review record.

**Provisional significations** (after the rules) are single graha or house terms drafted for one domain, e.g. Marriage or Wealth. Each carries domain tags: an answer shows only the terms tagged for the asked domain. The reviewed signification terms already in the app are tagged Career (reviewed) only, so a Marriage answer shows none of them. Approving a provisional term tags it for its domain as reviewed.

## Summary

| Domain | Provisional rules | Wording held |
| --- | --- | --- |
| Education | 1 | 0 |
| Wealth | 10 | 2 |
| Spirituality | 1 | 0 |
| Marriage | 9 | 8 |
| Property | 1 | 0 |

Domains with no provisional rule yet: General, Career, Business, Children, Travel (residence away from birthplace), Friends, Health.

## Education

### 1. D1 fifth-house lord in the fourth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.5.equals_4.education.v1` (v2)
- **Condition:** `jyotish.d1.house_lord.5.placement_house` = 4 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सुतेशभावफलम् (Sutesha-phala), verse 37; PDF p. 188 (printed p. 190).
- **Confidence (author's):** medium
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review

**Original text**

> सुतेशे मातृभवने चिरं मातृसुखं भवेत् । लक्ष्मीयुक्तः सुबुद्धिश्च सचिवोऽप्यथवा गुरुः ॥ ३७ ॥

**Draft translation**

> When the lord of the fifth is in the fourth (the house of the mother), there is long-lasting happiness from the mother; the native is endowed with prosperity (Lakshmi), of sound intelligence, and a minister/adviser or else a teacher (guru).

**Statement shown in the app (with the provisional badge)**

> With the D1 fifth-house lord in the fourth house, the text associates the placement with intelligence (सुबुद्धि) and with an adviser's or teacher's role (सचिव, गुरु). The same verse also names lasting comfort from the mother and prosperity (लक्ष्मी).

**Interpretive reasoning**

The fifth house is read for intelligence and learning; the verse names सुबुद्धि (sound intelligence) and two roles that rest on learning, सचिव (adviser) and गुरु (teacher). That is why the rule is proposed for Education rather than Career. The mother-comfort and prosperity clauses are kept in the displayed statement, not dropped. The edition's Hindi rendering continues with qualities (knowing muhurta, crooked speech, wealthy) that are not in the Sanskrit of v.37; they are treated as a carry-over and not used.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page image; the PDF text layer drops the first line. The Hindi rendering's second sentence (मुहूर्त को जानने वाला, टेढ़ा बोलने वाला, धनी और बुद्धिमान्) has no counterpart in the printed Sanskrit.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

## Wealth

### 2. D1 second-house lord in the first house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.2.equals_1.wealth.v1` (v2)
- **Condition:** `jyotish.d1.house_lord.2.placement_house` = 1 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ धनेशभावफलम् (Dhanesha-phala), verse 9; PDF p. 183 (printed p. 185); Hindi PDF p. 184.
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other clauses, about children (the text says 'son'), the family and conduct, are not wealth themes; only the wealth clause is shown, and the full translation is kept for the expert review.
- **Source verse:** held in the app — its clause पुत्री names a child's sex or denies children (children wording rule, NEXT-CHILDREN-GUARD-01); the verse is given in full below.

**Original text**

> धनेशे च तनौ पुत्री स्वकुटुम्बस्य कण्टकः । धनवान्निष्ठुरः कामी परकार्येषु तत्परः ॥ ९ ॥

**Draft translation**

> When the lord of the second is in the first (तनु), the native has sons, is a thorn to his own family, wealthy, harsh, lustful and busy with others' affairs. [Hindi: धनेश लग्न में हो तो जातक पुत्रवान्, अपने कुटुम्ब का कंटक, धनी, निष्ठुर, कामी और दूसरे के कार्य में तत्पर होता है।]

**Statement shown in the app (with the provisional badge)**

> With the D1 second-house lord in the first house, the text describes the native as wealthy (धनवान्).

**Interpretive reasoning**

धनेश is the second lord; तनौ is the first house; the edition's Hindi agrees. The wealth clause is धनवान् (wealthy); it is the only clause displayed. The clauses about children (the text says 'son'), स्वकुटुम्बस्य कण्टकः (a thorn to his family), निष्ठुर (harsh), कामी (lustful) and परकार्येषु तत्परः (busy with others' affairs) are not wealth themes; several are judgements of conduct and are not displayed.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The second lord is named धनेश (lord of the house of wealth) and वित्तेश in these verses.
- Only the verse's wealth clause is displayed; its other clauses are named in the reasoning and kept, with the full translation, in the review pack.
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page images (Sanskrit at the foot of PDF p. 183, Hindi at the top of PDF p. 184). The PDF text layer reads धनवातरिष्ठुरः for धनवान्निष्ठुरः.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 3. D1 second-house lord in the tenth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.2.equals_10.wealth.v1` (v2)
- **Condition:** `jyotish.d1.house_lord.2.placement_house` = 10 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ धनेशभावफलम् (Dhanesha-phala), verse 17; PDF p. 185 (printed p. 187).
- **Confidence (author's):** medium
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other clauses, about conduct, wives and children (the text says 'son'), are not wealth themes; only the wealth clause is shown, and the full translation is kept for the expert review.
- **Source verse:** held in the app — its clause सुतहीन names a child's sex or denies children (children wording rule, NEXT-CHILDREN-GUARD-01); the verse is given in full below.

**Original text**

> धनेशो दशमे यस्य कामी मानी च पण्डितः । बहुदारधनैर्युक्तः सुतहीनो प्रजायते ॥ १७ ॥

**Draft translation**

> He whose second lord is in the tenth is lustful, honoured and learned; he is endowed with many wives and wealth, and is without sons. [Hindi: धनेश दशम भाव में हो तो जातक कामी, मानी, पंडित, अनेक स्त्री तथा धन से युक्त और पुत्रहीन होता है।]

**Statement shown in the app (with the provisional badge)**

> With the D1 second-house lord in the tenth house, the text associates the placement with wealth (धन).

**Interpretive reasoning**

दशमे is the tenth house. The wealth clause is in the compound बहुदारधनैर्युक्तः (endowed with many wives and wealth); only 'wealth (धन)' is displayed. Confidence is medium: बहु may qualify both wives and wealth ('much wealth'); the statement claims no amount. कामी, मानी, पण्डित (lustful, honoured, learned), the wives and the clause about children (the text says 'son') are not wealth themes and are not displayed.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The second lord is named धनेश (lord of the house of wealth) and वित्तेश in these verses.
- Only the verse's wealth clause is displayed; its other clauses are named in the reasoning and kept, with the full translation, in the review pack.
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page image; the Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 4. D1 second-house lord in the eleventh house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.2.equals_11.wealth.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.2.placement_house` = 11 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ धनेशभावफलम् (Dhanesha-phala), verse 16; PDF p. 184 (printed p. 186); Hindi PDF p. 185.
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other clauses (childhood illness, later happiness) are not wealth themes; only the wealth clause is shown, and the full translation is kept for the expert review.

**Original text**

> धनेशे नवमे लाभे धनवानुद्यमी पटुः । बाल्ये रोगी सुखी पश्चाद्यावदायुः समाप्यते ॥ १६ ॥

**Draft translation**

> When the lord of the second is in the ninth or the eleventh (लाभ), the native is wealthy, enterprising and skilful; ill in childhood, he is happy afterwards for the rest of his life. [Hindi: धनेश नवम भाव वा लाभभाव में हो तो जातक धनी, उद्यमी, विद्वान् होता है। बाल्य अवस्था में रोगी और पीछे आयु पर्यंत सुखी होता है।]

**Statement shown in the app (with the provisional badge)**

> With the D1 second-house lord in the eleventh house, the text describes the native as wealthy (धनवान्) and enterprising (उद्यमी).

**Interpretive reasoning**

धनेश is the second lord; नवमे लाभे names the ninth and the eleventh; the edition's Hindi agrees. The wealth clause is धनवान् (wealthy), with उद्यमी (enterprising); both are displayed. पटु (skilful; the Hindi has विद्वान्, learned) is a quality of the person, and बाल्ये रोगी (ill in childhood) is a health statement; neither is displayed.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The second lord is named धनेश (lord of the house of wealth) and वित्तेश in these verses.
- Only the verse's wealth clause is displayed; its other clauses are named in the reasoning and kept, with the full translation, in the review pack.

**Transcription notes**

Read from the page images (Sanskrit at the foot of PDF p. 184, Hindi at the top of PDF p. 185). The Hindi renders पटु as विद्वान् (learned).

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 5. D1 second-house lord in the twelfth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.2.equals_12.wealth.v1` (v2)
- **Condition:** `jyotish.d1.house_lord.2.placement_house` = 12 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ धनेशभावफलम् (Dhanesha-phala), verse 18; PDF p. 185 (printed p. 187).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Wording:** held in the app — The verse predicts being without wealth. Owner rule: a verse that predicts poverty or loss is held, not shown; the expert review decides the wording.
- **Source verse:** held in the app — its clause ज्येष्ठपुत्र names a child's sex or denies children (children wording rule, NEXT-CHILDREN-GUARD-01); the verse is given in full below.

**Original text**

> धनेशे व्ययगे ज्ञानी साहसी धनवर्जितः । जीविका नृपगेहाच्च ज्येष्ठपुत्रसुखं न हि ॥ १८ ॥

**Draft translation**

> When the lord of the second is in the twelfth, the native is wise and daring but without wealth; his livelihood comes from the king's house, and there is no happiness from the eldest son. [Hindi: धनेश बारहवें भाव में हो तो जातक ज्ञानी, साहसी, धनहीन, राजगृह से जीविकावाला और ज्येष्ठ पुत्र के सुख से हीन होता है।]

**Statement shown in the app (with the provisional badge)**

> A provisional source verse exists for this placement; its wording is held for the expert review.

**Interpretive reasoning**

व्ययगे is the twelfth house. The wealth clause is धनवर्जितः (without wealth). Owner rule: a verse that predicts poverty is held; nothing is displayed.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The second lord is named धनेश (lord of the house of wealth) and वित्तेश in these verses.
- Only the verse's wealth clause is displayed; its other clauses are named in the reasoning and kept, with the full translation, in the review pack.
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page image; the Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 6. D1 second-house lord in the second house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.2.equals_2.wealth.v1` (v2)
- **Condition:** `jyotish.d1.house_lord.2.placement_house` = 2 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ धनेशभावफलम् (Dhanesha-phala), verse 10; PDF p. 184 (printed p. 186).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other clauses, about pride, wives and children (the text says 'son'), are not wealth themes; only the wealth clause is shown, and the full translation is kept for the expert review.
- **Source verse:** held in the app — its clause पुत्रहीन names a child's sex or denies children (children wording rule, NEXT-CHILDREN-GUARD-01); the verse is given in full below.

**Original text**

> धनेशे धनगे मर्त्यः धनवान् गर्वसंयुतः । भार्याद्वयं त्रयं वापि पुत्रहीनः प्रजायते ॥ १० ॥

**Draft translation**

> When the lord of the second is in the second, the person is wealthy and proud; he has two or three wives and is without sons. [Hindi: धनेश धनभाव में हो जातक धनी, धर्म से युक्त होता है। उसे २ या ३ स्त्रियाँ होती है और पुत्रहीन होता है।]

**Statement shown in the app (with the provisional badge)**

> With the D1 second-house lord in the second house, the text describes the native as wealthy (धनवान्).

**Interpretive reasoning**

धनगे (in the house of wealth) is the second house. The wealth clause is धनवान् (wealthy); it is the only clause displayed. गर्वसंयुत (proud), the number of wives and the clause about children (the text says 'son') are not wealth themes and are not displayed.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The second lord is named धनेश (lord of the house of wealth) and वित्तेश in these verses.
- Only the verse's wealth clause is displayed; its other clauses are named in the reasoning and kept, with the full translation, in the review pack.
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page image (PDF p. 184, printed p. 186). The Hindi renders गर्वसंयुतः (proud) as 'धर्म से युक्त' (righteous); the Sanskrit is followed. The wealth clause is the same in both.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 7. D1 second-house lord in the fifth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.2.equals_5.wealth.v1` (v2)
- **Condition:** `jyotish.d1.house_lord.2.placement_house` = 5 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ धनेशभावफलम् (Dhanesha-phala), verse 12; PDF p. 184 (printed p. 186).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other clauses, about miserliness, sorrow, fame and children (the text says 'son'), are not wealth themes; only the wealth clause is shown, and the full translation is kept for the expert review.
- **Source verse:** held in the app — its clause पुत्रवान names a child's sex or denies children (children wording rule, NEXT-CHILDREN-GUARD-01); the verse is given in full below.

**Original text**

> धनेशे सुतभावस्थे पुत्रतो धनवान् भवेत् । कृपणो दुःखभाग्जातो यशस्वी पुत्रवान् भवेत् ॥ १२ ॥

**Draft translation**

> When the lord of the second is in the fifth, the native becomes wealthy through a son; he is miserly, has his share of sorrow, is famous and has sons. [Hindi: धनेश पाँचवें भाव में हो तो पुत्र से धनी, कृपण, दुःख भोगने वाला, यशस्वी और पुत्रवान् होता है।]

**Statement shown in the app (with the provisional badge)**

> With the D1 second-house lord in the fifth house, the text describes wealth through children (the text says 'son'): पुत्रतो धनवान्.

**Interpretive reasoning**

सुतभाव, the house of children (the text says 'son'), is the fifth house. The wealth clause is पुत्रतो धनवान्, wealthy through children (the text says 'son'); it is the only clause displayed. कृपण (miserly), दुःखभाक् (sharing in sorrow), यशस्वी (famous) and the verse's further clause about children are not wealth themes and are not displayed.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The second lord is named धनेश (lord of the house of wealth) and वित्तेश in these verses.
- Only the verse's wealth clause is displayed; its other clauses are named in the reasoning and kept, with the full translation, in the review pack.
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page image; the Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 8. D1 second-house lord in the sixth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.2.equals_6.wealth.v1` (v2)
- **Condition:** `jyotish.d1.house_lord.2.placement_house` = 6 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ धनेशभावफलम् (Dhanesha-phala), verse 13; PDF p. 184 (printed p. 186).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Wording:** held in the app — The verse predicts a loss of wealth. Owner rule: a verse that predicts poverty or loss is held, not shown; the expert review decides the wording.

**Original text**

> धनेशे शत्रुगे शत्रोर्धनं प्राप्नोति निश्चितम् । शत्रुतो वित्तनाशः स्याज्जंघोर्वोर्भवेच्च रुक् ॥ १३ ॥

**Draft translation**

> When the lord of the second is in the sixth, the native certainly obtains wealth from an enemy; through an enemy there is a loss of wealth, and an ailment of the shanks and thighs. [Hindi: धनेश छठे भाव में हो तो शत्रु से धन प्राप्त करने वाला, पुत्र द्वारा धन नाश वाला और जंघा तथा उरु प्रदेश में रोग युक्त होता है।]

**Statement shown in the app (with the provisional badge)**

> A provisional source verse exists for this placement; its wording is held for the expert review.

**Interpretive reasoning**

शत्रुगे is the sixth house. The verse pairs wealth from an enemy (शत्रोर्धनं प्राप्नोति) with a loss of wealth (वित्तनाशः) and an illness, stated as certain (निश्चितम्). Owner rule: a verse that predicts loss is held; nothing is displayed.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The second lord is named धनेश (lord of the house of wealth) and वित्तेश in these verses.
- Only the verse's wealth clause is displayed; its other clauses are named in the reasoning and kept, with the full translation, in the review pack.
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page image (PDF p. 184). The Sanskrit has शत्रुतो वित्तनाशः (loss of wealth through an enemy); the Hindi reads पुत्र, children (the text says 'son'), in place of the enemy, probably a misprint; the Sanskrit is followed.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 9. D1 second-house lord in the eighth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.2.equals_8.wealth.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.2.placement_house` = 8 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ धनेशभावफलम् (Dhanesha-phala), verse 15; PDF p. 184 (printed p. 186).
- **Confidence (author's):** medium
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other clauses (the wife, an elder brother) are not wealth themes; only the wealth clause is shown, and the full translation is kept for the expert review.

**Original text**

> धनेशे मृत्युगेहस्थे भूमिद्रव्यं लभेद् ध्रुवम् । जायासौख्यं भवेत्स्वल्पं ज्येष्ठभ्रातृसुखं न हि ॥ १५ ॥

**Draft translation**

> When the lord of the second is in the eighth, the native surely gains wealth from the ground (or land and goods); there is little happiness from the wife and no happiness from an elder brother. [Hindi: धनेश आठवें भाव में हो तो जातक को भूमिगत द्रव्य का लाभ, स्त्री का सुख अल्प और ज्येष्ठ भाई का सुख नहीं होता है।]

**Statement shown in the app (with the provisional badge)**

> With the D1 second-house lord in the eighth house, the text describes a gain of wealth connected with land (भूमिद्रव्य).

**Interpretive reasoning**

मृत्युगेह is the eighth house. The wealth clause is भूमिद्रव्यं लभेत् (gains भूमिद्रव्य); it is the only clause displayed, without the verse's ध्रुवम् (surely), which would state a certainty. Confidence is medium: भूमिद्रव्य may be 'land and goods' or 'wealth from the ground'; the edition's Hindi reads भूमिगत द्रव्य (buried wealth). The clauses about the wife and an elder brother are not wealth themes and are not displayed.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The second lord is named धनेश (lord of the house of wealth) and वित्तेश in these verses.
- Only the verse's wealth clause is displayed; its other clauses are named in the reasoning and kept, with the full translation, in the review pack.

**Transcription notes**

Read from the page image; the Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 10. D1 second-house lord in the ninth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.2.equals_9.wealth.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.2.placement_house` = 9 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ धनेशभावफलम् (Dhanesha-phala), verse 16; PDF p. 184 (printed p. 186); Hindi PDF p. 185.
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other clauses (childhood illness, later happiness) are not wealth themes; only the wealth clause is shown, and the full translation is kept for the expert review.

**Original text**

> धनेशे नवमे लाभे धनवानुद्यमी पटुः । बाल्ये रोगी सुखी पश्चाद्यावदायुः समाप्यते ॥ १६ ॥

**Draft translation**

> When the lord of the second is in the ninth or the eleventh (लाभ), the native is wealthy, enterprising and skilful; ill in childhood, he is happy afterwards for the rest of his life. [Hindi: धनेश नवम भाव वा लाभभाव में हो तो जातक धनी, उद्यमी, विद्वान् होता है। बाल्य अवस्था में रोगी और पीछे आयु पर्यंत सुखी होता है।]

**Statement shown in the app (with the provisional badge)**

> With the D1 second-house lord in the ninth house, the text describes the native as wealthy (धनवान्) and enterprising (उद्यमी).

**Interpretive reasoning**

धनेश is the second lord; नवमे लाभे names the ninth and the eleventh; the edition's Hindi agrees. The wealth clause is धनवान् (wealthy), with उद्यमी (enterprising); both are displayed. पटु (skilful; the Hindi has विद्वान्, learned) is a quality of the person, and बाल्ये रोगी (ill in childhood) is a health statement; neither is displayed.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The second lord is named धनेश (lord of the house of wealth) and वित्तेश in these verses.
- Only the verse's wealth clause is displayed; its other clauses are named in the reasoning and kept, with the full translation, in the review pack.

**Transcription notes**

Read from the page images (Sanskrit at the foot of PDF p. 184, Hindi at the top of PDF p. 185). The Hindi renders पटु as विद्वान् (learned).

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 11. D1 seventh-house lord in the fifth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.7.equals_5.wealth.v1` (v3)
- **Condition:** `jyotish.d1.house_lord.7.placement_house` = 5 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala), verse 54; PDF p. 190 (printed p. 192).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — Every Wealth item keeps its full translation in the review pack (NEXT-PROPERTY-01). The statement shown already names each clause of the verse.

**Original text**

> सर्वगुणयुतो मानी भवेत्सर्वधनाधिपः । सदैव हर्षसंयुक्तः सप्तमेशे सुते स्थिते ॥ ५४ ॥

**Draft translation**

> When the lord of the seventh is placed in the fifth, the native is endowed with all virtues, honoured, master of all kinds of wealth, and always joyful.

**Statement shown in the app (with the provisional badge)**

> With the D1 seventh-house lord in the fifth house, the text associates the placement with possessing wealth of every kind (सर्वधनाधिप), with being held in honour (मानी), with many qualities, and with constant cheerfulness.

**Interpretive reasoning**

The central term is सर्वधनाधिप (master of every kind of wealth), so the rule is proposed for Wealth. The other clauses (virtues, honour, joy) are kept in the displayed statement. The verse gives no amount, source or timing of wealth, and the rule claims none.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page image; the PDF text layer reads भानी for मानी. Sanskrit and Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### Located, not drafted (Wealth)

- Second lord in the 3rd or the 4th house: verse 11 (धनेशे सहजे तुर्ये …), PDF p. 184, located. It has no wealth clause (valour, intelligence, conduct; लोभी, greedy, is not wealth), so no Wealth rule is proposed.
- Second lord in the 7th house: verse 14 (धनेशे सप्तमे …), PDF p. 184, located. It has no wealth clause; its clauses are accusatory judgements about the native's family. No Wealth rule is proposed and nothing is shown.
- Eleventh lord in the 1st (v.78), the 2nd or 5th (v.79) and the 9th or 10th (v.83), भावेशफलाध्यायः, अथ लाभेशभावफलम् (Labhesha-phala), PDF p. 194: these placements already have reviewed Wealth rules (jyotish.production.cumulative); no provisional rule duplicates them.
- Eleventh lord in the 3rd or 4th (v.80), the 6th (v.81), the 11th (v.84) and the 12th (v.85), भावेशफलाध्यायः, अथ लाभेशभावफलम् (Labhesha-phala), PDF pp. 194–195, located: no wealth clause (pilgrimage, illness, eloquence, conduct), so no Wealth rule is proposed.
- Eleventh lord in the 7th or 8th: verse 82 (लाभेशे सप्तमे रन्ध्रे भार्या तस्य न जीवति …), भावेशफलाध्यायः, अथ लाभेशभावफलम् (Labhesha-phala), PDF p. 194, located. It has no wealth clause and predicts the loss of the wife; it is not drafted and nothing is shown.

## Spirituality

### 12. D1 fifth-house lord in the seventh house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.5.equals_7.spirituality.v1` (v2)
- **Condition:** `jyotish.d1.house_lord.5.placement_house` = 7 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सुतेशभावफलम् (Sutesha-phala), verse 40; PDF p. 188 (printed p. 190).
- **Confidence (author's):** low
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review

**Original text**

> सुतेशे कामगे मानी सर्वधर्मसमन्वितः । तुंगबष्टिस्तनुस्वामी भक्तियुक्तैकचेतसा ॥ ४० ॥

**Draft translation**

> When the lord of the fifth is in the seventh, the native is proud/honoured, endowed with all dharmas, [tall-nosed (per the Hindi)], and devoted with a single-pointed mind.

**Statement shown in the app (with the provisional badge)**

> With the D1 fifth-house lord in the seventh house, the text associates the placement with adherence to every dharma (सर्वधर्मसमन्वित), single-minded devotion (भक्ति) and being held in honour (मानी).

**Interpretive reasoning**

सर्वधर्मसमन्वित (endowed with every dharma) and भक्तियुक्तैकचेतसा (single-minded devotion) are religious and devotional qualities, so the rule is proposed for Spirituality. The physical description (ऊँचे नाक वाला in the Hindi) is not a spirituality theme and is not displayed. Confidence is low because line 2 is uncertain: the printed तुंगबष्टि looks like a misprint, and तनुस्वामी could be read as a second condition involving the Lagna lord. If it is a condition, this formalization (fifth lord in the seventh only) is incomplete.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Printed तुंगबष्टिस्तनुस्वामी kept as printed (likely misprint; the Hindi reads 'ऊँचे नाक वाला', tall-nosed). The PDF text layer reads तुंगबष्टिस्तनुस्वाधी and भर्तियुक्तैकचेतसा; the page image shows स्वामी and भक्ति.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

## Marriage

### 13. D1 seventh-house lord in the first house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.7.equals_1.marriage.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.7.placement_house` = 1 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala), verse 50; PDF p. 190 (printed p. 192).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Wording:** held in the app — The verse's marriage clause is a judgement about a person's conduct or fidelity; stated to a user it would be accusatory. Wording is for the expert review.

**Original text**

> सप्तमेशे तनौ चास्ते परजायासु लम्पटः । दुष्टो विचक्षणो धीरो वातरुक् स्थीयते हृदि ॥ ५० ॥

**Draft translation**

> When the lord of the seventh is in the first house (and, reading चास्ते as च अस्ते, in the seventh), the native is drawn to the wives of others, wicked, discerning and steady, and a vāta (wind) ailment settles in the heart. [Hindi: सप्तमेश लग्न या सप्तम में हो तो जातक परस्त्री में आसक्त, दुष्ट, पंडित, वातरोगी होता है।]

**Statement shown in the app (with the provisional badge)**

> A provisional source verse exists for this placement; its wording is held for the expert review.

**Interpretive reasoning**

तनौ is the first house. The verse's only marriage clause, परजायासु लम्पटः (drawn to the wives of others), is a judgement about the person's conduct, so the wording is held. दुष्ट, विचक्षण, धीर (character) are not marriage themes; the vāta clause is a health statement. Neither is used.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The verses address a male native (भार्या, जाया, कामिनी: wife); a displayed statement says 'spouse'. Whether a verse applies unchanged to every chart is for the expert review.
- The seventh lord is named by its synonyms: सप्तमेश, द्यूनेश (द्यून = seventh house), जायेश (lord of the house of the wife).

**Transcription notes**

Read from the page image. चास्ते is read as च + अस्ते (अस्त, a name of the seventh house); the edition's Hindi confirms 'लग्न या सप्तम'.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 14. D1 seventh-house lord in the tenth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.7.equals_10.marriage.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.7.placement_house` = 10 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala), verse 53; PDF p. 190 (printed p. 192).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Wording:** held in the app — The verse's marriage clause is a judgement about a person's conduct or fidelity; stated to a user it would be accusatory. Wording is for the expert review.

**Original text**

> द्यूनेशे दशमे तुर्ये नास्य जाया पतिव्रता । धर्मात्मा सत्यसंयुक्तः केवलं दन्तरोगवान् ॥ ५३ ॥

**Draft translation**

> When the lord of the seventh is in the tenth or the fourth, his wife is not pativratā (devoted to her husband); the native is righteous and truthful, and has only a dental ailment. [Hindi: सप्तमेश दशम या चतुर्थ भाव में हो तो जातक की स्त्री पतिव्रता नहीं होती है।]

**Statement shown in the app (with the provisional badge)**

> A provisional source verse exists for this placement; its wording is held for the expert review.

**Interpretive reasoning**

द्यूनेश is the seventh lord; दशमे तुर्ये names the tenth and the fourth. The marriage clause नास्य जाया पतिव्रता is a judgement about the spouse's fidelity, so the wording is held. धर्मात्मा and सत्यसंयुक्त (righteous, truthful) describe the person, not the marriage; the dental clause is a health statement. Neither is used.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The verses address a male native (भार्या, जाया, कामिनी: wife); a displayed statement says 'spouse'. Whether a verse applies unchanged to every chart is for the expert review.
- The seventh lord is named by its synonyms: सप्तमेश, द्यूनेश (द्यून = seventh house), जायेश (lord of the house of the wife).

**Transcription notes**

Read from the page image. The Hindi agrees on the first clause, but its second sentence (सर्वगुणसम्पन्न, मानी, सर्व सम्पत्तिमान्) matches v.54, not the printed Sanskrit of v.53 (धर्मात्मा सत्यसंयुक्तः केवलं दन्तरोगवान्). The Sanskrit is followed; the Hindi second sentence is treated as a carry-over.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 15. D1 seventh-house lord in the twelfth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.7.equals_12.marriage.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.7.placement_house` = 12 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala), verse 56; PDF p. 191 (printed p. 193).
- **Confidence (author's):** medium
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review

**Original text**

> द्वादशस्थे सप्तमेशे दरिद्रः कृपणो महान् । चारुकन्या भवेद्भार्या वस्त्राज्जीवी च निर्धनी ॥ ५६ ॥

**Draft translation**

> When the lord of the seventh is in the twelfth, the native is without means and very miserly; his wife is a beautiful maiden; he lives by cloth and is without wealth. [Hindi: सप्तमेश १२वें भाव में हो तो जातक दरिद्र, अत्यंत कृपण, स्त्री सुंदरी, और वस्त्र से जीविका करने वाला निर्धन होता है।]

**Statement shown in the app (with the provisional badge)**

> With the D1 seventh-house lord in the twelfth house, the text describes the spouse as beautiful (चारु).

**Interpretive reasoning**

The marriage clause is चारुकन्या भवेद्भार्या (the wife is a beautiful maiden); it is the only clause displayed. दरिद्र, कृपण, वस्त्राज्जीवी and निर्धनी (without means, miserly, living by cloth, without wealth) are wealth and livelihood themes, not marriage themes, and are not displayed under Marriage; they are named here so that nothing is left out silently. Confidence is medium: निर्धनी has a feminine-looking form, so the last words may describe the wife rather than the native; the edition's Hindi applies them to the native.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The verses address a male native (भार्या, जाया, कामिनी: wife); a displayed statement says 'spouse'. Whether a verse applies unchanged to every chart is for the expert review.
- The seventh lord is named by its synonyms: सप्तमेश, द्यूनेश (द्यून = seventh house), जायेश (lord of the house of the wife).

**Transcription notes**

Read from the page image (PDF p. 191, printed p. 193). The Sanskrit and the edition's Hindi agree; the Hindi renders चारुकन्या भार्या as 'स्त्री सुंदरी'.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 16. D1 seventh-house lord in the second house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.7.equals_2.marriage.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.7.placement_house` = 2 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala), verse 51; PDF p. 190 (printed p. 192).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Wording:** held in the app — The verse's marriage clause is a judgement about a person's conduct or fidelity; stated to a user it would be accusatory. Wording is for the expert review.

**Original text**

> द्यूनेशे नवमे वित्ते नानास्त्रीभिः समागमः । आरम्भी दीर्घसूत्री च स्त्रीषु चित्तं हि केवलम् ॥ ५१ ॥

**Draft translation**

> When the lord of the seventh is in the ninth or the second (वित्त), there is union with many women; the native starts undertakings, is slow to finish them, and his mind is on women alone. [Hindi: सप्तमेश नवम और दूसरे भाव में हो तो अनेक स्त्रियों में आसक्त, कार्य को आरंभ करने वाला, दीर्घसूत्री और केवल स्त्री में चित्त को लगाने वाला होता है।]

**Statement shown in the app (with the provisional badge)**

> A provisional source verse exists for this placement; its wording is held for the expert review.

**Interpretive reasoning**

द्यूनेश is the seventh lord; नवमे वित्ते names the ninth and the second (वित्त, the house of wealth); the edition's Hindi agrees. The marriage clauses (नानास्त्रीभिः समागमः, स्त्रीषु चित्तं हि केवलम्) are judgements about the person's conduct, so the wording is held. आरम्भी and दीर्घसूत्री (starts undertakings, slow to finish) are not marriage themes and are not used.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The verses address a male native (भार्या, जाया, कामिनी: wife); a displayed statement says 'spouse'. Whether a verse applies unchanged to every chart is for the expert review.
- The seventh lord is named by its synonyms: सप्तमेश, द्यूनेश (द्यून = seventh house), जायेश (lord of the house of the wife).

**Transcription notes**

Read from the page image; the Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 17. D1 seventh-house lord in the fourth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.7.equals_4.marriage.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.7.placement_house` = 4 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala), verse 53; PDF p. 190 (printed p. 192).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Wording:** held in the app — The verse's marriage clause is a judgement about a person's conduct or fidelity; stated to a user it would be accusatory. Wording is for the expert review.

**Original text**

> द्यूनेशे दशमे तुर्ये नास्य जाया पतिव्रता । धर्मात्मा सत्यसंयुक्तः केवलं दन्तरोगवान् ॥ ५३ ॥

**Draft translation**

> When the lord of the seventh is in the tenth or the fourth, his wife is not pativratā (devoted to her husband); the native is righteous and truthful, and has only a dental ailment. [Hindi: सप्तमेश दशम या चतुर्थ भाव में हो तो जातक की स्त्री पतिव्रता नहीं होती है।]

**Statement shown in the app (with the provisional badge)**

> A provisional source verse exists for this placement; its wording is held for the expert review.

**Interpretive reasoning**

द्यूनेश is the seventh lord; दशमे तुर्ये names the tenth and the fourth. The marriage clause नास्य जाया पतिव्रता is a judgement about the spouse's fidelity, so the wording is held. धर्मात्मा and सत्यसंयुक्त (righteous, truthful) describe the person, not the marriage; the dental clause is a health statement. Neither is used.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The verses address a male native (भार्या, जाया, कामिनी: wife); a displayed statement says 'spouse'. Whether a verse applies unchanged to every chart is for the expert review.
- The seventh lord is named by its synonyms: सप्तमेश, द्यूनेश (द्यून = seventh house), जायेश (lord of the house of the wife).

**Transcription notes**

Read from the page image. The Hindi agrees on the first clause, but its second sentence (सर्वगुणसम्पन्न, मानी, सर्व सम्पत्तिमान्) matches v.54, not the printed Sanskrit of v.53 (धर्मात्मा सत्यसंयुक्तः केवलं दन्तरोगवान्). The Sanskrit is followed; the Hindi second sentence is treated as a carry-over.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 18. D1 seventh-house lord in the sixth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.7.equals_6.marriage.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.7.placement_house` = 6 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala), verse 55; PDF p. 190 (printed p. 192).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Wording:** held in the app — The verse's marriage clause is a health statement about the spouse and the verse is phrased in absolute terms. Health is a high-stakes topic; wording is for the expert review.

**Original text**

> जायेशे चाष्टमे षष्ठे रोगिणी कामिनी लभेत् । क्रोधयुक्तो भवेद्वापि न सुखं लभते क्वचित् ॥ ५५ ॥

**Draft translation**

> When the lord of the seventh is in the eighth or the sixth, the native obtains a sickly wife; he is given to anger and finds no happiness anywhere. [Hindi: सप्तमेश ६ या ८ भाव में हो तो जातक की स्त्री रोगिणी होती है। जातक क्रोधी होता है और सुखी नहीं रहता है।]

**Statement shown in the app (with the provisional badge)**

> A provisional source verse exists for this placement; its wording is held for the expert review.

**Interpretive reasoning**

जायेश (lord of the house of the wife) is the seventh lord; अष्टमे षष्ठे names the eighth and the sixth; the edition's Hindi agrees. The marriage clause रोगिणी कामिनी लभेत् is a health statement about the spouse, and the rest of the verse is phrased in absolute terms (न सुखं लभते क्वचित्). The wording is held.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The verses address a male native (भार्या, जाया, कामिनी: wife); a displayed statement says 'spouse'. Whether a verse applies unchanged to every chart is for the expert review.
- The seventh lord is named by its synonyms: सप्तमेश, द्यूनेश (द्यून = seventh house), जायेश (lord of the house of the wife).

**Transcription notes**

Read from the page image; the Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 19. D1 seventh-house lord in the seventh house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.7.equals_7.marriage.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.7.placement_house` = 7 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala), verse 50; PDF p. 190 (printed p. 192).
- **Confidence (author's):** medium
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Wording:** held in the app — The verse's marriage clause is a judgement about a person's conduct or fidelity; stated to a user it would be accusatory. Wording is for the expert review.

**Original text**

> सप्तमेशे तनौ चास्ते परजायासु लम्पटः । दुष्टो विचक्षणो धीरो वातरुक् स्थीयते हृदि ॥ ५० ॥

**Draft translation**

> When the lord of the seventh is in the first house (and, reading चास्ते as च अस्ते, in the seventh), the native is drawn to the wives of others, wicked, discerning and steady, and a vāta (wind) ailment settles in the heart. [Hindi: सप्तमेश लग्न या सप्तम में हो तो जातक परस्त्री में आसक्त, दुष्ट, पंडित, वातरोगी होता है।]

**Statement shown in the app (with the provisional badge)**

> A provisional source verse exists for this placement; its wording is held for the expert review.

**Interpretive reasoning**

The seventh house is read from चास्ते as च अस्ते (अस्त, a name of the seventh house); the edition's Hindi says 'लग्न या सप्तम'. Confidence is medium because the seventh-house condition rests on that reading. The verse's only marriage clause, परजायासु लम्पटः, is a judgement about the person's conduct, so the wording is held. The character and vāta clauses are not used.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The verses address a male native (भार्या, जाया, कामिनी: wife); a displayed statement says 'spouse'. Whether a verse applies unchanged to every chart is for the expert review.
- The seventh lord is named by its synonyms: सप्तमेश, द्यूनेश (द्यून = seventh house), जायेश (lord of the house of the wife).

**Transcription notes**

Read from the page image. चास्ते is read as च + अस्ते (अस्त, a name of the seventh house); the edition's Hindi confirms 'लग्न या सप्तम'.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 20. D1 seventh-house lord in the eighth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.7.equals_8.marriage.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.7.placement_house` = 8 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala), verse 55; PDF p. 190 (printed p. 192).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Wording:** held in the app — The verse's marriage clause is a health statement about the spouse and the verse is phrased in absolute terms. Health is a high-stakes topic; wording is for the expert review.

**Original text**

> जायेशे चाष्टमे षष्ठे रोगिणी कामिनी लभेत् । क्रोधयुक्तो भवेद्वापि न सुखं लभते क्वचित् ॥ ५५ ॥

**Draft translation**

> When the lord of the seventh is in the eighth or the sixth, the native obtains a sickly wife; he is given to anger and finds no happiness anywhere. [Hindi: सप्तमेश ६ या ८ भाव में हो तो जातक की स्त्री रोगिणी होती है। जातक क्रोधी होता है और सुखी नहीं रहता है।]

**Statement shown in the app (with the provisional badge)**

> A provisional source verse exists for this placement; its wording is held for the expert review.

**Interpretive reasoning**

जायेश (lord of the house of the wife) is the seventh lord; अष्टमे षष्ठे names the eighth and the sixth; the edition's Hindi agrees. The marriage clause रोगिणी कामिनी लभेत् is a health statement about the spouse, and the rest of the verse is phrased in absolute terms (न सुखं लभते क्वचित्). The wording is held.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The verses address a male native (भार्या, जाया, कामिनी: wife); a displayed statement says 'spouse'. Whether a verse applies unchanged to every chart is for the expert review.
- The seventh lord is named by its synonyms: सप्तमेश, द्यूनेश (द्यून = seventh house), जायेश (lord of the house of the wife).

**Transcription notes**

Read from the page image; the Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### 21. D1 seventh-house lord in the ninth house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.7.equals_9.marriage.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.7.placement_house` = 9 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala), verse 51; PDF p. 190 (printed p. 192).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Wording:** held in the app — The verse's marriage clause is a judgement about a person's conduct or fidelity; stated to a user it would be accusatory. Wording is for the expert review.

**Original text**

> द्यूनेशे नवमे वित्ते नानास्त्रीभिः समागमः । आरम्भी दीर्घसूत्री च स्त्रीषु चित्तं हि केवलम् ॥ ५१ ॥

**Draft translation**

> When the lord of the seventh is in the ninth or the second (वित्त), there is union with many women; the native starts undertakings, is slow to finish them, and his mind is on women alone. [Hindi: सप्तमेश नवम और दूसरे भाव में हो तो अनेक स्त्रियों में आसक्त, कार्य को आरंभ करने वाला, दीर्घसूत्री और केवल स्त्री में चित्त को लगाने वाला होता है।]

**Statement shown in the app (with the provisional badge)**

> A provisional source verse exists for this placement; its wording is held for the expert review.

**Interpretive reasoning**

द्यूनेश is the seventh lord; नवमे वित्ते names the ninth and the second (वित्त, the house of wealth); the edition's Hindi agrees. The marriage clauses (नानास्त्रीभिः समागमः, स्त्रीषु चित्तं हि केवलम्) are judgements about the person's conduct, so the wording is held. आरम्भी and दीर्घसूत्री (starts undertakings, slow to finish) are not marriage themes and are not used.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The verses address a male native (भार्या, जाया, कामिनी: wife); a displayed statement says 'spouse'. Whether a verse applies unchanged to every chart is for the expert review.
- The seventh lord is named by its synonyms: सप्तमेश, द्यूनेश (द्यून = seventh house), जायेश (lord of the house of the wife).

**Transcription notes**

Read from the page image; the Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### Located, not drafted (Marriage)

- Seventh lord in the 3rd or the 11th house: verse 52 (द्यूनेशे सहजे लाभे …), PDF p. 190 (printed p. 192), located. Its clauses concern children only; it has no marriage clause, so no Marriage rule is proposed.
- Seventh lord in the 5th house: verse 54 (सर्वगुणयुतो मानी …), PDF p. 190 (printed p. 192), located. It has no marriage clause (virtues, honour, wealth, joy); it is already the provisional Wealth rule, so no Marriage rule is proposed.

## Property

### 22. D1 fourth-house lord in the second house (provisional)

- **Rule id:** `provisional.bphs.d1.house_lord.4.equals_2.property.v1` (v1)
- **Condition:** `jyotish.d1.house_lord.4.placement_house` = 2 (D1/Rashi, static, contextual; no timing, polarity or weight)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** भावेशफलाध्यायः, अथ सुखेशभावफलम् (Sukhesha-phala), verse 27; PDF p. 186 (printed p. 188).
- **Confidence (author's):** low
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other clauses (honour, daring, trickery, the family, pleasures) are not property themes; only the property clause is shown, and the full translation is kept for the expert review.

**Original text**

> सर्वसम्पद्युतो मानी साहसी कुहकान्वितः । कुटुम्बसंयुतो भोगी सुखेशे च धनस्थिते ॥ २७ ॥

**Draft translation**

> When the lord of the fourth is in the second (धन), the native is endowed with all kinds of possessions, honoured, daring, given to trickery, has his family with him and enjoys pleasures. [Hindi: सुखेश धनभाव में हो तो जातक सभी सम्पत्तियों से युक्त, मानी, साहसी, इन्द्रजाल करने वाला, कुटुम्ब से युक्त और भोगी होता है।]

**Statement shown in the app (with the provisional badge)**

> With the D1 fourth-house lord in the second house, the text describes the native as endowed with all kinds of possessions (सर्वसम्पद्युत).

**Interpretive reasoning**

सुखेश is the fourth lord; धनस्थिते is the second house; the edition's Hindi agrees. The only clause that touches property is सर्वसम्पद्युत (endowed with all सम्पद्), which the Hindi renders 'सभी सम्पत्तियों से युक्त' (with all properties). सम्पद् also means prosperity or riches, and the verse names no land, house or vehicle, so confidence is low; the expert review decides whether it is a Property or a Wealth clause. मानी (honoured), साहसी (daring), कुहकान्वित (given to trickery; Hindi: इन्द्रजाल करने वाला), कुटुम्बसंयुत (with his family) and भोगी (enjoying pleasures) are not property themes; one is a judgement of conduct. None of them is displayed.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Classical seven-planet sign lordship; the house lord's placement is a deterministic D1 fact (jyotish-derived-facts-v1).
- Static, contextual natal evidence only: no polarity, weight, timing or prediction.
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The fourth lord is named सुखेश (lord of the house of happiness) and तुर्येश in these verses.
- Drafted only where the verse has a property clause (land, a house, vehicles or possessions); only that clause is displayed, and the full translation stays in the review pack.

**Transcription notes**

Read from the page image (PDF p. 186, printed p. 188). The PDF text layer agrees. The Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### Located, not drafted (Property)

- Fourth lord in the 1st house: verse 26 (सुखेशे लग्नगे …), PDF p. 186, located (verse 32 also names लग्ने). No property clause (affection of father and son, enmity from the father's side, fame by the father's name); no Property rule is proposed.
- Fourth lord in the 3rd or 11th house: verse 28 (सुखेशे सहजे लाभे …), PDF p. 186, located. स्वभुजार्जितवित्तवान् (wealth earned by one's own effort) is a wealth clause, not a property clause; नित्यरोगी (always ill) is a health statement. No Property rule is proposed.
- Fourth lord in the 4th house: verse 29 (तुर्येशे तुर्यगे …), PDF pp. 186–187, located. सर्वधनाधिप (master of all wealth) and धनाढ्य (rich) are wealth (धन) clauses; the edition's Hindi renders सर्वधनाधिप as 'सभी प्रकार की संपत्ति'. No Property rule is proposed; the question is in the reviewer questions.
- Fourth lord in the 5th or 9th house: verse 30 (तुर्येशे पञ्चमे भाग्ये …), PDF p. 187, located. No property clause (happiness, popularity, devotion, honour, wealth earned by effort); no Property rule is proposed.
- Fourth lord in the 6th house: verse 31 (सुखेशे शत्रुगेहस्थे …), PDF p. 187, located. No property clause; its clauses are accusatory judgements (anger, theft, sorcery). Not drafted and nothing is shown.
- Fourth lord in the 7th house: verse 32 (सुखेशे सप्तमे लग्ने …), PDF p. 187, located. No property clause (learning, giving up the father's wealth, silence in an assembly); no Property rule is proposed.
- Fourth lord in the 8th or 12th house: verse 33 (सुखेशे व्ययरन्ध्रस्थे …), PDF p. 187, located. No property clause; it predicts a lack of happiness and makes accusatory statements about the native's birth. Not drafted and nothing is shown.
- Fourth lord in the 10th house: verse 34 (सुखेशे कर्मगेहस्थे …), PDF p. 187, located. No property clause (royal honour, alchemy, delight, happiness); no Property rule is proposed.
- 4th-house terms that are not property terms (द्वादशभावविचाराध्यायः v.4, PDF p. 147): बन्धु (relatives) and मातृसौख्य (the mother's happiness) belong to a relatives, mother or happiness domain, which JyotAI does not have, so they are neither tagged Property nor drafted; निधि (treasure; Hindi: गड़े धन, buried wealth) is a wealth matter, not land, a house or a vehicle, and is not drafted.

## Provisional significations: Wealth

Corpus `jyotish.provisional.signification@v4` · 4 terms.

### S1. 2nd house: धन (wealth)

- **Term id:** `provisional.signification.bhava.2.dhana` (v1)
- **Subject:** bhava 2
- **Domain tags:** Wealth (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** द्वादशभावविचाराध्यायः (अथ द्वादशभावेषु विचार्यत्वमाह), verse 2; PDF p. 146 (printed p. 148).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not wealth terms (they include death and enemies); the full translation is kept for the expert review and is not shown in a wealth answer.

**Original text**

> धनं धान्यं कुटुम्बं च मृत्युजालममित्रकम् । धातुरत्नादिकं सर्वं धनस्थानाद्विचारयेत् ॥ २ ॥

**Draft translation**

> From the house of wealth (the second), one should consider wealth, grain, family, the net of death, enemies, and metals, gems and the like. [Hindi (PDF p. 147): दूसरे भाव में धन, धान्य, कुटुंब, मृत्यु, शत्रु का और धातु, रत्न आदि का विचार करना चाहिए।]

**Statement shown in the app (with the provisional badge)**

> The text lists wealth (धन) first among the matters judged from the 2nd house, which it calls the house of wealth (धनस्थान).

**Interpretive reasoning**

The verse opens with धनं (wealth) and closes with धनस्थानाद्विचारयेत् (judge from the house of wealth), so the second house's wealth term is explicit. Only धन is drafted. धान्य (grain) and धातुरत्नादि (metals, gems and the like) are possessions the expert review may add; कुटुम्ब is drafted separately (low). मृत्युजाल (the net of death) and अमित्र (enemies) are not wealth terms and are not drafted. The Career-tagged signification term of the second house is also धन ('wealth'), tagged for Career only; this provisional Wealth record does not change it.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, amount or prediction. Domain tag: Wealth (provisional).
- Drafted only where the verse names wealth or gain (धन, लाभ); a Career-tagged term of the same word stays Career only until a reviewer tags it.

**Transcription notes**

Read from the page image (Sanskrit at the foot of PDF p. 146, Hindi at the top of PDF p. 147). The PDF text layer agrees. The Sanskrit and the Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### S2. 2nd house: कुटुम्ब (family)

- **Term id:** `provisional.signification.bhava.2.kutumba` (v2)
- **Subject:** bhava 2
- **Domain tags:** Wealth (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** द्वादशभावविचाराध्यायः (अथ द्वादशभावेषु विचार्यत्वमाह), verse 2; PDF p. 146 (printed p. 148).
- **Confidence (author's):** low
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not wealth terms (they include death and enemies); the full translation is kept for the expert review and is not shown in a wealth answer.

**Original text**

> धनं धान्यं कुटुम्बं च मृत्युजालममित्रकम् । धातुरत्नादिकं सर्वं धनस्थानाद्विचारयेत् ॥ २ ॥

**Draft translation**

> From the house of wealth (the second), one should consider wealth, grain, family, the net of death, enemies, and metals, gems and the like. [Hindi (PDF p. 147): दूसरे भाव में धन, धान्य, कुटुंब, मृत्यु, शत्रु का और धातु, रत्न आदि का विचार करना चाहिए।]

**Statement shown in the app (with the provisional badge)**

> The text lists family (कुटुम्ब) among the matters judged from the 2nd house, which it calls the house of wealth (धनस्थान).

**Interpretive reasoning**

Owner instruction (NEXT-WEALTH-01): कुटुम्ब is no longer drafted for Marriage; the verse names no spouse. It is tagged Wealth (provisional) because the verse judges it from धनस्थान, the house of wealth, next to धन and धान्य. कुटुम्ब (family, household) is not itself wealth, so confidence stays low; the expert review decides whether it belongs to Wealth, to another domain, or to none. The kāraka chapter v.35 (PDF p. 108) calls the second house दारकारक (kāraka of the wife) while v.36 on the same page takes दारा from the seventh house; that conflict is a question for the reviewer in the review pack and is not used here.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, amount or prediction. Domain tag: Wealth (provisional).
- Drafted only where the verse names wealth or gain (धन, लाभ); a Career-tagged term of the same word stays Career only until a reviewer tags it.

**Transcription notes**

Read from the page image (Sanskrit at the foot of PDF p. 146, Hindi at the top of PDF p. 147). The PDF text layer agrees. The Sanskrit and the Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### S3. 11th house: लाभ (gain)

- **Term id:** `provisional.signification.bhava.11.labha` (v2)
- **Subject:** bhava 11
- **Domain tags:** Wealth (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** द्वादशभावविचाराध्यायः (अथ द्वादशभावेषु विचार्यत्वमाह), verse 11; PDF p. 148 (printed p. 150).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not wealth terms (they include children (the text says 'son'), the wife and livestock); the full translation is kept for the expert review and is not shown in a wealth answer.

**Original text**

> नानावस्तुभवस्यापि पुत्रजायादिकस्य च । लाभवृद्धिपशूनां च भवस्थानाद्विचारयेत् ॥ ११ ॥

**Draft translation**

> From the house of gains (भव, the eleventh), one should consider the acquisition of various things, sons, wife and the like, gain, and the increase of livestock. [Hindi: एकादश भाव से अनेक वस्तुओं की प्राप्ति, पुत्र, स्त्री, पशुओं की वृद्धि तथा लाभ आदि का विचार करना चाहिए।]

**Statement shown in the app (with the provisional badge)**

> The text lists gain (लाभ) among the matters judged from the 11th house.

**Interpretive reasoning**

The verse names लाभ (gain) among the eleventh house's matters; नानावस्तुभव (the acquisition of various things) points the same way and is left for the expert review. Only लाभ is drafted. वृद्धि is read with पशूनां (the increase of livestock), as the edition's Hindi does, and is not drafted. पुत्र and जाया (children (the text says 'son'); the wife) are Children and Marriage matters, not wealth terms. The Career-tagged terms of the eleventh house (लाभ 'gain', वृद्धि 'increase') stay Career only.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, amount or prediction. Domain tag: Wealth (provisional).
- Drafted only where the verse names wealth or gain (धन, लाभ); a Career-tagged term of the same word stays Career only until a reviewer tags it.
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page image (PDF p. 148, printed p. 150). The PDF text layer agrees except for the verse number (९९ for ११). The Sanskrit and the Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### S4. Jupiter: धन (wealth (kāraka))

- **Term id:** `provisional.signification.graha.jupiter.dhana` (v2)
- **Subject:** graha jupiter
- **Domain tags:** Wealth (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह, verse 5; PDF p. 109 (printed p. 111). Corroboration: अथ भावकारकमाह v.37, PDF p. 108 (printed p. 110).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not wealth terms (they include one's own work, children (the text says 'son') and friends); the full translation is kept for the expert review and is not shown in a wealth answer.

**Original text**

> स्वकर्मयजनदेवब्राह्मणधनगृहकाञ्चनवस्त्रपुत्रमित्रान्दोलनादिकारको गुरुः ॥ ५ ॥ | v.37: सूर्यो गुरुः कुजः सोमो गुरुर्भौमः सितः शनिः । गुरुश्चन्द्रसुतो जीवो मन्दश्च भावकारकः ॥ ३७ ॥

**Draft translation**

> v.5: Guru (Jupiter) is the kāraka of one's own work, sacrifice, the gods, brāhmaṇas, wealth (धन), house, gold, cloth, sons, friends, swings and the like. [Hindi: अपने कार्य, यज्ञ, देवता, ब्राह्मण, धन, गृह, सुवर्ण, वस्त्र, पुत्र, मित्र, आंदोलन आदि के कारक गुरु हैं।] v.37: the kārakas of the houses from the Lagna are, in order, Sun, Jupiter (the second), Mars, Moon (Hindi: Mercury), Jupiter, Mars, Venus, Saturn, Jupiter, Mercury, Jupiter (the eleventh), Saturn.

**Statement shown in the app (with the provisional badge)**

> The text names Jupiter a kāraka (significator) of wealth (धन).

**Interpretive reasoning**

Jupiter's own kāraka list (v.5) names धन (wealth) and काञ्चन (gold); the bhāva-kāraka list (v.37) makes Jupiter the kāraka of the second and the eleventh houses, the two Wealth houses. Only धन is drafted. स्वकर्म (one's own work) is closer to Career, पुत्र (children (the text says 'son')) to Children; they are not drafted for Wealth. The Career-tagged Career terms of Jupiter (ज्ञानम्, सचिवः) stay Career only.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, amount or prediction. Domain tag: Wealth (provisional).
- Drafted only where the verse names wealth or gain (धन, लाभ); a Career-tagged term of the same word stays Career only until a reviewer tags it.
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page images. The PDF text layer breaks v.5 at काञ्चन (a line break, no letter lost) and garbles v.37 (सूयां गृरुः for सूर्यो गुरुः). In v.37 the Sanskrit's fourth kāraka is सोमः (Moon) while the Hindi gives बुध (Mercury); the second and eleventh (गुरुः) agree in both.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

## Provisional significations: Marriage

Corpus `jyotish.provisional.signification@v4` · 2 terms.

### S1. 7th house: जाया (spouse)

- **Term id:** `provisional.signification.bhava.7.jaya` (v1)
- **Subject:** bhava 7
- **Domain tags:** Marriage (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** द्वादशभावविचाराध्यायः (अथ द्वादशभावेषु विचार्यत्वमाह), verse 7; PDF p. 147 (printed p. 149).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other clauses include death, which is not a marriage term; the full translation is kept for the expert review and is not shown in a marriage answer.

**Original text**

> जायामध्वप्रयाणं च व्यापारं हतवीक्षणम् । मरणं च स्वदेहस्य जायाभावान्निरीक्षयेत् ॥ ७ ॥

**Draft translation**

> From the house of the wife (the seventh), one should examine the wife, journeys on the road, trade, lost things, and the death of one's own body. [Hindi: सप्तम भाव से स्त्री, मार्ग, यात्रा, व्यापार, नष्ट वस्तु और मृत्यु का विचार करना चाहिए।]

**Statement shown in the app (with the provisional badge)**

> The text lists the spouse (जाया) among the matters judged from the 7th house.

**Interpretive reasoning**

The verse names जाया (wife) first among the seventh house's matters and calls the seventh 'the house of the wife' (जायाभाव). Only that term is drafted for Marriage. व्यापार (trade) is already a Career signification term and stays Career only; journeys, lost things and death are not marriage terms and are not drafted. 'Marriage' and 'partnership' are not in the verse and are not used. Corroboration: the kāraka chapter v.36 (PDF p. 108) gives दारा (wife) from the seventh house.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The verses address a male native (जाया, कलत्र, स्त्री: wife); the display says 'spouse'. Whether the term applies unchanged to every chart is for the expert review.
- A signification term names a theme only: no polarity, weight, timing or prediction. Domain tag: Marriage (provisional).

**Transcription notes**

Read from the page image. The PDF text layer agrees on the first line and reads जायाभावात्निरीक्षयेत् for the printed जायाभावान्निरीक्षयेत्. The Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### S2. Venus: कलत्र (spouse (kāraka))

- **Term id:** `provisional.signification.graha.venus.kalatra` (v2)
- **Subject:** graha venus
- **Domain tags:** Marriage (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह, verse 6; PDF p. 109 (printed p. 111). Corroboration: अथ भावकारकमाह v.37, PDF p. 108 (printed p. 110); अथ स्थिरकारकमाह v.33, PDF p. 107 (printed p. 109).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review

**Original text**

> कलत्रकार्मुकसुखगीतशास्त्रकाव्यपुष्पसुकुमारयौवनाभरणरजतयानस्वर्गलोकमौक्तिकविभवकवितारसादिकारको भृगुः ॥ ६ ॥ | v.37: सूर्यो गुरुः कुजः सोमो गुरुर्भौमः सितः शनिः । गुरुश्चन्द्रसुतो जीवो मन्दश्च भावकारकः ॥ ३७ ॥ | v.33: देवेज्यात्पञ्चमे पुत्रो दैत्येज्याद्द्यूनभे स्त्रियः । मन्दादष्टमतो मृत्युस्तातादीनां विचिन्तयेत् ॥ ३३ ॥

**Draft translation**

> v.6: Bhṛgu (Venus) is the kāraka of the wife (कलत्र), the bow, happiness, music, poetry, flowers, youth, ornaments, silver, vehicles, … [Hindi: स्त्री, धनुष, सुख, गीतशास्त्र … के कारक शुक्र हैं।] v.37: the kārakas of the houses from the Lagna are, in order, Sun, Jupiter, Mars, Moon (Hindi: Mercury), Jupiter, Mars, Venus (सितः, the seventh), Saturn, Jupiter, Mercury, Jupiter, Saturn. v.33: from Venus (दैत्येज्य), the seventh house is examined for the wife.

**Statement shown in the app (with the provisional badge)**

> The text names Venus the kāraka (significator) of the spouse (कलत्र).

**Interpretive reasoning**

Three verses agree that Venus signifies the wife: it is named कलत्रकारक in its own kāraka list (v.6), it is the bhāva-kāraka of the seventh house (v.37), and the seventh from Venus is examined for the wife (v.33). Only कलत्र is drafted for Marriage; the other Venus terms of v.6 are not marriage terms. The Career signification term of Venus (सचिवः, 'adviser or counsellor') stays Career only.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- The verses address a male native (जाया, कलत्र, स्त्री: wife); the display says 'spouse'. Whether the term applies unchanged to every chart is for the expert review.
- A signification term names a theme only: no polarity, weight, timing or prediction. Domain tag: Marriage (provisional).
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page images. The PDF text layer garbles v.6 (कामुक for कार्मुक, भगः for भृगुः) and v.37 (सूयां गृरुः for सूर्यो गुरुः). In v.37 the Sanskrit's fourth kāraka is सोमः (Moon) while the Hindi gives बुध (Mercury); this does not affect the seventh (सितः, Venus), on which both agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

## Provisional significations: Property

Corpus `jyotish.provisional.signification@v4` · 8 terms.

### S1. 4th house: गृह (house or home)

- **Term id:** `provisional.signification.bhava.4.griha` (v1)
- **Subject:** bhava 4
- **Domain tags:** Property (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** द्वादशभावविचाराध्यायः (अथ द्वादशभावेषु विचार्यत्वमाह), verse 4; PDF p. 147 (printed p. 149).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not property terms (they include relatives, the mother's happiness and treasure); the full translation is kept for the expert review and is not shown in a property answer.

**Original text**

> वाहनस्याथ बन्धूनां मातृसौख्यादिकानपि । निधिक्षेत्रं गृहं चापि पातालाच्च निरीक्षयेत् ॥ ४ ॥

**Draft translation**

> From the fourth house (पाताल), one should examine vehicles, relatives, the happiness of the mother and the like, treasure, fields (land) and the house. [Hindi: चौथे भाव से वाहन (सवारी) का, बंधुओं का, मातृसुख का, निधि (गड़े धन) का, क्षेत्र (खेत) तथा गृह का विचार करना चाहिए।]

**Statement shown in the app (with the provisional badge)**

> The text lists the house or home (गृह) among the matters judged from the 4th house.

**Interpretive reasoning**

The verse names गृह (house, home) among the fourth house's matters, and the edition's Hindi keeps गृह. Only that term is drafted here. बन्धु (relatives) and मातृसौख्य (the mother's happiness) are not property terms and are not tagged Property (JyotAI has no relatives, mother or happiness domain); निधि (treasure; Hindi: buried wealth) is a wealth matter and is not drafted.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, price or prediction. Domain tag: Property (provisional).
- Drafted only where the verse names land, a house or vehicles (भूमि, क्षेत्र, गृह, सद्म, वाहन, यान); the verse's other matters are not drafted for Property.

**Transcription notes**

Read from the page image (PDF p. 147, printed p. 149). The PDF text layer agrees. The Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### S2. 4th house: क्षेत्र (fields or land)

- **Term id:** `provisional.signification.bhava.4.kshetra` (v1)
- **Subject:** bhava 4
- **Domain tags:** Property (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** द्वादशभावविचाराध्यायः (अथ द्वादशभावेषु विचार्यत्वमाह), verse 4; PDF p. 147 (printed p. 149).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not property terms (they include relatives, the mother's happiness and treasure); the full translation is kept for the expert review and is not shown in a property answer.

**Original text**

> वाहनस्याथ बन्धूनां मातृसौख्यादिकानपि । निधिक्षेत्रं गृहं चापि पातालाच्च निरीक्षयेत् ॥ ४ ॥

**Draft translation**

> From the fourth house (पाताल), one should examine vehicles, relatives, the happiness of the mother and the like, treasure, fields (land) and the house. [Hindi: चौथे भाव से वाहन (सवारी) का, बंधुओं का, मातृसुख का, निधि (गड़े धन) का, क्षेत्र (खेत) तथा गृह का विचार करना चाहिए।]

**Statement shown in the app (with the provisional badge)**

> The text lists fields or land (क्षेत्र) among the matters judged from the 4th house.

**Interpretive reasoning**

The verse names क्षेत्र (in the compound निधिक्षेत्रं), which the edition's Hindi glosses as खेत (field, farmland); 'fields or land' is displayed. बन्धु (relatives) and मातृसौख्य (the mother's happiness) are not property terms and are not tagged Property (JyotAI has no relatives, mother or happiness domain); निधि (treasure; Hindi: buried wealth) is a wealth matter and is not drafted.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, price or prediction. Domain tag: Property (provisional).
- Drafted only where the verse names land, a house or vehicles (भूमि, क्षेत्र, गृह, सद्म, वाहन, यान); the verse's other matters are not drafted for Property.

**Transcription notes**

Read from the page image (PDF p. 147, printed p. 149). The PDF text layer agrees. The Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### S3. 4th house: वाहन (vehicles)

- **Term id:** `provisional.signification.bhava.4.vahana` (v1)
- **Subject:** bhava 4
- **Domain tags:** Property (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** द्वादशभावविचाराध्यायः (अथ द्वादशभावेषु विचार्यत्वमाह), verse 4; PDF p. 147 (printed p. 149).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not property terms (they include relatives, the mother's happiness and treasure); the full translation is kept for the expert review and is not shown in a property answer.

**Original text**

> वाहनस्याथ बन्धूनां मातृसौख्यादिकानपि । निधिक्षेत्रं गृहं चापि पातालाच्च निरीक्षयेत् ॥ ४ ॥

**Draft translation**

> From the fourth house (पाताल), one should examine vehicles, relatives, the happiness of the mother and the like, treasure, fields (land) and the house. [Hindi: चौथे भाव से वाहन (सवारी) का, बंधुओं का, मातृसुख का, निधि (गड़े धन) का, क्षेत्र (खेत) तथा गृह का विचार करना चाहिए।]

**Statement shown in the app (with the provisional badge)**

> The text lists vehicles (वाहन) first among the matters judged from the 4th house.

**Interpretive reasoning**

The verse opens with वाहन (vehicle, conveyance), which the edition's Hindi glosses as सवारी (a ride, conveyance); 'vehicles' is displayed. बन्धु (relatives) and मातृसौख्य (the mother's happiness) are not property terms and are not tagged Property (JyotAI has no relatives, mother or happiness domain); निधि (treasure; Hindi: buried wealth) is a wealth matter and is not drafted.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, price or prediction. Domain tag: Property (provisional).
- Drafted only where the verse names land, a house or vehicles (भूमि, क्षेत्र, गृह, सद्म, वाहन, यान); the verse's other matters are not drafted for Property.

**Transcription notes**

Read from the page image (PDF p. 147, printed p. 149). The PDF text layer agrees. The Sanskrit and the edition's Hindi agree.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### S4. Mars: भूमि (land (kāraka))

- **Term id:** `provisional.signification.graha.mars.bhumi` (v2)
- **Subject:** graha mars
- **Domain tags:** Property (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह, verse 3; PDF p. 109 (printed p. 111).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not property terms (they include disease, theft, children (the text says 'son'), brothers and the king's enemies); the full translation is kept for the expert review and is not shown in a property answer.

**Original text**

> सत्त्वसद्मभूमिपुत्रशीलचौर्यरोगब्रह्मभ्रातृपराक्रमाग्निसाहसराजशत्रुकारकः कुजः ॥ ३ ॥

**Draft translation**

> Kuja (Mars) is the kāraka of strength, the dwelling (सद्म), land (भूमि), sons, conduct, theft, disease, ब्रह्म (left untranslated; the Hindi keeps ब्रह्म), brothers, valour, fire, daring and the king's enemies. [Hindi: ओज, भूमि, पुत्र, शील, चोर, रोग, ब्रह्म, भाई, पराक्रम, अग्नि, साहस और राजशत्रु के कारक भौम हैं।]

**Statement shown in the app (with the provisional badge)**

> The text names Mars a kāraka (significator) of land (भूमि).

**Interpretive reasoning**

Mars's own kāraka list names भूमि (land), and the edition's Hindi keeps भूमि. Only भूमि is drafted in this record; सद्म (dwelling) is a separate record. The other Mars terms (strength, children (the text says 'son'), conduct, theft, disease, brothers, valour, fire, daring, the king's enemies) are not property terms and are not drafted.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, price or prediction. Domain tag: Property (provisional).
- Drafted only where the verse names land, a house or vehicles (भूमि, क्षेत्र, गृह, सद्म, वाहन, यान); the verse's other matters are not drafted for Property.
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page image (PDF p. 109, printed p. 111). The PDF text layer reads सत्वसद्म… चौयरोगत्रर्मश्रात् for सत्त्वसद्म… चौर्यरोगब्रह्मभ्रातृ. The edition's Hindi renders सत्त्व as ओज and does not render सद्म; it keeps भूमि.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### S5. Mars: सद्म (dwelling (kāraka))

- **Term id:** `provisional.signification.graha.mars.sadma` (v2)
- **Subject:** graha mars
- **Domain tags:** Property (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह, verse 3; PDF p. 109 (printed p. 111).
- **Confidence (author's):** medium
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not property terms (they include disease, theft, children (the text says 'son'), brothers and the king's enemies); the full translation is kept for the expert review and is not shown in a property answer.

**Original text**

> सत्त्वसद्मभूमिपुत्रशीलचौर्यरोगब्रह्मभ्रातृपराक्रमाग्निसाहसराजशत्रुकारकः कुजः ॥ ३ ॥

**Draft translation**

> Kuja (Mars) is the kāraka of strength, the dwelling (सद्म), land (भूमि), sons, conduct, theft, disease, ब्रह्म (left untranslated; the Hindi keeps ब्रह्म), brothers, valour, fire, daring and the king's enemies. [Hindi: ओज, भूमि, पुत्र, शील, चोर, रोग, ब्रह्म, भाई, पराक्रम, अग्नि, साहस और राजशत्रु के कारक भौम हैं।]

**Statement shown in the app (with the provisional badge)**

> The text names Mars a kāraka (significator) of the dwelling (सद्म); the edition's Hindi does not render the word, so the reading is tentative.

**Interpretive reasoning**

The list opens सत्त्वसद्म…; read as separate members of the compound, सद्म is a dwelling or house. Confidence is medium: the edition's Hindi renders सत्त्व as ओज and gives no word for सद्म, and सत्त्वसद्म could also be read together ('abode of strength'). Only सद्म is drafted in this record.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, price or prediction. Domain tag: Property (provisional).
- Drafted only where the verse names land, a house or vehicles (भूमि, क्षेत्र, गृह, सद्म, वाहन, यान); the verse's other matters are not drafted for Property.
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page image (PDF p. 109, printed p. 111). The PDF text layer reads सत्वसद्म… चौयरोगत्रर्मश्रात् for सत्त्वसद्म… चौर्यरोगब्रह्मभ्रातृ. The edition's Hindi renders सत्त्व as ओज and does not render सद्म; it keeps भूमि.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### S6. Jupiter: गृह (house (kāraka))

- **Term id:** `provisional.signification.graha.jupiter.griha` (v2)
- **Subject:** graha jupiter
- **Domain tags:** Property (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह, verse 5; PDF p. 109 (printed p. 111).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not property terms (they include one's own work, wealth, children (the text says 'son') and friends); the full translation is kept for the expert review and is not shown in a property answer.

**Original text**

> स्वकर्मयजनदेवब्राह्मणधनगृहकाञ्चनवस्त्रपुत्रमित्रान्दोलनादिकारको गुरुः ॥ ५ ॥ | v.37: सूर्यो गुरुः कुजः सोमो गुरुर्भौमः सितः शनिः । गुरुश्चन्द्रसुतो जीवो मन्दश्च भावकारकः ॥ ३७ ॥

**Draft translation**

> v.5: Guru (Jupiter) is the kāraka of one's own work, sacrifice, the gods, brāhmaṇas, wealth (धन), house, gold, cloth, sons, friends, swings and the like. [Hindi: अपने कार्य, यज्ञ, देवता, ब्राह्मण, धन, गृह, सुवर्ण, वस्त्र, पुत्र, मित्र, आंदोलन आदि के कारक गुरु हैं।] v.37: the kārakas of the houses from the Lagna are, in order, Sun, Jupiter (the second), Mars, Moon (Hindi: Mercury), Jupiter, Mars, Venus, Saturn, Jupiter, Mercury, Jupiter (the eleventh), Saturn.

**Statement shown in the app (with the provisional badge)**

> The text names Jupiter a kāraka (significator) of the house (गृह).

**Interpretive reasoning**

Jupiter's own kāraka list (v.5) names गृह (house) next to धन (wealth), and the edition's Hindi keeps गृह. Only गृह is drafted for Property; धन is the separate provisional Wealth record. The other Jupiter terms (one's own work, sacrifice, the gods, children (the text says 'son'), friends) are not property terms. v.37 (Jupiter as bhāva-kāraka of the 2nd, 5th, 9th and 11th) does not name the 4th house and is not used here.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, price or prediction. Domain tag: Property (provisional).
- Drafted only where the verse names land, a house or vehicles (भूमि, क्षेत्र, गृह, सद्म, वाहन, यान); the verse's other matters are not drafted for Property.
- Where the text says पुत्र or सुत, the term is shown as written with the gloss "children (the text says 'son')"; it is a quoted term, never a prediction about the user. A source verse whose clause names a child's sex or denies children is held in the app and kept in full in the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, NEXT-CHILDREN-GUARD-01).

**Transcription notes**

Read from the page images. The PDF text layer breaks v.5 at काञ्चन (a line break, no letter lost) and garbles v.37 (सूयां गृरुः for सूर्यो गुरुः). In v.37 the Sanskrit's fourth kāraka is सोमः (Moon) while the Hindi gives बुध (Mercury); the second and eleventh (गुरुः) agree in both.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### S7. Venus: यान (vehicles (kāraka))

- **Term id:** `provisional.signification.graha.venus.yana` (v1)
- **Subject:** graha venus
- **Domain tags:** Property (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह, verse 6; PDF p. 109 (printed p. 111).
- **Confidence (author's):** high
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not property terms (they include the wife, happiness, music and ornaments); the full translation is kept for the expert review and is not shown in a property answer.

**Original text**

> कलत्रकार्मुकसुखगीतशास्त्रकाव्यपुष्पसुकुमारयौवनाभरणरजतयानस्वर्गलोकमौक्तिकविभवकवितारसादिकारको भृगुः ॥ ६ ॥

**Draft translation**

> Bhṛgu (Venus) is the kāraka of the wife, the bow, happiness, music, poetry, flowers, youth, ornaments, silver, vehicles (यान), heaven, pearls, splendour, verse, taste and the like. [Hindi: स्त्री, धनुष, सुख, गीतशास्त्र, काव्यशास्त्र, पुष्प, यौवन, आभूषण, चाँदी, सवारी, स्वर्गलोक, मोती, वैभव, कविता, रस आदि के कारक शुक्र हैं।]

**Statement shown in the app (with the provisional badge)**

> The text names Venus a kāraka (significator) of vehicles (यान).

**Interpretive reasoning**

Venus's own kāraka list names यान (vehicle, conveyance), which the edition's Hindi renders सवारी. Only यान is drafted for Property; कलत्र is the separate provisional Marriage record. The other Venus terms are not property terms.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, price or prediction. Domain tag: Property (provisional).
- Drafted only where the verse names land, a house or vehicles (भूमि, क्षेत्र, गृह, सद्म, वाहन, यान); the verse's other matters are not drafted for Property.

**Transcription notes**

Read from the page image (PDF p. 109, printed p. 111). The PDF text layer garbles v.6 (कामुक for कार्मुक, भगः for भृगुः) but reads यान correctly. The Sanskrit and the Hindi agree on यान/सवारी.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

### S8. Sun: क्षेत्र (fields or land (kāraka))

- **Term id:** `provisional.signification.graha.sun.kshetra` (v1)
- **Subject:** graha sun
- **Domain tags:** Property (provisional)
- **Source:** Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)
- **Verse / locator:** कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह, verse 1; PDF p. 109 (printed p. 111).
- **Confidence (author's):** medium
- **Author:** drafted_by: AI agent; adopted_by: project owner (pending)
- **Status:** provisional — pending expert review
- **Translation:** not shown in the app — The verse's other matters are not property terms (they include kingship, gems, the king and the father); the full translation is kept for the expert review and is not shown in a property answer.

**Original text**

> राज्यविद्रुमरक्तवस्त्रमाणिक्यराजवनपर्वतक्षेत्रपितृकारको रविः ॥ १ ॥

**Draft translation**

> Ravi (the Sun) is the kāraka of kingship, coral, red cloth, rubies, the king, forests, mountains, क्षेत्र (fields or regions) and the father. [Hindi: राज्य, मूँगा, रक्तवस्त्र, मानिक, राज, वन, पर्वत, क्षेत्र और पिता का कारक सूर्य होता है।]

**Statement shown in the app (with the provisional badge)**

> The text names the Sun a kāraka (significator) of क्षेत्र, read here as fields or land; the word may also mean a region, so the reading is tentative.

**Interpretive reasoning**

The Sun's list names क्षेत्र; the edition's Hindi keeps क्षेत्र without a gloss. Standing next to वन and पर्वत (forests, mountains), it may mean fields or land, or a region or sacred place, so confidence is medium. Only क्षेत्र is drafted. Because the reading is medium, the Sun is not one of the kārakas a Property answer lists (Mars, Jupiter and Venus each have a high-confidence term); the reviewer is asked.

**Conventions used**

- Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).
- Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 item 20).
- A signification term names a theme only: no polarity, weight, timing, price or prediction. Domain tag: Property (provisional).
- Drafted only where the verse names land, a house or vehicles (भूमि, क्षेत्र, गृह, सद्म, वाहन, यान); the verse's other matters are not drafted for Property.

**Transcription notes**

Read from the page image (PDF p. 109, printed p. 111). The PDF text layer reads राज्यविदुम… for राज्यविद्रुम…; क्षेत्र is read the same in both.

**Decision:** ☐ Approve ☐ Change ☐ Reject

Changed wording or condition (if Change): ______________________________

Reason (if Reject): ______________________________

Reviewer name, qualification, date: ______________________________

---

## Questions for the reviewer

### Q1. Which house is the kāraka of the wife: the 2nd (v.35) or the 7th (v.36)?

कारकाध्याय, अथ भावकारकमाह, PDF p. 108 (printed p. 110). v.35: धनभावं विजानीयाद्दारकारकमेव च (the house of wealth, the 2nd, is also the kāraka of the wife; Hindi: धनभाव स्त्रीकारक). v.36: सुते सुतं विजानीयाद्दारा सप्तमभावतः (sons from the 5th, the wife from the 7th; Hindi: सातवाँ स्त्री का कारक). JyotAI drafted no Marriage term from v.35: the 2nd-house term कुटुम्ब (family) was first proposed for Marriage (low) and is now proposed for Wealth only, and the 7th house carries जाया. Should the 2nd house carry any Marriage term, and how do v.35 and v.36 fit together?

Answer: ______________________________

### Q2. May the reviewed Career terms of the 2nd and 11th houses also be tagged Wealth?

The reviewed signification terms धन ('wealth', 2nd house) and लाभ ('gain'), वृद्धि ('increase', 11th house) were reviewed for Career only, so a Wealth answer does not show them. The provisional Wealth terms धन (2nd house), लाभ (11th house) and Jupiter as kāraka of धन are drafted separately. If the reviewed terms may be tagged Wealth (reviewed), the matching provisional terms would be withdrawn.

Answer: ______________________________

### Q3. Wording for the held 2nd-lord verses (6th: v.13; 12th: v.18)

Both verses are recorded in full above but held in the app (owner rule: no verse predicting poverty or loss is shown). Should either be shown, and with what wording?

Answer: ______________________________

### Q4. Which kārakas should a Property answer use?

कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह, PDF p. 109 (printed p. 111): Mars is the kāraka of भूमि (land) and सद्म (dwelling; the Hindi omits सद्म), v.3; Jupiter of गृह (house), v.5; Venus of यान (vehicles), v.6; the Sun of क्षेत्र (field or region), v.1. The bhāva-kāraka list (v.37, PDF p. 108) gives the 4th house to सोमः (Moon) in the Sanskrit and to Mercury in the Hindi, without naming property. JyotAI's Property answer lists Mars, Jupiter and Venus (each has a high-confidence property term); the Sun's क्षेत्र is a provisional signification (medium) only. Which kārakas are right, and how does v.37 fit?

Answer: ______________________________

### Q5. Are सम्पद् (v.27) and the Hindi संपत्ति for सर्वधनाधिप (v.29) property or wealth?

Fourth lord in the 2nd (v.27): सर्वसम्पद्युत, Hindi 'सभी सम्पत्तियों से युक्त', drafted for Property at low confidence. Fourth lord in the 4th (v.29): सर्वधनाधिप, धनाढ्य (wealth), which the Hindi renders 'सभी प्रकार की संपत्ति'; not drafted. Should either be a Property item, a Wealth item, or neither?

Answer: ______________________________

### Q6. Should D4 (Chaturthāṁśa) be calculated and shown for property, and by which method?

JyotAI calculates D1, D2, D9 and D10 only; no D4 is shown. A reviewer-approved D4 method (and whether any D4 reading belongs in a Property answer) is needed first.

Answer: ______________________________

### Q7. Is "children (the text says 'son')" the right display for पुत्र and for सुत?

Owner decision (NEXT-CHILDREN-GUARD-01): JyotAI never predicts or hints at the sex of a child, so where the text says पुत्र or सुत the app shows the term as written with the gloss "children (the text says 'son')" (second-lord verses 9, 10, 12, 13, 17, 18; the kāraka lists of Mars and Jupiter; the 11th-house verse; Venus's v.33; सुत also where it names the fifth house: सुतभाव v.12, सुतेशे vv. 37 and 40, सुते v.54). The app does not display a source verse whose clause names a child's sex or denies children (vv. 9 पुत्री, 10 पुत्रहीनः, 12 पुत्रवान्, 17 सुतहीनो, 18 ज्येष्ठपुत्रसुखं न हि): it shows a held notice, and the verses are in full in this pack. Please confirm the gloss for both terms, or give the wording to use.

Answer: ______________________________
