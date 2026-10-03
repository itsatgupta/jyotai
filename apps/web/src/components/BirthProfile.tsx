import { useState } from "react";

import type { BirthInput } from "../lib/contracts";

type Props = { onSubmit: (birth: BirthInput, asOf: string) => Promise<void>; loading: boolean };

const browserZone = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";

export function BirthProfile({ onSubmit, loading }: Props) {
  const [values, setValues] = useState({
    display_name: "",
    place_name: "",
    birth_date: "",
    birth_time: "",
    timezone: browserZone,
    latitude: "",
    longitude: "",
    as_of_date: new Date().toISOString().slice(0, 10),
    as_of_time: new Date().toTimeString().slice(0, 5),
    as_of_timezone: browserZone,
  });
  const [error, setError] = useState("");
  const change = (key: keyof typeof values, value: string) => setValues((current) => ({ ...current, [key]: value }));

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!values.birth_date || !values.birth_time || !values.timezone || !values.latitude || !values.longitude) {
      setError("Birth date, exact time, timezone, latitude, and longitude are required.");
      return;
    }
    const asOf = `${values.as_of_date}T${values.as_of_time}:00${timezoneOffset(values.as_of_timezone)}`;
    if (!values.as_of_date || !values.as_of_time || !values.as_of_timezone || asOf.endsWith("NaN")) {
      setError("Provide an explicit as-of date, time, and valid IANA timezone.");
      return;
    }
    setError("");
    await onSubmit(
      {
        display_name: values.display_name || null,
        place_name: values.place_name || null,
        birth_date: values.birth_date,
        birth_time: `${values.birth_time}:00`,
        timezone: values.timezone,
        latitude: Number(values.latitude),
        longitude: Number(values.longitude),
      },
      asOf,
    );
  }

  return <section className="profile-card" aria-labelledby="birth-profile-heading">
    <div className="eyebrow">Birth profile</div><h1 id="birth-profile-heading">Your deterministic astrology profile</h1>
    <p className="muted">Use exact coordinates and an IANA timezone. Place labels are for your reference only.</p>
    <form onSubmit={submit} noValidate>
      <div className="form-grid">
        <Field label="Display name" value={values.display_name} onChange={(v) => change("display_name", v)} optional />
        <Field label="Place label" value={values.place_name} onChange={(v) => change("place_name", v)} optional placeholder="e.g. Mumbai" />
        <Field label="Birth date" type="date" value={values.birth_date} onChange={(v) => change("birth_date", v)} required />
        <Field label="Exact birth time" type="time" value={values.birth_time} onChange={(v) => change("birth_time", v)} required />
        <Field label="Birth timezone" value={values.timezone} onChange={(v) => change("timezone", v)} placeholder="Asia/Kolkata" required />
        <Field label="Latitude" type="number" value={values.latitude} onChange={(v) => change("latitude", v)} placeholder="19.076" required />
        <Field label="Longitude" type="number" value={values.longitude} onChange={(v) => change("longitude", v)} placeholder="72.8777" required />
        <Field label="As of date" type="date" value={values.as_of_date} onChange={(v) => change("as_of_date", v)} required />
        <Field label="As of time" type="time" value={values.as_of_time} onChange={(v) => change("as_of_time", v)} required />
        <Field label="As of timezone" value={values.as_of_timezone} onChange={(v) => change("as_of_timezone", v)} placeholder="Asia/Kolkata" required />
      </div>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="button primary" disabled={loading} type="submit">{loading ? "Generating…" : "Generate Astrology Profile"}</button>
    </form>
  </section>;
}

function Field({ label, optional, ...props }: { label: string; optional?: boolean; value: string; onChange: (value: string) => void; type?: string; placeholder?: string; required?: boolean }) {
  return <label><span>{label}{optional && <em>Optional</em>}</span><input {...props} onChange={(event) => props.onChange(event.target.value)} /></label>;
}

function timezoneOffset(zone: string): string {
  try {
    const parts = new Intl.DateTimeFormat("en", { timeZone: zone, timeZoneName: "longOffset" }).formatToParts(new Date());
    return parts.find((part) => part.type === "timeZoneName")?.value.replace("GMT", "") || "Z";
  } catch { return "NaN"; }
}
