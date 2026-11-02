"""
Data migration: give every existing Venue its 7 baseline OpeningHours
rows (the post_save signal only covers venues created from now on).

Where the old Venue.hours field has the per-day shape
({"mon": "7:00-18:00", ...}) and a day's value parses cleanly, that
day's row is created with real open/close times. Everything else
(the free-text {"display": "..."} shape, a day missing from the dict,
or a value that doesn't parse) gets an UNSET placeholder row — NOT a
closed one. "We don't know this venue's hours yet" and "this venue is
closed that day" must never be conflated; only parsed-and-confirmed
closed days (there's no way to express "closed" in the old free-text
format, so in practice this migration only ever produces open-or-unset
rows, never closed ones — closing a day is left for the admin).

Venue.hours itself is left untouched — see models.py's TODO on that
field about a later release dropping it once nothing still reads it.
"""

from django.db import migrations

from core.hours_parsing import DAY_KEYS, parse_day_range


def populate_opening_hours(apps, schema_editor):
    Venue = apps.get_model("core", "Venue")
    OpeningHours = apps.get_model("core", "OpeningHours")

    rows = []
    for venue in Venue.objects.all():
        old_hours = venue.hours if isinstance(venue.hours, dict) else {}
        for weekday, day_key in enumerate(DAY_KEYS):
            raw = old_hours.get(day_key)
            parsed = parse_day_range(raw)
            if parsed:
                open_time, close_time = parsed
                rows.append(
                    OpeningHours(
                        venue=venue, weekday=weekday, is_closed=False,
                        open_time=open_time, close_time=close_time,
                    )
                )
            else:
                # Doesn't parse cleanly (or wasn't there, e.g. the
                # {"display": "..."} shape) -> unset, not closed.
                rows.append(OpeningHours(venue=venue, weekday=weekday))

    OpeningHours.objects.bulk_create(rows)


def remove_opening_hours(apps, schema_editor):
    # Reverse: this migration is the only thing that creates OpeningHours
    # in bulk for pre-existing venues, so undoing it means removing all
    # rows it (and the post_save signal, for venues created in the
    # meantime) would have produced. Safe to just clear the table.
    OpeningHours = apps.get_model("core", "OpeningHours")
    OpeningHours.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_city_timezone_openinghours"),
    ]

    operations = [
        migrations.RunPython(populate_opening_hours, remove_opening_hours),
    ]
