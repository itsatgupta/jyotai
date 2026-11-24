import { describe, expect, it } from "vitest";

import { PROVISIONAL_STORAGE_KEY, PROVISIONAL_TOGGLE_LABEL, readShowProvisional, writeShowProvisional } from "./provisional";

function memory() {
  const values = new Map<string, string>();
  return { getItem: (key: string) => values.get(key) ?? null, setItem: (key: string, value: string) => { values.set(key, value); }, values };
}

describe("provisional preference", () => {
  it("is off by default and remembered per browser", () => {
    const storage = memory();
    expect(PROVISIONAL_TOGGLE_LABEL).toBe("Show provisional interpretations (beta)");
    expect(readShowProvisional(storage)).toBe(false);
    writeShowProvisional(true, storage);
    expect(storage.values.get(PROVISIONAL_STORAGE_KEY)).toBe("on");
    expect(readShowProvisional(storage)).toBe(true);
    writeShowProvisional(false, storage);
    expect(readShowProvisional(storage)).toBe(false);
  });

  it("stays off when storage is unavailable", () => {
    const broken = { getItem: () => { throw new Error("blocked"); }, setItem: () => { throw new Error("blocked"); } };
    expect(readShowProvisional(broken)).toBe(false);
    expect(() => writeShowProvisional(true, broken)).not.toThrow();
    expect(readShowProvisional(undefined)).toBe(false);
  });
});
