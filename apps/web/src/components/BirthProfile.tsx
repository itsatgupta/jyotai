import { useEffect, useId, useRef, useState } from "react";

import { api } from "../lib/api";
import { validateBirth } from "../lib/birthValidation";
import type { BirthErrors, BirthValues } from "../lib/birthValidation";
import type { BirthInput, LocationSuggestion } from "../lib/contracts";

type Props = { onSubmit: (birth: BirthInput, asOf: string) => Promise<void>; loading: boolean; initialBirth?: BirthInput; initialAsOf?: string };
const browserZone = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";

export function BirthProfile({ onSubmit, loading, initialBirth, initialAsOf }: Props) {
  const listId = useId();
  const [values, setValues] = useState<BirthValues>(() => currentValues(initialBirth, initialAsOf));
  const [errors, setErrors] = useState<BirthErrors>({});
  const [selected, setSelected] = useState<LocationSuggestion | null>(null);
  const [results, setResults] = useState<LocationSuggestion[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [activeIndex, setActiveIndex] = useState(-1);
  const abortRef = useRef<AbortController | null>(null);
  const change = (key: keyof BirthValues, value: string) => { setValues((current) => ({ ...current, [key]: value })); setErrors((current) => ({ ...current, [key]: undefined })); };

  useEffect(() => {
    const query = values.place_query.trim();
    abortRef.current?.abort();
    if (query.length < 3 || selected?.display_name === values.place_query) { setResults([]); setSearching(false); setSearchError(""); return; }
    const controller = new AbortController(); abortRef.current = controller;
    const timer = window.setTimeout(() => {
      setSearching(true); setSearchError("");
      api.locations(query, controller.signal).then(({ results: suggestions }) => { if (controller.signal.aborted) return; setResults(suggestions); setActiveIndex(-1); setSearchError(suggestions.length ? "" : "no-results"); }).catch((reason: unknown) => {
        if (!controller.signal.aborted && !(reason instanceof DOMException && reason.name === "AbortError")) setSearchError("unavailable");
      }).finally(() => { if (!controller.signal.aborted) setSearching(false); });
    }, 280);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [values.place_query, selected?.display_name]);

  function selectLocation(location: LocationSuggestion) {
    setSelected(location); setResults([]); setActiveIndex(-1); setSearchError("");
    setValues((current) => ({ ...current, place_query: location.display_name, timezone: location.timezone, latitude: String(location.latitude), longitude: String(location.longitude) }));
    setErrors((current) => ({ ...current, place_query: undefined, timezone: undefined, latitude: undefined, longitude: undefined }));
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
    const validation = validateBirth(values);
    setErrors(validation.errors);
    if (Object.keys(validation.errors).length || !validation.asOf) return;
    await onSubmit({ display_name: values.display_name || null, place_name: values.place_query.trim(), birth_date: values.birth_date, birth_time: `${values.birth_time}:00`, timezone: values.timezone.trim(), latitude: Number(values.latitude), longitude: Number(values.longitude) }, validation.asOf);
  }
  return <section className="birth-section" id="birth-profile" aria-labelledby="birth-profile-heading">
    <div className="section-intro"><span className="eyebrow">Birth profile</span><h2 id="birth-profile-heading">Begin with the details only you know.</h2><p>Your birthplace resolves the precise coordinates and timezone used by the deterministic chart engine.</p><p>Consultations stay in this open page. If you refreshed or lost a previous consultation, enter your details to start a new one.</p></div>
    <form className="birth-card" onSubmit={submit} noValidate>
      <div className="form-grid consumer-grid">
        <Field label="Name" value={values.display_name} onChange={(value) => change("display_name", value)} optional placeholder="How should we address you?" />
        <Field label="Date of Birth" type="date" value={values.birth_date} onChange={(value) => change("birth_date", value)} error={errors.birth_date} required />
        <Field label="Time of Birth" type="time" value={values.birth_time} onChange={(value) => change("birth_time", value)} error={errors.birth_time} required />
        <label className="place-field"><span>Place of Birth <b aria-hidden="true">*</b></span><div className="autocomplete-wrap"><input aria-autocomplete="list" aria-controls={listId} aria-expanded={results.length > 0} aria-invalid={Boolean(errors.place_query)} autoComplete="off" value={values.place_query} onChange={(event) => { change("place_query", event.target.value); if (selected) { setValues((current) => ({ ...current, timezone: "", latitude: "", longitude: "" })); setSelected(null); } }} onKeyDown={onPlaceKeyDown} placeholder="Search city, town, or address" required />{searching && <span className="field-status">Finding places…</span>}{results.length > 0 && <ul id={listId} className="location-results" role="listbox" aria-label="Birthplace suggestions">{results.map((location, index) => <li key={`${location.provider_id}-${location.display_name}`} role="option" aria-selected={activeIndex === index}><button type="button" onMouseDown={(event) => event.preventDefault()} onClick={() => selectLocation(location)}><span>{location.display_name}</span><small>{location.timezone}</small></button></li>)}</ul>}</div>{errors.place_query && <span className="form-error" role="alert">{errors.place_query}</span>}{selected && <span className="location-confirmation">✓ Selected: {selected.display_name}</span>}{searchError && <span className="form-error" role="alert">{searchError === "no-results" ? "No matching places found. Enter timezone and coordinates in Advanced location details." : "Location search is unavailable. Enter timezone and coordinates in Advanced location details."}</span>}</label>
      </div>
      <p className="privacy-note">Location search is provided by Geoapify. It receives your place query only, not your full birth profile. <a href="https://www.geoapify.com/" target="_blank" rel="noreferrer">Powered by Geoapify</a></p>
      <details className="advanced-details" open={Object.keys(errors).some((key) => ["timezone", "latitude", "longitude", "as_of_date", "as_of_time", "as_of_timezone"].includes(key)) || undefined}><summary>Advanced location details</summary><p>Review a selected location or enter a manual fallback. Use an IANA timezone such as Asia/Kolkata.</p><div className="form-grid advanced-grid"><Field label="Selected timezone" value={values.timezone} onChange={(value) => change("timezone", value)} error={errors.timezone} placeholder="Asia/Kolkata" /><Field label="Latitude" type="number" value={values.latitude} onChange={(value) => change("latitude", value)} error={errors.latitude} placeholder="28.4595" /><Field label="Longitude" type="number" value={values.longitude} onChange={(value) => change("longitude", value)} error={errors.longitude} placeholder="77.0266" /><Field label="As-of date" type="date" value={values.as_of_date} onChange={(value) => change("as_of_date", value)} error={errors.as_of_date} /><Field label="As-of time" type="time" value={values.as_of_time} onChange={(value) => change("as_of_time", value)} error={errors.as_of_time} /><Field label="As-of timezone" value={values.as_of_timezone} onChange={(value) => change("as_of_timezone", value)} error={errors.as_of_timezone} placeholder="Asia/Kolkata" /></div></details>
      <button className="button primary" disabled={loading} type="submit">{loading ? "Creating your chart…" : "Create My Horoscope"}</button>
    </form>
  </section>;
}
function Field({ label, optional, error, ...props }: { label: string; optional?: boolean; error?: string; value: string; onChange: (value: string) => void; type?: string; placeholder?: string; required?: boolean }) { return <label><span>{label}{optional && <em>Optional</em>}</span><input {...props} aria-invalid={Boolean(error)} onChange={(event) => props.onChange(event.target.value)} />{error && <span className="form-error" role="alert">{error}</span>}</label>; }
function currentValues(birth?: BirthInput, asOf?: string): BirthValues { const instant = asOf ? new Date(asOf) : new Date(); const now = Number.isFinite(instant.getTime()) ? instant : new Date(); return { display_name: birth?.display_name ?? "", birth_date: birth?.birth_date ?? "", birth_time: birth?.birth_time.slice(0, 5) ?? "", place_query: birth?.place_name ?? "", timezone: birth?.timezone ?? "", latitude: birth ? String(birth.latitude) : "", longitude: birth ? String(birth.longitude) : "", as_of_date: localDate(now), as_of_time: localTime(now), as_of_timezone: browserZone }; }
function localDate(value: Date) { return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`; }
function localTime(value: Date) { return `${String(value.getHours()).padStart(2, "0")}:${String(value.getMinutes()).padStart(2, "0")}`; }
