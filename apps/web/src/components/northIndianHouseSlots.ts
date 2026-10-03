type Anchor = { x: number; y: number };

export type NorthIndianHouseSlot = {
  signAnchor: Anchor;
  planetAnchor: Anchor;
};

// The SVG's side-midpoint diamond is split into the four kendra regions by
// diagonals running from each corner to the chart center. The other eight
// regions are the surrounding corner triangles. These keys are fixed,
// one-based house numbers; signs are content rendered inside the fixed slot.
export const northIndianHouseSlots: Record<number, NorthIndianHouseSlot> = {
  1: { signAnchor: { x: 200, y: 58 }, planetAnchor: { x: 200, y: 135 } },
  2: { signAnchor: { x: 95, y: 28 }, planetAnchor: { x: 100, y: 61 } },
  3: { signAnchor: { x: 28, y: 90 }, planetAnchor: { x: 48, y: 130 } },
  4: { signAnchor: { x: 50, y: 200 }, planetAnchor: { x: 125, y: 200 } },
  5: { signAnchor: { x: 28, y: 270 }, planetAnchor: { x: 45, y: 310 } },
  6: { signAnchor: { x: 100, y: 354 }, planetAnchor: { x: 105, y: 335 } },
  7: { signAnchor: { x: 200, y: 350 }, planetAnchor: { x: 200, y: 260 } },
  8: { signAnchor: { x: 300, y: 354 }, planetAnchor: { x: 295, y: 335 } },
  9: { signAnchor: { x: 372, y: 270 }, planetAnchor: { x: 350, y: 310 } },
  10: { signAnchor: { x: 350, y: 200 }, planetAnchor: { x: 275, y: 200 } },
  11: { signAnchor: { x: 372, y: 90 }, planetAnchor: { x: 350, y: 130 } },
  12: { signAnchor: { x: 300, y: 28 }, planetAnchor: { x: 300, y: 61 } },
};

const zodiacSigns = [
  "aries", "taurus", "gemini", "cancer", "leo", "virgo",
  "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
] as const;

export function zodiacSignNumber(sign: string): number {
  const index = zodiacSigns.indexOf(sign as (typeof zodiacSigns)[number]);
  if (index === -1) throw new Error(`Unsupported zodiac sign: ${sign}`);
  return index + 1;
}
