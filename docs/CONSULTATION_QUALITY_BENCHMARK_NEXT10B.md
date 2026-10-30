# JYOTISH-AI-NEXT-10B consultation quality baseline

## Reproduction and scope

Baseline: `main` at `1c33cd48b37130ce4f05f425283fe41f7d774027` (`feat(ask): add evidence-linked multi-turn consultation`). Initial status contained only the protected untracked research file. Active interpretation manifest: `jyotish.production.cumulative@v10` (22 rules). Active timing release: `jyotish.timing.production.career@v2` (2 rules). The captured context uses `deterministic-astrology-context-v1`, `vimshottari-v1`, the declared D1 sidereal/Lahiri/Whole Sign conventions, and the installed Swiss Ephemeris adapter. The fixed `as_of` is `2026-01-01T00:00:00+00:00`.

Run from `apps/api`:

```sh
uv run python tests/consultation_quality_benchmark.py --output /tmp/consultation-quality-v1-replay.json
cmp /tmp/consultation-quality-v1-replay.json tests/fixtures/consultation_quality_v1_results.json
.venv/bin/pytest -q tests/test_consultation_quality_benchmark.py tests/test_multiturn_consultation.py tests/test_career_consultation.py
.venv/bin/ruff check tests/consultation_quality_benchmark.py tests/test_consultation_quality_benchmark.py
```

Use a fresh replay path on every run. The runner refuses to overwrite any existing output, including the frozen `v1` results. The committed `consultation-quality-v1` scenario and captured results are immutable reference artifacts: future product changes must compare a new run with this baseline and record differences explicitly. A revised benchmark needs a new fixture version, new result filename and version identifier, with the original `v1` files retained. Never change failing expectations to improve a score.

The [versioned scenarios](../apps/api/tests/fixtures/consultation_quality_v1.json), [executable runner](../apps/api/tests/consultation_quality_benchmark.py), and [captured actual responses](../apps/api/tests/fixtures/consultation_quality_v1_results.json) are the acceptance artifacts. The runner posts to the real `/api/v1/consultation` FastAPI contract. It removes process-random IDs and birth inputs from the saved results, while retaining answer text, follow-ups, selected fact values, claim ledgers, source references, timing windows, statuses, and releases. Five synthetic birth profiles are used. The fault injection in J31 deliberately removes one already calculated fact at the context boundary; it tests fail-closed UNKNOWN behavior and is not a normal engine output. No new rule, historical manifest, or calculation convention was activated.

The optional LLM path was **NOT EXECUTED**: the benchmark deliberately pins `LLM_ENABLED=false`, and no safe live provider configuration was established for this run. Existing provider-packet privacy tests were run separately. No live user rating or real-world prediction outcome was collected.

## Scenario inventory and executed result

`FULL` below means `FULLY_SUPPORTED_WITHIN_DECLARED_SCOPE`; `PARTIAL` means `PARTIALLY_SUPPORTED`. `FACTS` means `FACTS_ONLY`: the deterministic response payload has the fact, but Ask does not provide the requested interpretation or a usable direct answer. `UNSUPPORTED` is not counted as a completed consultation. All answers and exact follow-up replies are in the captured results file.

