"use client";

import { useSyncExternalStore } from "react";
import { todayWeekdayIndex } from "@/lib/openingHours";

// "Current date/time" isn't a subscribable store in any real sense, but
// useSyncExternalStore is still the right tool here: it's the one hook
// that lets a value differ between the server-rendered snapshot and the
// client's first paint without a hydration-mismatch warning or a
// setState-in-effect render cascade (same reasoning as ThanksContent's
// sessionStorage read). getServerSnapshot returns -1 (nothing
// highlighted), matching the client's own pre-hydration paint.
function subscribe() {
  return () => {};
}

function getServerSnapshot() {
  return -1;
}

interface TodayWeekdayStyleProps {
  timezone: string;
}

/** Tiny client component: computes which weekday row is "today" in the
 * city's timezone and injects a scoped CSS rule to bold it. The table
 * itself (OpeningHoursTable) is a plain server component — this is the
 * only client-computed piece, by design (ISR-cached pages can be stale
 * by the time a visitor loads them; "today" must always be correct for
 * the actual visitor, not whenever the page was last regenerated). */
export default function TodayWeekdayStyle({ timezone }: TodayWeekdayStyleProps) {
  const todayIndex = useSyncExternalStore(
    subscribe,
    () => todayWeekdayIndex(timezone, new Date()),
    getServerSnapshot
  );

  if (todayIndex < 0) return null;

  return (
    <style>{`.opening-hours-table [data-weekday="${todayIndex}"] { font-weight: 700; color: var(--color-forest); }`}</style>
  );
}
