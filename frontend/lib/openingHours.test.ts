import { describe, expect, it } from "vitest";
import {
  formatClockTime,
  formatDayRanges,
  hasAnySetHours,
  todayWeekdayIndex,
  WEEKDAY_ORDER,
} from "./openingHours";
import type { OpeningHoursDay } from "./types";

describe("formatClockTime", () => {
  it("drops the minutes on the hour", () => {
    expect(formatClockTime("7:00")).toBe("7 AM");
    expect(formatClockTime("19:00")).toBe("7 PM");
  });

  it("keeps minutes when not on the hour", () => {
    expect(formatClockTime("13:30")).toBe("1:30 PM");
    expect(formatClockTime("7:05")).toBe("7:05 AM");
  });

  it("handles midnight and noon", () => {
    expect(formatClockTime("00:00")).toBe("12 AM");
    expect(formatClockTime("12:00")).toBe("12 PM");
  });
});

describe("formatDayRanges", () => {
  it("formats a single range", () => {
    expect(formatDayRanges([{ open: "07:00", close: "19:00" }])).toBe("7 AM – 7 PM");
  });

  it("joins split-hours ranges with a comma", () => {
    expect(
      formatDayRanges([
        { open: "11:00", close: "14:00" },
        { open: "17:00", close: "21:00" },
      ])
    ).toBe("11 AM – 2 PM, 5 PM – 9 PM");
  });

  it("shows an overnight range (close before open) as plain times, no marker", () => {
    expect(formatDayRanges([{ open: "18:00", close: "02:00" }])).toBe("6 PM – 2 AM");
  });

  it("returns an empty string for no ranges", () => {
    expect(formatDayRanges([])).toBe("");
  });
});

function day(overrides: Partial<OpeningHoursDay> = {}): OpeningHoursDay {
  return { day: "Monday", is_closed: false, ranges: [], ...overrides };
}

describe("hasAnySetHours", () => {
  it("is false when every day is unset", () => {
    expect(hasAnySetHours(WEEKDAY_ORDER.map((name) => day({ day: name })))).toBe(false);
  });

  it("is true when at least one day is explicitly closed", () => {
    const days = WEEKDAY_ORDER.map((name) => day({ day: name }));
    days[0] = day({ day: "Monday", is_closed: true });
    expect(hasAnySetHours(days)).toBe(true);
  });

  it("is true when at least one day has ranges", () => {
    const days = WEEKDAY_ORDER.map((name) => day({ day: name }));
    days[0] = day({ day: "Monday", ranges: [{ open: "07:00", close: "19:00" }] });
    expect(hasAnySetHours(days)).toBe(true);
  });

  it("is false (not a crash) when opening_hours is missing from the API response", () => {
    // Exactly what happened against the live preview API before it had
    // shipped this field: VenueDetail.opening_hours was simply absent.
    expect(hasAnySetHours(undefined)).toBe(false);
  });

  it("is false (not a crash) when opening_hours is explicitly null", () => {
    expect(hasAnySetHours(null)).toBe(false);
  });
});

describe("todayWeekdayIndex", () => {
  it("resolves a known instant to the right weekday index in a given timezone", () => {
    // 2026-11-02 is a Monday. Noon UTC is still Monday morning in
    // America/Chicago (UTC-6 in November, standard time).
    const monday = new Date("2026-11-02T12:00:00Z");
    expect(todayWeekdayIndex("America/Chicago", monday)).toBe(0); // Monday
  });

  it("crosses a day boundary correctly near midnight UTC", () => {
    // 2026-11-02T04:00:00Z is still 2026-11-01 (Sunday) 22:00 in Chicago.
    const lateSunday = new Date("2026-11-02T04:00:00Z");
    expect(todayWeekdayIndex("America/Chicago", lateSunday)).toBe(6); // Sunday
  });

  it("returns -1 for an unrecognized timezone instead of throwing", () => {
    expect(todayWeekdayIndex("Not/A_Real_Zone", new Date())).toBe(-1);
  });

  it("agrees with WEEKDAY_ORDER's index convention (Monday=0)", () => {
    const sunday = new Date("2026-11-08T12:00:00Z"); // a Sunday
    const index = todayWeekdayIndex("America/Chicago", sunday);
    expect(WEEKDAY_ORDER[index]).toBe("Sunday");
  });
});
