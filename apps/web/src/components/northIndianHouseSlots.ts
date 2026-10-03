type Slot = { x: number; y: number };

// These are visual slots only. The keys are one-based Whole Sign house numbers
// from the API; sign values must never select a visual slot.
export const northIndianHouseSlots: Record<number, Slot> = {
  1: { x: 200, y: 66 }, 2: { x: 95, y: 72 }, 3: { x: 38, y: 145 },
  4: { x: 83, y: 218 }, 5: { x: 200, y: 350 }, 6: { x: 305, y: 336 },
  7: { x: 362, y: 255 }, 8: { x: 362, y: 145 }, 9: { x: 306, y: 72 },
  10: { x: 200, y: 151 }, 11: { x: 200, y: 255 }, 12: { x: 92, y: 336 },
};
