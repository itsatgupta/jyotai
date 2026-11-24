import { describe, expect, it } from "vitest";
import { formatDegree, formatNakshatra, planetCardSummary } from "./format";

describe("degree display (NEXT-FIX-DEG-01)", () => {
  it("uses the server's DD°MM′ value verbatim, never re-rounding it", () => {
    expect(formatDegree({ degree_in_sign: "29.99999", degree_in_sign_dms: "29°59′" })).toBe("29°59′");
    expect(formatDegree({ degree_in_sign: 0, degree_in_sign_dms: "00°00′" })).toBe("00°00′");
  });
  it("falls back to the decimal degree where no DD°MM′ is supplied (D9/D10, transits)", () => {
    expect(formatDegree({ degree_in_sign: "12.3456" })).toBe("12.35°");
    expect(formatDegree({ degree_in_sign: 3, degree_in_sign_dms: null })).toBe("3.00°");
  });
  it("formats nakshatra and pada, with a dash when absent", () => {
    expect(formatNakshatra({ nakshatra: "purva_bhadrapada", pada: 4 })).toBe("Purva Bhadrapada · Pada 4");
    expect(formatNakshatra(undefined)).toBe("—");
  });
  it("summarises a card with calculated facts only", () => {
    const base = { body: "ketu", sign: "libra", degree_in_sign: 0, degree_in_sign_dms: "00°00′", house_number: 7, nakshatra: { nakshatra: "chitra", pada: 3 } };
    expect(planetCardSummary({ ...base, retrograde: true })).toBe("Ketu · Libra 00°00′ · Chitra · Pada 3 · House 7 · Retrograde");
    expect(planetCardSummary({ ...base, retrograde: false })).toBe("Ketu · Libra 00°00′ · Chitra · Pada 3 · House 7");
  });
});
