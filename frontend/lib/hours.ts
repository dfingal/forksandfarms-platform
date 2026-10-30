// Venue.hours (spec §4.2) can be either a single free-text display string
// ({"display": "Mon–Fri 7–6 · Sat–Sun 8–4"}) or per-day keys
// ({"mon": "7:00–18:00", ...}). This normalizes either shape into lines
// ready to render.

const DAY_LABELS: Record<string, string> = {
  mon: "Mon",
  tue: "Tue",
  wed: "Wed",
  thu: "Thu",
  fri: "Fri",
  sat: "Sat",
  sun: "Sun",
};
const DAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];

export function formatHours(hours: Record<string, string> | null | undefined): string[] {
  if (!hours) return [];

  if (hours.display) {
    return [hours.display];
  }

  return DAY_ORDER.filter((day) => hours[day]).map((day) => `${DAY_LABELS[day]}: ${hours[day]}`);
}