| ID | Profile | Journey target | Initial answerability | Observed follow-up / finding |
| --- | --- | --- | --- | --- |
| J01 | P_MATCH | Overall chart understanding | UNSUPPORTED | Needs domain clarification for natural “overall chart” phrasing. |
| J02 | P_MATCH | Career strengths | PARTIAL | Placement explanation works; “What are the limitations?” gives generic clarification. |
| J03 | P_MATCH | Career in 2027 | PARTIAL | Why, Dasha, and explicit 2028 continuation work; broad timing context only. |
| J04 | P_MATCH | Career development over five years | PARTIAL | Static context; no reviewed trajectory synthesis. |
| J05 | P_MATCH | Current Mahadasha | FACTS | Calculated Jupiter Mahadasha exists in context; Ask asks for clarification. |
| J06 | P_MATCH | Current Antardasha meaning for career | FACTS | Routes to Career but omits the calculated Antardasha and its interpretation limit. |
| J07 | P_MATCH | Favorable Career periods | PARTIAL | One broad reviewed Mahadasha window; Dasha follow-up works. |
| J08 | P_MATCH | Why a placement claim was made | FULL | Placement, rule, source, and follow-up resolve. |
| J09 | P_MATCH | Multiple possible prior claims | PARTIAL | Generic why asks for a claim ID; Dasha follow-up resolves. |
| J10 | P_MATCH | Is 2028 better than 2027? | PARTIAL | Correctly refuses ranking and shows independently evaluated windows. |
| J11 | P_BUSINESS | Business suitability | PARTIAL | Approved contextual business evidence exists; no suitability method. |
| J12 | P_BUSINESS | Wealth context | PARTIAL | One reviewed D1 wealth interpretation appears in structured detail. |
| J13 | P_EDUCATION | Education context | PARTIAL | One reviewed D1 education interpretation appears in structured detail. |
| J14 | P_MATCH | Property purchase timing | UNSUPPORTED | No production property rule or timing; Dasha follow-up safely declines. |
| J15 | P_MATCH | Marriage timing | UNSUPPORTED | No production marriage rule or timing; Dasha follow-up safely declines. |
| J16 | P_MATCH | D10 Career interpretation | FACTS | D10 is calculated, but Ask silently gives D1 Career context. |
| J17 | P_MATCH | D9 Marriage interpretation | FACTS | D9 is calculated; no approved D9 interpretation or clear method-specific response. |
| J18 | P_MATCH | Exact promotion month | PARTIAL | Explicit unsupported precision; no invented month; Dasha follow-up declines. |
| J19 | P_MATCH | Which profession to choose | PARTIAL | Explicitly declines profession selection, with static placement context. |
| J20 | P_NO_MATCH | Career in 2027 | PARTIAL | Static placement matches, Career timing is `NO_MATCH`; Dasha follow-up declines. |
| J21 | P_OTHER | Career strengths with no static match | UNSUPPORTED | Exact D1 placement is shown; no approved interpretation matched. |
| J22 | P_MATCH | Career plus wealth and ambiguous follow-up | PARTIAL | Career context only; why follow-up asks which domain. |
| J23 | P_MATCH | Changed profile | PARTIAL initial | Cross-profile follow-up rejected with HTTP 409. |
| J24 | P_MATCH | Forged claim reference | PARTIAL initial | Forged reference rejected with HTTP 409. |
| J25 | P_MATCH | Expired consultation and recovery | PARTIAL initial | Expired follow-up rejected; a fresh consultation succeeds. |
| J26 | P_MATCH | Stale turn reference | PARTIAL initial | Stale reference rejected with HTTP 409. |
| J27 | P_MATCH | Exact salary in 2027 | UNSUPPORTED | No Career route for “salary”; no amount invented. |
| J28 | P_MATCH | Two-year Career comparison | PARTIAL | Comparison method `UNSUPPORTED`/not evaluated; no ranking. |
| J29 | P_EDUCATION | Explicit overall reading | PARTIAL | One reviewed general D1 contextual interpretation. |
| J30 | P_MATCH | Exact displayed claim ID | FULL | Claim ID resolves to its approved source and fact. |
| J31 | P_MATCH | Missing approved fact injection | UNSUPPORTED | Four active Career rules become `UNKNOWN`; no match is inferred. |
| J32 | P_MATCH | “What about next year?” | PARTIAL initial | Follow-up fails to resolve 2028 from the prior 2027 claim. |
| J33 | P_MATCH | “Is next year better?” | PARTIAL initial | Follow-up asks for two years instead of resolving 2027/2028, then refusing ranking. |
| J34 | P_MATCH | New process-local store | PARTIAL initial | Replacing the in-memory store simulates a process restart; follow-up is rejected with HTTP 409. |

## Correctness and traceability

