export type BirthInput = {
  display_name?: string | null;
  place_name?: string | null;
  birth_date: string;
  birth_time: string;
  timezone: string;
  latitude: number;
  longitude: number;
};

export type Planet = {
  body: string;
  sign: string;
  degree_in_sign: string | number;
  /** D1 only: degree within the sign as DD°MM′ (server-formatted, minutes truncated). */
  degree_in_sign_dms?: string | null;
  house_number: number;
  retrograde?: boolean | null;
  motion_speed?: string | number | null;
  nakshatra?: { nakshatra: string; pada: number };
};

export type TransitPlanet = Omit<Planet, "nakshatra" | "house_number"> & {
  nakshatra: string;
  pada: number;
};

export type House = { number: number; sign: string };

export type Chart = {
  methodology: { chart_type: string };
  ascendant?: { sign: string; degree_in_sign: string | number; degree_in_sign_dms?: string | null; nakshatra: { nakshatra: string; pada: number } };
  houses: House[];
  planets: Planet[];
};

export type Context = {
  birth_input: BirthInput;
  requested_as_of: string;
  normalized_as_of_utc: string;
  d1: Chart;
  d9: Chart;
  d10: Chart;
  active_dasha: {
    instant: string;
    mahadasha: { lord: string; start: string; end: string };
    antardasha: { lord: string; start: string; end: string };
  };
  transit_snapshot: { normalized_utc_instant: string; positions: TransitPlanet[] };
};

export type Intent = {
  intent_id: string;
  domain: string;
  shape: string;
  temporal_intent: string;
  requires_timing: boolean;
  time_range?: { start_date: string; end_date: string } | null;
  unresolved_relative_time?: string | null;
};

export type Routing = {
  status: "routable" | "needs_clarification" | "unsupported";
  intents: Intent[];
  issues: string[];
};

export type Evidence = {
  rule_id: string;
  rule_version: string;
  domain: string;
  evaluation_status: string;
  evidence_direction: string;
  posture: string;
  resolved_facts: { fact_id: string; value: unknown }[];
  condition_trace: unknown;
  governance_provenance: Record<string, unknown>;
  fact_provenance: Record<string, unknown>;
};

export type Selection = {
  question_intent: Intent;
  selected_matched: Evidence[];
  relevant_unmatched: Evidence[];
  relevant_unknown: Evidence[];
  excluded: { rule_id: string; rule_version: string; domain: string; exclusion_reason: string }[];
  capability_summary: {
    timing_requested: boolean;
    timing_answerability_established: boolean;
    has_matched_evidence: boolean;
  };
};

export type AnalysisResult = {
  context: Context;
  routing: Routing;
  selections: Selection[];
  answers: DetailedComposedAnswer[];
};

export type ComposedAnswer = {
  answer: string;
  referenced_evidence_item_ids: string[];
  timing_answered: boolean;
  corpus_limitation: boolean;
  interpretation_contract_sha256: string;
  manifest_id: string;
  manifest_version: string;
};

export type DetailedEvidence = {
  placement_explanation: string;
  reviewed_statement: string;
  question_framing: string;
  source_work: string;
  source_section: string;
  source_reference?: string | null;
  chart_scope: "D1/Rashi";
  posture: "static/contextual";
  domain: string;
  /** NEXT-ADMIT-02: reviewer weight, display order only (secondary is shown as "Supporting"). */
  weight?: "primary" | "secondary";
  /** NEXT-ADMIT-02 (X2): the rule lord's sign dignity, a calculated modifier only. */
  lord_dignity?: string | null;
};

export type ReviewTypeLabel =
  | "Independent reviewer (Pandit ji, Acharya)"
  | "Project-owner review (not independently certified)"
  | "Project interpretive convention, reviewer-approved; no source verse identified";

/** NEXT-THEMES-01: one cited rule's review type, from its existing record. Disclosure only. */
export type RuleReviewType = {
  rule_id: string;
  review_type: ReviewTypeLabel;
};

