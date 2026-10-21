import { describe, expect, it } from "vitest";
import { resolveWallTime, validateBirth } from "./birthValidation";
import type { BirthValues } from "./birthValidation";

const valid: BirthValues = {
  display_name: "", birth_date: "1990-01-15", birth_time: "09:30", place_query: "Mumbai",
  timezone: "Asia/Kolkata", latitude: "19.076", longitude: "72.8777",
  as_of_date: "2026-10-02", as_of_time: "12:00", as_of_timezone: "Asia/Kolkata",
};

describe("birth and as-of validation", () => {
  it("accepts valid manual details and an offset-bearing as-of instant", () => {
    expect(validateBirth(valid)).toEqual({ errors: {}, asOf: "2026-10-02T12:00:00+05:30" });
  });
  it("reports every required missing field", () => {
    const result = validateBirth({ ...valid, birth_date: "", birth_time: "", place_query: "", timezone: "", latitude: "", longitude: "", as_of_timezone: "" });
    expect(Object.keys(result.errors)).toEqual(expect.arrayContaining(["birth_date", "birth_time", "place_query", "timezone", "latitude", "longitude", "as_of_timezone"]));
    expect(result.asOf).toBeUndefined();
  });
  it("rejects invalid calendar dates, times, coordinates, and IANA identifiers", () => {
    const result = validateBirth({ ...valid, birth_date: "2025-02-29", birth_time: "24:00", latitude: "91", longitude: "-181", timezone: "Invalid/Zone", as_of_date: "2026-02-30", as_of_time: "25:00", as_of_timezone: "Invalid/Zone" });
    expect(Object.keys(result.errors)).toEqual(expect.arrayContaining(["birth_date", "birth_time", "latitude", "longitude", "timezone", "as_of_date", "as_of_time", "as_of_timezone"]));
    expect(validateBirth({ ...valid, birth_date: "0000-01-01", as_of_timezone: "+05:30" }).errors).toMatchObject({ birth_date: expect.any(String), as_of_timezone: expect.any(String) });
  });
  it("rejects both ambiguous and nonexistent birth and as-of wall times", () => {
    for (const [date, time, word] of [["2025-03-09", "02:30", "does not exist"], ["2025-11-02", "01:30", "occurs twice"]]) {
      const result = validateBirth({ ...valid, birth_date: date, birth_time: time, timezone: "America/New_York", as_of_date: date, as_of_time: time, as_of_timezone: "America/New_York" });
      expect(result.errors.birth_time).toContain(word);
      expect(result.errors.as_of_time).toContain(word);
    }
  });
  it("uses the offset at the actual as-of instant on both sides of DST", () => {
    expect(resolveWallTime("2025-03-09", "01:30", "America/New_York").instant).toBe("2025-03-09T01:30:00-05:00");
    expect(resolveWallTime("2025-03-09", "03:30", "America/New_York").instant).toBe("2025-03-09T03:30:00-04:00");
    expect(resolveWallTime("2025-11-02", "00:30", "America/New_York").instant).toBe("2025-11-02T00:30:00-04:00");
    expect(resolveWallTime("2025-11-02", "02:30", "America/New_York").instant).toBe("2025-11-02T02:30:00-05:00");
  });
});
