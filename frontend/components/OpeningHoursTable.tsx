import { formatDayRanges, hasAnySetHours } from "@/lib/openingHours";
import type { OpeningHoursDay } from "@/lib/types";
import TodayWeekdayStyle from "./TodayWeekdayStyle";

interface OpeningHoursTableProps {
  // Optional/nullable: the API field this comes from can lag behind a
  // frontend deploy that already expects it (see lib/types.ts) — must
  // degrade to the "coming soon" fallback below, never throw.
  days: OpeningHoursDay[] | null | undefined;
  timezone: string;
}

// Plain server component — all the real content (day names, open/closed
// state, formatted ranges) renders here, server-side. Only the "which
// row is today" bolding is deferred to TodayWeekdayStyle (client).
export default function OpeningHoursTable({ days, timezone }: OpeningHoursTableProps) {
  if (!hasAnySetHours(days)) {
    return <p className="text-sm text-forest/60">Hours coming soon.</p>;
  }

  return (
    <div className="opening-hours-table">
      <TodayWeekdayStyle timezone={timezone} />
      <table className="w-full text-sm">
        <tbody>
          {(days ?? []).map((day, i) => (
            <tr key={day.day} data-weekday={i} className="text-forest/80">
              <td className="w-28 py-0.5 pr-4">{day.day}</td>
              <td className="py-0.5">
                {day.is_closed
                  ? "Closed"
                  : day.ranges.length > 0
                    ? formatDayRanges(day.ranges)
                    : "Hours not set"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
