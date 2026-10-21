import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./api";

describe("API validation errors", () => {
  afterEach(() => vi.restoreAllMocks());

  it("turns structured FastAPI errors into readable field guidance", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 422, json: async () => ({ detail: [
      { loc: ["body", "birth_input", "latitude"], msg: "Input should be less than or equal to 90", type: "less_than_equal" },
      { loc: ["body", "as_of"], msg: "secret internal context", type: "value_error" },
    ] }) }));
    const diagnostics = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    await expect(api.context({} as Parameters<typeof api.context>[0], "bad")).rejects.toThrow("Latitude is invalid or missing. Check this field and try again. As-of date and time is invalid or missing.");
    expect(diagnostics).toHaveBeenCalledWith("API validation failed", expect.objectContaining({ status: 422 }));
  });

  it("does not expose arbitrary server detail", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500, json: async () => ({ detail: "stack trace with private data" }) }));
    vi.spyOn(console, "warn").mockImplementation(() => undefined);
    await expect(api.locations("Mumbai")).rejects.toThrow("The service is temporarily unavailable. Please try again.");
  });
});