/** NEXT-PROVISIONAL-01: the full justification of a provisional rule (evidence disclosure). */
export type ProvisionalJustification = {
  source_work: string;
  locator: string;
  original_text: string;
  draft_translation: string;
  interpretive_reasoning: string;
  conventions: string[];
  confidence: "high" | "medium" | "low";
  author: "project owner, provisional" | "drafted_by: AI agent; adopted_by: project owner (pending)";
  status: "provisional";
  transcription_notes?: string | null;
};

/** NEXT-PROVISIONAL-01: a matched provisional rule; returned only with include_provisional. */
export type ProvisionalInterpretation = {
  rule_id: string;
  rule_version: string;
  tier: "provisional";
  badge: "Provisional · high confidence" | "Provisional · medium confidence" | "Provisional · low confidence";
  domain: string;
  placement_explanation: string;
  statement: string;
  fact_ids: string[];
  corpus_release: string;
  justification: ProvisionalJustification;
};

export type DetailedComposedAnswer = ComposedAnswer & {
  rule_review_types?: RuleReviewType[];
  provisional_interpretations?: ProvisionalInterpretation[];
  claim_ledger?: CareerClaimLedger | null;
  career_answer_plan?: CareerAnswerPlan | null;
  consultation_sections?: ConsultationSection[];
  why_it_applies?: string[];
  reviewed_interpretations?: string[];
  limitations?: string[];
  evidence?: DetailedEvidence[];
  narrative?: {
    summary: string;
    explanation: string;
    question_relevance: string;
    follow_up?: string | null;
  } | null;
  timing?: CareerTimingContext | null;
  /** NEXT-COMPARE-02: a factual side-by-side of two calendar years; never a ranking. */
  career_comparison?: CareerYearComparison | null;
};

export type ComparisonSentence = {
  text: string;
  basis: "fact" | "rule" | "fixed";
  claim_ids: string[];
  fact_ids: string[];
  rule_ids: string[];
  calc_method_ids: string[];
};

export type ComparisonTimingIndication = {
  claim_id: string;
  rule_id: string;
  label: string;
  reviewed_statement: string;
  source_reference: string;
  precision: "BROAD_PERIOD" | "SUB_PERIOD";
  local_span: string;
};

export type CareerYearColumn = {
  year: number;
  dasha_segments: PlannedDashaSegment[];
  periods: ComparisonSentence[];
  lord_facts: ComparisonSentence[];
  timing_status: "MATCH" | "NO_MATCH" | "UNKNOWN" | "UNSUPPORTED" | "NOT_EVALUATED";
  timing_indications: ComparisonTimingIndication[];
  timing: ComparisonSentence[];
  co_references: ComparisonSentence[];
  dasha_interpretation: ComparisonSentence;
  manifest_id: string;
  manifest_version: string;
  methodology_version: string;
  timing_release_id: string;
  timing_release_version: string;
  synthesis_version?: string | null;
  answer_plan_version?: string | null;
};

export type CareerYearComparison = {
  view_version: "comparison-view-v1";
  comparison_mode: "SIDE_BY_SIDE";
  ranking_status: "unsupported";
  unit: "calendar_year";
  years: [number, number];
  direct: ComparisonSentence[];
  differences: ComparisonSentence[];
  natal_shared: ComparisonSentence[];
  columns: [CareerYearColumn, CareerYearColumn];
  why_no_ranking: ComparisonSentence[];
  limitations: ComparisonSentence[];
};

export type DashaContextSentence = { text: string; fact_ids: string[] };

export type SynthesisLink = {
  link_type: "SAME_PLANET" | "SAME_HOUSE" | "SAME_PERIOD";
  claim_id: string;
  claim_label: string;
  claim_subject?: string | null;
  claim_fact_ids: string[];
  claim_rule_ids: string[];
  dasha_fact_ids: string[];
  /** Admitted Dasha interpretation rules only; empty when none are admitted. */
  dasha_rule_ids: string[];
  /** Calculation methodology provenance; never a rule. */
  calc_method_ids: string[];
  segment_ids: string[];
  period_role?: "Mahadasha" | "Antardasha" | null;
  period_lord?: string | null;
  period_span?: string | null;
  period_covers_year?: boolean;
  shared_reference: string;
  text: string;
};