All **34/34** executed journeys passed the runner's hard structural gates. These gates compare selected evidence facts to the deterministic derived-fact bundle, check active rule membership and supported claim references, check D1-only interpreted evidence and domain separation, verify active Dasha containment at `as_of`, independently recompute each returned timing window's Mahadasha/Antardasha lord and complete half-open boundaries, enforce the requested-date intersection and unsupported precision behavior, and reject obvious invented promotion/salary/profession assertions. Profile change, forged claim, stale turn, expiry, and simulated process-store loss are tested through HTTP 409; recovery is tested through a new request. Existing provider privacy tests passed. This is **contract traceability**, not independent external ephemeris validation or proof that an astrological prediction will happen.

The observed status distinctions are: `MATCH` for the P_MATCH 2027 Career window; `NO_MATCH` for P_NO_MATCH 2027 Career timing; `UNKNOWN` only under J31's labeled missing-fact injection; `UNSUPPORTED` for exact-month and comparison methods; and `NOT_EVALUATED` for unrun optional LLM behavior and external predictive accuracy. No same-domain selection in this suite contained both approved supporting and challenging matches. The benchmark therefore reports **no observed approved conflict** and does not invent one.

The source and claim references are retained per response in the JSON. For example, J03's tenth-lord-in-fourth placement resolves to the active D1 rule `bphs.d1.house_lord.10.in_4_or_10.v1`, while its 2027 broad window resolves to `bphs.timing.vimshottari.career.10th_lord.in_4.md.v1`. The independent Dasha check places J03's Jupiter Mahadasha at `2015-03-18T04:20:01.069357Z` through `2031-03-18T04:20:01.069357Z` (end exclusive); its 2027 answer uses only the 2027 calendar intersection. The active Antardasha at the fixed `as_of` is Sun, `2025-09-28T11:32:01.069357Z` through `2026-07-17T16:20:01.069357Z` (end exclusive). These are calculated facts, not outcome predictions.

The suite cannot prove independent longitude or ascendant correctness. CALC-01 already records unresolved external comparison and ephemeris reproducibility dependencies; CALC-02 remains a separate independent reference-validation dependency. It also cannot prove absence of every possible hallucination by regex alone; the claim ledger and evidence provenance provide the stronger structural constraint. No live provider output was judged.

## Answerability and product value

The product denominator excludes five repeated security/process-state starts and the one fault injection, leaving **28 ordinary questions**. `FULL`: **2/28**; `PARTIAL`: **17/28**; `FACTS_ONLY`: **4/28**; `UNSUPPORTED`: **5/28**. **21/28** had at least one matching, selected rule; that does not mean the user's requested method was answered. A stricter, explicitly editorial coding found **10/28** initial questions with a substantive, relevant, evidence-backed response to the requested target (J03, J07–J10, J12–J13, J30, J32–J33). This coding is reproducible in the runner, but is not a human user rating or satisfaction estimate. The five security/process-state starts and J31 are excluded from these product metrics.

The **10/28** editorial count asks whether an initial answer contains useful evidence for its target, even when it also leaves part of the question unanswered; J32–J33 qualify on their initial 2027 answers despite their failed follow-ups. The **2/28** `FULL` count requires the entire requested question to be supported within the declared scope. These are different classifications, and neither is a user satisfaction score. Correct refusals protect integrity but are not counted as substantive astrological consultations.

| Domain / target | Benchmark IDs | Scope result |
| --- | --- | --- |
| D1 Career placement | J08, J30 | `FULLY_SUPPORTED_WITHIN_DECLARED_SCOPE` |
| Career strengths, periods, development, comparisons and exact outcomes | J02–J04, J07, J09–J10, J18–J21, J28, J32–J33 | `PARTIALLY_SUPPORTED` where contextual evidence exists; J21 `UNSUPPORTED`. Exact outcomes/comparison are not established. |
| Business suitability | J11 | `PARTIALLY_SUPPORTED`: contextual business rule, no suitability synthesis. |
| Wealth | J12 | `PARTIALLY_SUPPORTED`: one D1 contextual rule. |
| Education | J13 | `PARTIALLY_SUPPORTED`: one D1 contextual rule. |
| Overall/general | J01, J29 | J01 `UNSUPPORTED` natural phrasing; J29 `PARTIALLY_SUPPORTED` narrow D1 context. |
| Current Dasha facts and D9/D10 requests | J05–J06, J16–J17 | `FACTS_ONLY` in the deterministic payload; requested interpretation is absent. |
| Property and Marriage timing | J14–J15 | `UNSUPPORTED`: no approved production interpretation/timing rules. |
| Health, legal and investment consultations | None | `NOT_EVALUATED` by this suite. |

