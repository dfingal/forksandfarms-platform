import type { OpeningHoursDay, OpeningHoursRange } from "./types";

// Matches core.models.OpeningHours.Weekday (Monday=0..Sunday=6) — the
// order the API's opening_hours array already comes in.
export const WEEKDAY_ORDER = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
] as const;

/** "7:00" -> "7 AM", "13:30" -> "1:30 PM". Minutes are omitted on the hour. */
export function formatClockTime(hhmm: string): string {
  const [hStr, mStr] = hhmm.split(":");
  const hours = Number(hStr);
  const minutes = Number(mStr);
  const period = hours < 12 ? "AM" : "PM";
  const hours12 = hours % 12 === 0 ? 12 : hours % 12;
  return minutes === 0 ? `${hours12} ${period}` : `${hours12}:${String(minutes).padStart(2, "0")} ${period}`;
}

/** Joins one day's ranges into "7 AM – 7 PM" / "11 AM – 2 PM, 5 PM – 9 PM".
 * An overnight range (close earlier than open) is shown as-is, e.g.
 * "6 PM – 2 AM" — no "(next day)" marker; out of scope for Phase I. */
export function formatDayRanges(ranges: OpeningHoursRange[]): string {
  return ranges.map((r) => `${formatClockTime(r.open)} – ${formatClockTime(r.close)}`).join(", ");
}

/** True if at least one day has been given real data (closed or has
 * hours) — i.e. this isn't still all 7 unset placeholder rows. */
export function hasAnySetHours(days: OpeningHoursDay[]): boolean {
  return days.some((d) => d.is_closed || d.ranges.length > 0);
}

/**
 * Which weekday (0=Monday..6=Sunday, matching WEEKDAY_ORDER/the API) is
 * "today" in the given IANA timezone, for a given instant. Takes `now`
 * explicitly rather than reading the clock itself so it's a pure,
 * easily-testable function — callers pass `new Date()`.
 *
 * Returns -1 if `timezone` isn't a timezone Intl recognizes (shouldn't
 * happen for a city saved through the admin, which validates it, but
 * never crash the page over a bad value) — callers should treat -1 as
 * "don't highlight anything".
 */
export function todayWeekdayIndex(timezone: string, now: Date): number {
  try {
    const weekdayName = new Intl.DateTimeFormat("en-US", {
      timeZone: timezone,
      weekday: "long",
    }).format(now);
    return WEEKDAY_ORDER.indexOf(weekdayName as (typeof WEEKDAY_ORDER)[number]);
  } catch {
    return -1;
  }
}
