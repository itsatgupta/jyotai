export type BirthValues = {
  display_name: string; birth_date: string; birth_time: string; place_query: string;
  timezone: string; latitude: string; longitude: string;
  as_of_date: string; as_of_time: string; as_of_timezone: string;
};
export type BirthErrors = Partial<Record<keyof BirthValues, string>>;

function validDate(value: string): boolean {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) return false;
  const [, year, month, day] = match.map(Number);
  const date = new Date(0);
  date.setUTCFullYear(year, month - 1, day);
  return year >= 1 && date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

function validTime(value: string): boolean { return /^([01]\d|2[0-3]):[0-5]\d$/.test(value); }

function validZone(value: string): boolean {
  if (!/^[A-Za-z_]+(?:\/[A-Za-z0-9_+-]+)*$/.test(value)) return false;
  try { new Intl.DateTimeFormat("en-US", { timeZone: value }).format(); return Boolean(value.trim()); }
  catch { return false; }
}

function offsetMinutes(zone: string, instant: number): number {
  const parts = new Intl.DateTimeFormat("en-US", { timeZone: zone, timeZoneName: "longOffset" }).formatToParts(instant);
  const label = parts.find((part) => part.type === "timeZoneName")?.value;
  const match = /^GMT(?:([+-])(\d{1,2})(?::(\d{2}))?)?$/.exec(label ?? "");
  if (!match) throw new Error("Unable to resolve the selected timezone.");
  return match[1] ? (match[1] === "+" ? 1 : -1) * (Number(match[2]) * 60 + Number(match[3] ?? 0)) : 0;
}

export function resolveWallTime(date: string, time: string, zone: string): { instant: string; error?: never } | { error: string; instant?: never } {
  if (!validDate(date) || !validTime(time) || !validZone(zone)) return { error: "Enter a valid date, time, and IANA timezone." };
  const wall = Date.parse(`${date}T${time}:00Z`);
  const offsets = new Set<number>();
  for (let hours = -48; hours <= 48; hours += 6) offsets.add(offsetMinutes(zone, wall + hours * 3_600_000));
  const matches = [...offsets].map((offset) => ({ offset, instant: wall - offset * 60_000 }))
    .filter(({ offset, instant }) => offsetMinutes(zone, instant) === offset);
  if (!matches.length) return { error: "This local time does not exist in the selected timezone. Choose another time." };
  if (matches.length > 1) return { error: "This local time occurs twice in the selected timezone. Choose an unambiguous time." };
  const { offset } = matches[0];
  const sign = offset >= 0 ? "+" : "-";
  const absolute = Math.abs(offset);
  return { instant: `${date}T${time}:00${sign}${String(Math.floor(absolute / 60)).padStart(2, "0")}:${String(absolute % 60).padStart(2, "0")}` };
}

export function validateBirth(values: BirthValues): { errors: BirthErrors; asOf?: string } {
  const errors: BirthErrors = {};
  if (!values.birth_date) errors.birth_date = "Enter your birth date.";
  else if (!validDate(values.birth_date)) errors.birth_date = "Enter a valid calendar date.";
  if (!values.birth_time) errors.birth_time = "Enter your birth time.";
  else if (!validTime(values.birth_time)) errors.birth_time = "Enter a valid time in 24-hour format.";
  if (!values.place_query.trim()) errors.place_query = "Enter a birthplace or select a search result.";
  if (!values.timezone.trim()) errors.timezone = "Enter the birthplace's IANA timezone, such as Asia/Kolkata.";
  else if (!validZone(values.timezone.trim())) errors.timezone = "Enter a valid IANA timezone, such as Asia/Kolkata.";
  for (const [field, limit] of [["latitude", 90], ["longitude", 180]] as const) {
    const input = values[field].trim();
    if (!input) errors[field] = `Enter ${field}.`;
    else if (!Number.isFinite(Number(input)) || Math.abs(Number(input)) > limit) errors[field] = `Enter ${field} between -${limit} and ${limit}.`;
  }
  if (!errors.birth_date && !errors.birth_time && !errors.timezone) {
    const resolved = resolveWallTime(values.birth_date, values.birth_time, values.timezone.trim());
    if (resolved.error) errors.birth_time = resolved.error;
  }
  if (!values.as_of_date) errors.as_of_date = "Enter an as-of date.";
  else if (!validDate(values.as_of_date)) errors.as_of_date = "Enter a valid as-of calendar date.";
  if (!values.as_of_time) errors.as_of_time = "Enter an as-of time.";
  else if (!validTime(values.as_of_time)) errors.as_of_time = "Enter a valid as-of time.";
  if (!values.as_of_timezone.trim()) errors.as_of_timezone = "Enter an as-of IANA timezone.";
  else if (!validZone(values.as_of_timezone.trim())) errors.as_of_timezone = "Enter a valid as-of IANA timezone.";
  let asOf: string | undefined;
  if (!errors.as_of_date && !errors.as_of_time && !errors.as_of_timezone) {
    const resolved = resolveWallTime(values.as_of_date, values.as_of_time, values.as_of_timezone.trim());
    if (resolved.error) errors.as_of_time = resolved.error;
    else asOf = resolved.instant;
  }
  return { errors, asOf };
}
