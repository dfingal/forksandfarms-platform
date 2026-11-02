"""
Best-effort parsing of the old free-text/per-day Venue.hours shape into
real (open, close) times. Used by the 0003 data migration; pulled out
into its own module (rather than living inline in the migration file)
so it's a normal importable, testable unit.
"""

import re
from datetime import datetime

DAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]  # index == Weekday value (Monday=0)

_TIME_FORMATS = ["%H:%M", "%I:%M%p", "%I:%M %p", "%I%p", "%I %p"]

# Splits "7:00-18:00", "7:00 – 18:00", "7:00am-6:00pm" etc. on the dash
# (hyphen, en dash, or em dash) separating the two times.
_RANGE_SPLIT_RE = re.compile(r"\s*[-–—]\s*")


def parse_time(raw):
    """Best-effort parse of one clock time string. Returns a time, or
    None if it doesn't match any of the formats we try."""
    raw = raw.strip().upper().replace(".", "")
    for fmt in _TIME_FORMATS:
        try:
            return datetime.strptime(raw, fmt).time()
        except ValueError:
            continue
    return None


def parse_day_range(raw):
    """Parse one day's "open-close" string into (open, close) times.
    Returns None if it doesn't parse cleanly — callers should fall back
    to leaving that day unset rather than guessing."""
    if not isinstance(raw, str):
        return None
    parts = _RANGE_SPLIT_RE.split(raw.strip(), maxsplit=1)
    if len(parts) != 2:
        return None
    open_time = parse_time(parts[0])
    close_time = parse_time(parts[1])
    if open_time is None or close_time is None or open_time == close_time:
        return None
    return open_time, close_time