The API's top-level domain routing passed **31/34**, but that overstates question-target routing: J06's Antardasha, J16's D10, and J17's D9 requests were treated as ordinary domain questions without a method-specific explanation. The editorial question-target routing count is **28/34**. None of those boundary misses created an unauthorized D9/D10 interpretation; they are relevance and wording defects.

Multi-turn structural success was **22/25** executed follow-ups. Success includes five expected HTTP 409 reference, expiry and process-store rejections, one successful new consultation after expiry, valid claim/Dasha explanations, safe unsupported responses, and appropriate ambiguity prompts. The three failures are J02's limitations request and J32–J33's relative-year follow-ups. The consultation store is process-local, bounded to 500 records, and expires entries after 30 minutes. J34 simulates replacing that store and confirms the old consultation fails; actual multi-worker deployment and restart recovery remain **NOT_EVALUATED** and require persistent session design. No database persistence was built.

## Human-review rubric

For each journey, recruit raters who see the question, the visible UI response, and the supplied evidence. Score each applicable dimension **1–5**: 1 = misses or misleads, 2 = major gaps, 3 = partly useful, 4 = good with a minor gap, 5 = directly useful and clear. Mark `N/A` when the dimension does not apply, and write one concrete reason plus a cited response span for any score below 4. A correctness-gate failure overrides the quality score and fails the journey. Do not ask raters to judge real-world predictive truth from an astrological consultation.

| Dimension | What the rater checks |
| --- | --- |
| 1. Directness | Did it answer the real question, including the requested method and precision? |
| 2. Personalization | Did it use this chart's calculated facts rather than generic prose? |
| 3. Clarity | Could a non-expert understand the factors and limits? |
| 4. Detail | Was the level of detail proportionate to the question? |
| 5. Dasha context | Was relevant Dasha context explained, or its absence stated? |
| 6. Accessible evidence | Could the user find the fact, rule, source and claim behind the statement? |
| 7. Follow-up coherence | Did the reply carry the correct profile, claim and year forward? |
| 8. Repetition | Did the answer avoid repeating generic stock text? |
| 9. Unsupported request | Was a missing method or precision explained plainly? |
| 10. Methodology usefulness | Did the answer help the user understand what this declared Jyotish method says? |

All dimensions are currently **USER_RATING_PENDING**. The structural counts above must not be presented as user satisfaction.

## Ranked gaps and release decision

| Rank | Category | Evidence in this suite | Impact / frequency / correctness risk / feasibility / expected improvement |
| --- | --- | --- | --- |
| 1 | B, D, J — missing approved methodology and synthesis | 17 partial, 4 facts-only, 5 unsupported product questions; business suitability, career trajectory, comparisons, Property, Marriage, D9/D10 meaning lack reviewed methods. | Very high / frequent / high if guessed / low until expert review / potentially large after approval. Substantive expansion is blocked by expert-approved knowledge. |
| 2 | E, G — follow-up reference resolution | J32–J33 miss relative year; J02 misses “limitations”; 3/25 follow-ups fail. | High / 3 observed / low if constrained to existing claims / high / measurable improvement of up to three frozen cases. |
| 3 | E, F — method-aware routing and explicit boundaries | J01, J05, J27 domain routing misses; J06, J16, J17 silently miss requested method. | High / 6 observed / medium / medium / clearer, more relevant answers without new doctrine. |
| 4 | C — timing interpretation breadth | J20 `NO_MATCH`; J18 exact month unsupported; only two active Career timing rules. | High / several / high if invented / low pending expert review / improved timing only after approval. |
| 5 | F, H — presentation of contextual evidence | J11–J13 top-level text is generic; reviewed statements live in separate UI sections. The UI itself was not browser-journey tested here. | Medium / 3 observed / low / medium / improved discoverability; browser impact `NOT_EVALUATED`. |
| 6 | A — independent calculation validation | Structural Dasha checks pass, but external ephemeris reference coverage remains incomplete. | High correctness importance / cross-cutting / high / external dependency / trust improvement, not a measured consultation uplift. |
| 7 | I — correctly declined requests | J14–J15, J18, J28 decline unapproved timing/comparison. | Protects correctness; it is not a complete consultation and should not be counted as one. |