/** One rendered sentence and the ids it was generated from (sentence-to-fact mapping). */
export type SynthesisSentence = {
  text: string;
  claim_ids: string[];
  fact_ids: string[];
  rule_ids: string[];
  calc_method_ids: string[];
};

export type CareerSynthesis = {
  synthesis_version: string;
  year: number;
  reviewed_claim_ids: string[];
  links: SynthesisLink[];
  year_spanning_claim_ids?: string[];
  out_of_scope: string[];
};

export type ConsultationSection = {
  kind: "direct" | "glance" | "why" | "period_themes" | "natal" | "dasha" | "dasha_context" | "timing" | "limit";
  text: string;
  fact_sentences?: DashaContextSentence[];
  framing?: string | null;
  interpretation_rule_ids?: string[];
  synthesis_links?: SynthesisLink[];
  synthesis_sentences?: SynthesisSentence[];
};

export type LinkageFact = {
  fact_id: string;
  name: string;
  status: "KNOWN" | "UNKNOWN" | "NOT_APPLICABLE";
  value: boolean | number | string | number[] | null;
  source_fact_ids: string[];
  note: string | null;
};

export type DashaLordLinkage = { lord: string; facts: LinkageFact[] };

export type DashaPairLinkage = {
  methodology: { methodology_id: string; reference_point: "d1_lagna"; house_system: "whole_sign"; rahu_ketu_aspects: "unmodeled" };
  mahadasha: DashaLordLinkage;
  antardasha: DashaLordLinkage;
  ad_house_from_md: LinkageFact;
};

export type DashaInterpretationClaim = {
  rule_id: string;
  rule_version: string;
  source_locator: string;
  permitted_wording: string;
  segment_id: string;
  mahadasha_lord: string;
  antardasha_lord: string;
  matched_fact_ids: string[];
};

export type DashaInterpretationSlot = {
  corpus_manifest_id: string;
  corpus_manifest_version: string;
  claims: DashaInterpretationClaim[];
};

export type CareerAnswerPlan = {
  plan_version: string;
  question_intent: Intent;
  requested_time_scope?: { start_date: string; end_date: string } | null;
  signification_corpus_version?: string | null;
  period_themes?: SynthesisSentence[];
  calculated_fact_ids: string[];
  matched_claim_ids: string[];
  timing_evidence_ids: string[];
  timing_references: string[];
  dasha_segments: PlannedDashaSegment[];
  approved_source_locators: string[];
  limitation_ids: string[];
  answerability: "REVIEWED_TIMING_CONTEXT" | "NATAL_CONTEXT_ONLY" | "FACTS_ONLY" | "UNKNOWN" | "UNSUPPORTED";
  dasha_linkages?: { segment_id: string; linkage: DashaPairLinkage; tenth_lord?: { fact_id: string; value: string } | null }[];
  dasha_interpretation?: DashaInterpretationSlot | null;
  synthesis?: CareerSynthesis | null;
  tenth_lord_facts?: { fact_id: string; value: string }[];
  tenth_lord_dignity?: string | null;
  tenth_lord_dignity_fact_ids?: string[];
};

export type PlannedDashaSegment = {
  segment_id: string;
  mahadasha_lord: string;
  antardasha_lord: string;
  mahadasha_start: string;
  mahadasha_end: string;
  antardasha_start: string;
  antardasha_end: string;
  effective_start: string;
  effective_end: string;
  local_start: string;
  local_end: string;
};

