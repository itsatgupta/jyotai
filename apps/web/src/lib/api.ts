import type { AnalysisResult, AnalyzeRequest, ConsultationResponse, Context, DashboardInsightsResult, LocationSuggestion } from "./contracts";

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "";

const fieldNames: Record<string, string> = {
  birth_date: "Birth date", birth_time: "Birth time", place_name: "Birthplace",
  timezone: "Birthplace timezone", latitude: "Latitude", longitude: "Longitude", as_of: "As-of date and time",
};

function errorMessage(payload: unknown, status: number, path: string): string {
  const route = path.split("?", 1)[0];
  const detail = payload && typeof payload === "object" && "detail" in payload ? payload.detail : undefined;
  if (status === 422 && Array.isArray(detail)) {
    const fields = detail.flatMap((item: unknown) => {
      if (!item || typeof item !== "object" || !("loc" in item) || !Array.isArray(item.loc)) return [];
      const loc = item.loc.filter((part: unknown): part is string => typeof part === "string");
      const field = loc.at(-1);
      if (field === "birth_input" && "msg" in item && typeof item.msg === "string") {
        if (item.msg.includes("ambiguous")) return ["Birth time occurs twice in that timezone. Choose an unambiguous time."];
        if (item.msg.includes("do not exist")) return ["Birth time does not exist in that timezone. Choose another time."];
      }
      if (!field || !fieldNames[field]) return [];
      return [`${fieldNames[field]} is invalid or missing. Check this field and try again.`];
    });
    console.warn("API validation failed", { route, status, fields: [...new Set(detail.flatMap((item: unknown) => {
      if (!item || typeof item !== "object" || !("loc" in item) || !Array.isArray(item.loc)) return [];
      return item.loc.filter((part: unknown): part is string => typeof part === "string" && part in fieldNames);
    }))] });
    return [...new Set(fields)].join(" ") || "Check the entered details and try again.";
  }
  if (status === 409 && typeof detail === "string") return detail;
  console.warn("API request failed", { route, status });
  return status >= 500 ? "The service is temporarily unavailable. Please try again." : "Please check your details and try again.";
}

export class ApiError extends Error {
  constructor(message: string, readonly status: number) { super(message); }
}

async function readError(response: Response, path: string): Promise<ApiError> {
  const payload: unknown = await response.json().catch(() => null);
  return new ApiError(errorMessage(payload, response.status, path), response.status);
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw await readError(response, path);
  }
  return response.json() as Promise<T>;
}

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { signal });
  if (!response.ok) {
    throw await readError(response, path);
  }
  return response.json() as Promise<T>;
}

export const api = {
  context: (birth_input: AnalyzeRequest["birth_input"], as_of: string) =>
    post<Context>("/api/v1/context/snapshot", { birth_input, as_of }),
  analyze: (request: AnalyzeRequest) => post<AnalysisResult>("/api/v1/analyze", request),
  consultation: (request: AnalyzeRequest & { consultation_id?: string; reference_turn_id?: string; claim_ids?: string[] }) =>
    post<ConsultationResponse>("/api/v1/consultation", request),
  dashboardInsights: (birth_input: AnalyzeRequest["birth_input"], as_of: string) =>
    post<DashboardInsightsResult>("/api/v1/insights/dashboard", { birth_input, as_of }),
  locations: (query: string, signal?: AbortSignal) =>
    get<{ results: LocationSuggestion[] }>(`/api/v1/locations/search?q=${encodeURIComponent(query)}`, signal),
};
