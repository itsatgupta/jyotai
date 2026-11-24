import type { Planet } from "./contracts";

export const titleCase = (value: string) =>
  value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

/** The server's DD°MM′ degree when supplied (D1), else the decimal degree to two places. */
export const formatDegree = (value: { degree_in_sign: string | number; degree_in_sign_dms?: string | null }) =>
  value.degree_in_sign_dms ?? `${Number(value.degree_in_sign).toFixed(2)}°`;

/** "Rohini · Pada 2" from a calculated nakshatra placement. */
export const formatNakshatra = (nakshatra: { nakshatra: string; pada: number } | undefined) =>
  nakshatra ? `${titleCase(nakshatra.nakshatra)} · Pada ${nakshatra.pada}` : "—";

/** Calculated facts only: sign, degree, nakshatra and pada, house, motion. */
export const planetCardSummary = (planet: Planet) =>
  `${titleCase(planet.body)} · ${titleCase(planet.sign)} ${formatDegree(planet)} · ${formatNakshatra(planet.nakshatra)} · House ${planet.house_number}${planet.retrograde ? " · Retrograde" : ""}`;