export type CareerClaimLedger = {
  ledger_version: string;
  domain: "career";
  question_shape: string;
  requested_question_shape: string;
  claims: {
    claim_id: string;
    kind: "CALCULATED_FACT" | "APPROVED_INTERPRETATION" | "APPROVED_TIMING_INTERPRETATION" | "INSUFFICIENT_EVIDENCE" | "UNSUPPORTED_REQUEST";
    evaluation_status: "MATCH" | "NO_MATCH" | "UNKNOWN" | "NOT_EVALUATED" | "UNSUPPORTED";
    fact_ids: string[];
    rule_ids: string[];
    evidence_item_ids: string[];
    calculation_version: string;
    methodology_version: string;
    source_reference: string;
    permitted_wording: string;
    timing_reference?: string | null;
    authorized_precision?: string | null;
    missing_evidence: string[];
    period_lords?: string[];
  }[];
};

export type CareerTimingContext = {
  domain: "career";
  timing_answerability_established: boolean;
  status: "MATCH" | "NO_MATCH" | "UNKNOWN" | "UNSUPPORTED";
  scope?: "requested_range" | "default_40_year_horizon" | "historical_unbounded" | "precision_unsupported";
  requested_start_date?: string | null;
  requested_end_date?: string | null;
  calendar_timezone_offset?: string | null;
  evaluated_start?: string | null;
  evaluated_end?: string | null;
  partially_supported?: boolean;
  timing_release_id: string;
  timing_release_version: string;
  windows: {
    rule_id: string;
    precision: "BROAD_PERIOD" | "SUB_PERIOD";
    source_start: string;
    source_end: string;
    effective_start: string;
    effective_end: string;
    mahadasha_lord?: string | null;
    antardasha_lord?: string | null;
    why_this_period_applies: string;
    reviewed_statement: string;
    limitations: string[];
    source: {
      source_work: string;
      section: string;
      verse: string;
      chart_scope: "D1/Rashi";
      dasha_scope: string;
      precision: "BROAD_PERIOD" | "SUB_PERIOD";
    };
  }[];
  message: string;
  /** Deprecated one-rule v1 compatibility fields. Use per-window metadata. */
  precision?: "BROAD_PERIOD" | "SUB_PERIOD" | null;
  reviewed_statement?: string | null;
  why_this_period_applies?: string | null;
  limitations?: string[];
};

export type AnalyzeRequest = { birth_input: BirthInput; as_of: string; question: string; include_provisional?: boolean };

export type ConsultationState = {
  consultation_id: string;
  turn_id: string;
  domain: string | null;
  intent: Intent | null;
  claim_ids: string[];
  evidence_item_ids: string[];
  timing_references: string[];
  manifest_id: string;
  manifest_version: string;
  methodology_version: string;
  timing_release_id: string;
  timing_release_version: string;
  limitation: boolean;
};

export type ConsultationResponse = {
  state: ConsultationState;
  analysis: AnalysisResult | null;
  reply: string | null;
  status: "answered" | "clarification" | "unsupported";
  source_references: string[];
  resolved_claim_ids: string[];
  resolved_evidence_item_ids: string[];
  resolved_timing_references: string[];
  consultation_sections?: ConsultationSection[];
  /** Plain-language follow-up options; ids travel only in claim_ids. */
  choices?: ConsultationChoice[];
  career_comparison?: CareerYearComparison | null;
};

export type ConsultationChoice = { label: string; question: string; claim_ids: string[] };

export type ConsultationMessage = { question: string; response: ConsultationResponse };

export type DashboardDomain = "career" | "wealth" | "education" | "business" | "children" | "spirituality" | "travel" | "friends";

export type DashboardInsight = {
  domain: DashboardDomain;
  answers: DetailedComposedAnswer[];
  has_matched_evidence: boolean;
  matched_count: number;
  unmatched_count: number;
  unknown_count: number;
};

export type DashboardInsightsResult = { insights: DashboardInsight[] };

export type LocationSuggestion = {
  display_name: string;
  latitude: number;
  longitude: number;
  timezone: string;
  provider_id: string | null;
};
