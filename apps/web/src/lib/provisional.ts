// NEXT-PROVISIONAL-01: the "Show provisional interpretations (beta)" preference, per browser.
export const PROVISIONAL_STORAGE_KEY = "jyotai-show-provisional";
export const PROVISIONAL_TOGGLE_LABEL = "Show provisional interpretations (beta)";

export function readShowProvisional(storage: Pick<Storage, "getItem"> | undefined = globalThis.localStorage): boolean {
  try { return storage?.getItem(PROVISIONAL_STORAGE_KEY) === "on"; }
  catch { return false; }
}

export function writeShowProvisional(value: boolean, storage: Pick<Storage, "setItem"> | undefined = globalThis.localStorage): void {
  try { storage?.setItem(PROVISIONAL_STORAGE_KEY, value ? "on" : "off"); }
  catch { /* Storage may be unavailable. */ }
}
