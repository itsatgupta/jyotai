import { useEffect, useId, useRef, useState } from "react";

import { api } from "../lib/api";
import type { BirthInput, LocationSuggestion } from "../lib/contracts";

type Props = { onSubmit: (birth: BirthInput, asOf: string) => Promise<void>; loading: boolean };
type Values = { display_name: string; birth_date: string; birth_time: string; place_query: string; timezone: string; latitude: string; longitude: string; as_of_date: string; as_of_time: string; as_of_timezone: string };
const browserZone = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";

export function BirthProfile({ onSubmit, loading }: Props) {
  const listId = useId();
  const [values, setValues] = useState<Values>(() => currentValues());
  const [selected, setSelected] = useState<LocationSuggestion | null>(null);
  const [results, setResults] = useState<LocationSuggestion[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [error, setError] = useState("");
  const [activeIndex, setActiveIndex] = useState(-1);
  const abortRef = useRef<AbortController | null>(null);
  const change = (key: keyof Values, value: string) => setValues((current) => ({ ...current, [key]: value }));

  useEffect(() => {
    const query = values.place_query.trim();
    abortRef.current?.abort();
    if (query.length < 3 || selected?.display_name === values.place_query) { setResults([]); setSearching(false); setSearchError(""); return; }
    const controller = new AbortController(); abortRef.current = controller;
    const timer = window.setTimeout(() => {
      setSearching(true); setSearchError("");
      api.locations(query, controller.signal).then(({ results: suggestions }) => { setResults(suggestions); setActiveIndex(-1); }).catch((reason: unknown) => {
        if (!(reason instanceof DOMException && reason.name === "AbortError")) setSearchError(message(reason));
      }).finally(() => { if (!controller.signal.aborted) setSearching(false); });
    }, 280);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [values.place_query, selected?.display_name]);

  function selectLocation(location: LocationSuggestion) {
    setSelected(location); setResults([]); setActiveIndex(-1); setSearchError("");
    setValues((current) => ({ ...current, place_query: location.display_name, timezone: location.timezone, latitude: String(location.latitude), longitude: String(location.longitude) }));
  }
  function onPlaceKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (!results.length) return;
    if (event.key === "ArrowDown") { event.preventDefault(); setActiveIndex((index) => Math.min(index + 1, results.length - 1)); }
    if (event.key === "ArrowUp") { event.preventDefault(); setActiveIndex((index) => Math.max(index - 1, 0)); }
    if (event.key === "Enter" && activeIndex >= 0) { event.preventDefault(); selectLocation(results[activeIndex]); }
    if (event.key === "Escape") setResults([]);
  }
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const manualValid = values.place_query.trim() && values.timezone.trim() && values.latitude !== "" && values.longitude !== "";
    if (!values.birth_date || !values.birth_time || (!selected && !manualValid)) { setError("Choose a birthplace from the list, or enter valid location details in Advanced location details."); return; }
    setError("");
    await onSubmit({ display_name: values.display_name || null, place_name: values.place_query.trim() || null, birth_date: values.birth_date, birth_time: `${values.birth_time}:00`, timezone: values.timezone.trim(), latitude: Number(values.latitude), longitude: Number(values.longitude) }, advancedAsOf(values) ?? localRfc3339(new Date()));
  }
  return <section className="birth-section" id="birth-profile" aria-labelledby="birth-profile-heading">
    <div className="section-intro"><span className="eyebrow">Birth profile</span><h2 id="birth-profile-heading">Begin with the details only you know.</h2><p>Your birthplace resolves the precise coordinates and timezone used by the deterministic chart engine.</p></div>
    <form className="birth-card" onSubmit={submit} noValidate>
      <div className="form-grid consumer-grid">
        <Field label="Name" value={values.display_name} onChange={(value) => change("display_name", value)} optional placeholder="How should we address you?" />
        <Field label="Date of Birth" type="date" value={values.birth_date} onChange={(value) => change("birth_date", value)} required />
        <Field label="Time of Birth" type="time" value={values.birth_time} onChange={(value) => change("birth_time", value)} required />
        <label className="place-field"><span>Place of Birth <b aria-hidden="true">*</b></span><div className="autocomplete-wrap"><input aria-autocomplete="list" aria-controls={listId} aria-expanded={results.length > 0} autoComplete="off" value={values.place_query} onChange={(event) => { change("place_query", event.target.value); setSelected(null); }} onKeyDown={onPlaceKeyDown} placeholder="Search city, town, or address" required />{searching && <span className="field-status">Finding places…</span>}{results.length > 0 && <ul id={listId} className="location-results" role="listbox" aria-label="Birthplace suggestions">{results.map((location, index) => <li key={`${location.provider_id}-${location.display_name}`} role="option" aria-selected={activeIndex === index}><button type="button" onMouseDown={(event) => event.preventDefault()} onClick={() => selectLocation(location)}><span>{location.display_name}</span><small>{location.timezone}</small></button></li>)}</ul>}</div>{selected && <span className="location-confirmation">✓ Selected: {selected.display_name}</span>}{searchError && <span className="form-error" role="alert">{searchError} You can enter location details manually below.</span>}</label>
      </div>
      <p className="privacy-note">Location search is provided by Geoapify. It receives your place query only, not your full birth profile. <a href="https://www.geoapify.com/" target="_blank" rel="noreferrer">Powered by Geoapify</a></p>
      <details className="advanced-details"><summary>Advanced location details</summary><p>Use these fields to review a selected location or enter a manual fallback. JyotAI validates the IANA timezone and coordinates server-side.</p><div className="form-grid advanced-grid"><Field label="Selected timezone" value={values.timezone} onChange={(value) => change("timezone", value)} placeholder="Asia/Kolkata" /><Field label="Latitude" type="number" value={values.latitude} onChange={(value) => change("latitude", value)} placeholder="28.4595" /><Field label="Longitude" type="number" value={values.longitude} onChange={(value) => change("longitude", value)} placeholder="77.0266" /><Field label="As-of date" type="date" value={values.as_of_date} onChange={(value) => change("as_of_date", value)} /><Field label="As-of time" type="time" value={values.as_of_time} onChange={(value) => change("as_of_time", value)} /><Field label="As-of timezone" value={values.as_of_timezone} onChange={(value) => change("as_of_timezone", value)} placeholder="Asia/Kolkata" /></div></details>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="button primary" disabled={loading} type="submit">{loading ? "Creating your chart…" : "Create My Horoscope"}</button>
    </form>
  </section>;
}
function Field({ label, optional, ...props }: { label: string; optional?: boolean; value: string; onChange: (value: string) => void; type?: string; placeholder?: string; required?: boolean }) { return <label><span>{label}{optional && <em>Optional</em>}</span><input {...props} onChange={(event) => props.onChange(event.target.value)} /></label>; }
function currentValues(): Values { const now = new Date(); return { display_name: "", birth_date: "", birth_time: "", place_query: "", timezone: "", latitude: "", longitude: "", as_of_date: localDate(now), as_of_time: localTime(now), as_of_timezone: browserZone }; }
function localDate(value: Date) { return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`; }
function localTime(value: Date) { return `${String(value.getHours()).padStart(2, "0")}:${String(value.getMinutes()).padStart(2, "0")}`; }
function localRfc3339(value: Date) { const offset = -value.getTimezoneOffset(); const sign = offset >= 0 ? "+" : "-"; const hours = String(Math.floor(Math.abs(offset) / 60)).padStart(2, "0"); const minutes = String(Math.abs(offset) % 60).padStart(2, "0"); return `${localDate(value)}T${String(value.getHours()).padStart(2, "0")}:${String(value.getMinutes()).padStart(2, "0")}:${String(value.getSeconds()).padStart(2, "0")}${sign}${hours}:${minutes}`; }
function advancedAsOf(values: Values) { if (!values.as_of_date || !values.as_of_time || !values.as_of_timezone) return null; try { const sample = new Date(`${values.as_of_date}T${values.as_of_time}:00Z`); const offset = new Intl.DateTimeFormat("en", { timeZone: values.as_of_timezone, timeZoneName: "longOffset" }).formatToParts(sample).find((part) => part.type === "timeZoneName")?.value.replace("GMT", "") || "Z"; return `${values.as_of_date}T${values.as_of_time}:00${offset}`; } catch { return null; } }
function message(reason: unknown) { return reason instanceof Error ? reason.message : "Location search is temporarily unavailable."; }