**One next implementation slice:** improve process-local evidence-linked follow-up resolution using the prior anchored year and claim ledger. Resolve “next year” to the year after the prior year, independently evaluate both broad windows for a comparison, refuse a relative outcome ranking, and answer “What are the limitations?” from the existing limitations. Keep the same profile, release, and stale-reference gates. The measurable acceptance target is to move J02, J32 and J33 from failed to successful follow-ups, while preserving all 34 correctness gates and the five reference/process-store rejections. This uses only currently approved evidence and adds no Jyotish rule. It will not make Property, Marriage, D9/D10 or career prediction substantive; expert-reviewed methodology is the dominant blocker to that larger product goal.

### Bounded NEXT-10C implementation contract

Change only the consultation follow-up resolver and its focused tests; preserve the `v1` scenarios and captured responses. Keep the previous profile, anchored claim, approved release, and reference checks. The three failures and required corrections are:

| Journey | Original → follow-up | Actual reply | Cause and smallest safe correction | Regression test |
| --- | --- | --- | --- | --- |
| J02 | “What are my career strengths?” → “What are the limitations?” | “Please ask which placement, Dasha, limitation, or approved claim you want explained.” | Limitation wording: the resolver's singular `limit` pattern misses “limitations”. Match that wording and answer from the anchored answer's existing limitations; add no new conclusion. | Assert an answered reply that cites the anchored limitations and retains the linked claim/evidence references. |
| J32 | “How will my career be in 2027?” → “What about next year?” | “Please ask which placement, Dasha, limitation, or approved claim you want explained.” | Relative-date resolution/routing: the continuation branch recognizes explicit years only. Resolve “next year” from the single anchored 2027 range to 2028, then run the same governed Career analysis as an explicit 2028 continuation. | Assert a 2028 requested range and independently checked 2028 timing evidence; reject ambiguous or missing anchors. |
| J33 | “How will my career be in 2027?” → “Is next year better?” | “Which two years would you like to compare?” | Relative-date resolution/comparison routing: the comparison branch sees only zero explicit years. Resolve the anchored 2027 and the next 2028 year, evaluate each broad window separately, and retain the unsupported relative-ranking response. | Assert both years and their separately governed timing contexts appear, with no comparative prediction; reject ambiguous or missing anchors. |

After NEXT-10C, run the current full correctness and security suite plus a fresh versioned replay. Report the changes against `consultation-quality-v1` explicitly; do not rewrite its failed follow-ups or promote a safe refusal to a substantive consultation.

Separate dependencies: **EXPERT-01** must review and approve new domain, D9/D10, comparison and timing doctrine before activating it; **CALC-02** must establish independent calculation references, boundary coverage and reproducible ephemeris/time-zone provenance before stronger calculation-accuracy claims; **production session persistence** needs a privacy-reviewed shared store, expiry semantics and cross-process tests before long-lived follow-ups. None is implemented by this benchmark.

## Checks, files and repository state

The original capture executed 34 API journeys and 25 follow-ups. Final review ran `uv run ruff check .` (passed), `uv run mypy src` (81 source files, passed), and `uv run pytest -q` (538 passed, one existing Starlette/httpx deprecation warning). A fresh runner output matched the frozen `v1` results byte for byte with `cmp`; `git diff --check` passed. No live LLM test, external reference comparison, user study, browser UI journey, or prediction-accuracy test was executed.

Only this report, the scenario JSON, the runner, its frozen results JSON, and its pytest file belong to the baseline commit. No production code, active rules, or protected research material belongs to it.
