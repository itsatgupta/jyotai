import type { AnalysisResult, AnalyzeRequest, Context, DashboardInsightsResult, LocationSuggestion } from "./contracts";

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "";

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const payload: { detail?: string } = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? "The deterministic service is temporarily unavailable.");
  }
  return response.json() as Promise<T>;
}

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { signal });
  if (!response.ok) {
    const payload: { detail?: string } = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? "The service is temporarily unavailable.");
  }
  return response.json() as Promise<T>;
}

export const api = {
  context: (birth_input: AnalyzeRequest["birth_input"], as_of: string) =>
    post<Context>("/api/v1/context/snapshot", { birth_input, as_of }),
  analyze: (request: AnalyzeRequest) => post<AnalysisResult>("/api/v1/analyze", request),
  dashboardInsights: (birth_input: AnalyzeRequest["birth_input"], as_of: string) =>
    post<DashboardInsightsResult>("/api/v1/insights/dashboard", { birth_input, as_of }),
  locations: (query: string, signal?: AbortSignal) =>
    get<{ results: LocationSuggestion[] }>(`/api/v1/locations/search?q=${encodeURIComponent(query)}`, signal),
};
