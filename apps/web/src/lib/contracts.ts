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
  ascendant?: { sign: string; degree_in_sign: string | number; nakshatra: { nakshatra: string; pada: number } };
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
  answers: ComposedAnswer[];
};

export type ComposedAnswer = {
  answer: string;
  referenced_evidence_item_ids: string[];
  timing_answered: false;
  corpus_limitation: boolean;
  interpretation_contract_sha256: string;
  manifest_id: string;
  manifest_version: string;
};

export type AnalyzeRequest = { birth_input: BirthInput; as_of: string; question: string };

export type DashboardDomain = "career" | "wealth" | "education" | "business" | "children" | "spirituality" | "travel" | "friends";

export type DashboardInsight = {
  domain: DashboardDomain;
  answers: ComposedAnswer[];
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
