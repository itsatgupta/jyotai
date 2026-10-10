# Dignity source admission v1

Record ID: `jyotish.dignity.source-admission.v1`  
Status: `REVIEWED_EXACT_LOCATOR`  
Scope: deterministic D1 factual `own_sign` and `exaltation_sign` only

This immutable review record governs the two factual tables consumed by
`jyotish.timing.dignity@v1`. It adds no rule, predictive claim, or
interpretation.

## Source

- Source ID: `bphs.selected-edition`
- Work: *Brihat Parashara Hora Shastra / Brihat Parashara Hora Shastram*
- Local reviewed artifact: `पराशरहोराशास्त्र Brihat Parashar Hora Shastra _text.pdf`
- Original language: Sanskrit; the selected artifact supplies a Hindi rendering.
- Review limitation: internal project-owner review against the selected local
  edition; it is not independent Sanskrit/Jyotish scholarly certification.

## Own-sign factual convention

- Section: `राशिप्रभेदाध्यायः` / Rāśi-prabheda.
- Exact locators: verses 7--24; printed pp. 23--26; local PDF pp. 21--24.
- Source-text anchors: `मेषराशिः कुजाधिपः` (v. 7), `शुक्राधिपो ... वृषः`
  (v. 8), `मिथुनाख्यो बुधाधिपः` (v. 9), `कर्कराशिर्मृगाङ्कोऽधिपतिः स्मृतः`
  (v. 11), `सिंहः सूर्याधिपः` (v. 12), and the corresponding
  ruler declarations for Virgo through Pisces (vv. 14--24).
- Reviewed Hindi rendering: each sign description explicitly identifies its
  `स्वामी` (ruler); it gives Aries/Scorpio--Mars, Taurus/Libra--Venus,
  Gemini/Virgo--Mercury, Cancer--Moon, Leo--Sun, Sagittarius/Pisces--Jupiter,
  and Capricorn/Aquarius--Saturn.
- Computational convention: `SIGN_RULERS` maps exactly those twelve signs to
  those seven planets; an `own_sign` fact is true only when a classical planet
  occupies a sign mapped to itself. Rahu and Ketu have no entry.

## Exaltation factual convention

- Section: `ग्रहस्वरूपाध्यायः` / Graha-svarūpa, `अथ ग्रहाणामुच्चनीचमाह`.
- Exact locator: verse 38; printed p. 32; local PDF p. 30. Verse 39 on the
  same page gives degrees and debilitation and is outside this admission.
- Sanskrit source text: `अजो वृषो मृगः कन्या कुलीरझषतौलिकाः । सूर्यादीनां क्रमादेतास्तुङ्गसंज्ञाः प्रकीर्तिताः ॥ ॥३८॥ ॥`
- Reviewed Hindi rendering: in order for Sun through Saturn, Aries, Taurus,
  Capricorn, Virgo, Cancer, Pisces, and Libra are stated as the exaltation
  signs. The edition also prints degree values, which are deliberately not
  admitted here.
- Computational convention: `EXALTATION_SIGNS` is exactly Sun--Aries,
  Moon--Taurus, Mars--Capricorn, Mercury--Virgo, Jupiter--Cancer,
  Venus--Pisces, Saturn--Libra. `exaltation_sign` is true only when the
  corresponding classical planet occupies its listed sign.

## Admission boundary

Admitted: factual sign ownership and factual exaltation-sign equality for Sun
through Saturn in D1/Rāśi.

Excluded: strength inference; favorable/unfavorable inference; Career
interpretation; timing interpretation by itself; exaltation degrees; all
mūlatrikoṇa degree ranges; varga/planetary strength; benefic/malefic
classification; Rahu/Ketu ownership or dignity.
