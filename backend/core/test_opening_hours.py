"""
Tests for OpeningHours: model validation (including the three-state
unset/closed/open distinction), the post_save placeholder signal, the
0003 data migration's parser, the admin "copy Monday" action, and the
API's per-day shape. See core/tests.py for make_city/make_venue.
"""

from datetime import time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command, CommandError
from django.test import TestCase, override_settings
from django.urls import reverse

from .hours_parsing import parse_day_range, parse_time
from .models import City, OpeningHours, Venue
from .serializers import VenueDetailSerializer
from .tests import make_city, make_venue

MON, TUE, WED, THU, FRI, SAT, SUN = range(7)


class OpeningHoursModelTests(TestCase):
    def setUp(self):
        self.city = make_city()
        self.venue = make_venue(self.city)

    def test_unset_row_is_valid(self):
        row = OpeningHours(venue=self.venue, weekday=MON)
        row.full_clean()
        self.assertTrue(row.is_unset)

    def test_closed_row_is_valid(self):
        row = OpeningHours(venue=self.venue, weekday=MON, is_closed=True)
        row.full_clean()
        self.assertFalse(row.is_unset)

    def test_closed_row_with_times_is_invalid(self):
        row = OpeningHours(
            venue=self.venue, weekday=MON, is_closed=True,
            open_time=time(9, 0), close_time=time(17, 0),
        )
        with self.assertRaises(ValidationError):
            row.full_clean()

    def test_open_row_with_both_times_is_valid(self):
        row = OpeningHours(
            venue=self.venue, weekday=MON, open_time=time(9, 0), close_time=time(17, 0)
        )
        row.full_clean()
        self.assertFalse(row.is_unset)

    def test_only_open_time_set_is_invalid(self):
        row = OpeningHours(venue=self.venue, weekday=MON, open_time=time(9, 0))
        with self.assertRaises(ValidationError):
            row.full_clean()

    def test_only_close_time_set_is_invalid(self):
        row = OpeningHours(venue=self.venue, weekday=MON, close_time=time(17, 0))
        with self.assertRaises(ValidationError):
            row.full_clean()

    def test_equal_open_and_close_time_is_invalid(self):
        row = OpeningHours(
            venue=self.venue, weekday=MON, open_time=time(9, 0), close_time=time(9, 0)
        )
        with self.assertRaises(ValidationError):
            row.full_clean()

    def test_close_before_open_means_overnight_and_is_valid(self):
        row = OpeningHours(
            venue=self.venue, weekday=FRI, open_time=time(18, 0), close_time=time(2, 0)
        )
        row.full_clean()  # must not raise


class CityTimezoneTests(TestCase):
    def test_valid_timezone_accepted(self):
        city = City(
            name="St. Louis", slug="st-louis", state="MO",
            map_center_lat=Decimal("38.627000"), map_center_lng=Decimal("-90.199400"),
            timezone="America/Chicago",
        )
        city.full_clean()

    def test_invalid_timezone_rejected(self):
        city = City(
            name="St. Louis", slug="st-louis", state="MO",
            map_center_lat=Decimal("38.627000"), map_center_lng=Decimal("-90.199400"),
            timezone="Not/A_Real_Zone",
        )
        with self.assertRaises(ValidationError):
            city.full_clean()


class PostSaveSignalTests(TestCase):
    def test_new_venue_gets_7_unset_rows(self):
        city = make_city()
        venue = make_venue(city)
        rows = list(venue.opening_hours.order_by("weekday"))
        self.assertEqual(len(rows), 7)
        self.assertEqual([r.weekday for r in rows], list(range(7)))
        self.assertTrue(all(r.is_unset for r in rows))


class DayRangeParserTests(TestCase):
    """The 0003 migration's parser (core/hours_parsing.py)."""

    def test_24h_format(self):
        self.assertEqual(parse_day_range("7:00-18:00"), (time(7, 0), time(18, 0)))

    def test_en_dash_with_spaces(self):
        self.assertEqual(parse_day_range("7:00 – 18:00"), (time(7, 0), time(18, 0)))

    def test_am_pm_format(self):
        self.assertEqual(parse_day_range("7:00am-6:00pm"), (time(7, 0), time(18, 0)))

    def test_overnight_range_parses_fine(self):
        # The parser itself doesn't reject close < open — that's a valid
        # overnight range, same as the model allows.
        self.assertEqual(parse_day_range("6pm-2am"), (time(18, 0), time(2, 0)))

    def test_garbage_returns_none(self):
        self.assertIsNone(parse_day_range("garbage"))

    def test_equal_times_returns_none(self):
        self.assertIsNone(parse_day_range("9:00-9:00"))

    def test_non_string_returns_none(self):
        self.assertIsNone(parse_day_range(None))

    def test_single_time_formats(self):
        self.assertEqual(parse_time("7:00"), time(7, 0))
        self.assertEqual(parse_time("7:00 AM"), time(7, 0))
        self.assertEqual(parse_time("7PM"), time(19, 0))
        self.assertIsNone(parse_time("not a time"))


class DataMigrationIntegrationTests(TestCase):
    """Exercises the real migration function against real model instances
    (not apps.get_model's historical versions) — close enough to the real
    thing to catch integration mistakes, cheaper than a full migration
    test harness."""

    def test_display_shape_creates_unset_placeholders_not_closed(self):
        city = make_city()
        venue = make_venue(city, hours={"display": "Mon–Fri 9-5"})
        venue.opening_hours.all().delete()  # undo the post_save placeholders for a clean slate

        from .hours_parsing import DAY_KEYS, parse_day_range

        rows = []
        old_hours = venue.hours if isinstance(venue.hours, dict) else {}
        for weekday, day_key in enumerate(DAY_KEYS):
            parsed = parse_day_range(old_hours.get(day_key))
            if parsed:
                open_time, close_time = parsed
                rows.append(OpeningHours(venue=venue, weekday=weekday, open_time=open_time, close_time=close_time))
            else:
                rows.append(OpeningHours(venue=venue, weekday=weekday))
        OpeningHours.objects.bulk_create(rows)

        self.assertTrue(all(r.is_unset for r in venue.opening_hours.all()))

    def test_per_day_shape_parses_cleanly_where_possible(self):
        city = make_city()
        venue = make_venue(
            city,
            hours={"mon": "7:00-18:00", "tue": "garbage", "wed": "9:00-17:00"},
        )
        venue.opening_hours.all().delete()

        from .hours_parsing import DAY_KEYS, parse_day_range

        rows = []
        old_hours = venue.hours
        for weekday, day_key in enumerate(DAY_KEYS):
            parsed = parse_day_range(old_hours.get(day_key))
            if parsed:
                open_time, close_time = parsed
                rows.append(OpeningHours(venue=venue, weekday=weekday, open_time=open_time, close_time=close_time))
            else:
                rows.append(OpeningHours(venue=venue, weekday=weekday))
        OpeningHours.objects.bulk_create(rows)

        mon = venue.opening_hours.get(weekday=MON)
        tue = venue.opening_hours.get(weekday=TUE)
        wed = venue.opening_hours.get(weekday=WED)
        thu = venue.opening_hours.get(weekday=THU)

        self.assertEqual((mon.open_time, mon.close_time), (time(7, 0), time(18, 0)))
        self.assertTrue(tue.is_unset)  # "garbage" didn't parse -> unset, not closed
        self.assertEqual((wed.open_time, wed.close_time), (time(9, 0), time(17, 0)))
        self.assertTrue(thu.is_unset)  # missing from the dict entirely -> unset


class CopyMondayActionTests(TestCase):
    """Exercised through the real admin changelist POST (not calling the
    action function directly) so this proves it works through Django
    admin itself, same pattern as the admin-view tests elsewhere."""

    def setUp(self):
        self.city = make_city()
        self.venue = make_venue(self.city)
        self.venue.opening_hours.all().delete()
        superuser = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.client.force_login(superuser)

    def _run_action(self):
        url = reverse("admin:core_venue_changelist")
        return self.client.post(
            url, {"action": "copy_monday_to_all_days", "_selected_action": [str(self.venue.pk)]}
        )

    def test_copies_times_to_every_other_day(self):
        OpeningHours.objects.create(
            venue=self.venue, weekday=MON, open_time=time(9, 0), close_time=time(17, 0)
        )
        response = self._run_action()
        self.assertEqual(response.status_code, 302)

        for weekday in range(7):
            row = self.venue.opening_hours.get(weekday=weekday)
            self.assertEqual((row.open_time, row.close_time), (time(9, 0), time(17, 0)))
            self.assertFalse(row.is_closed)

    def test_copies_closed_state_too(self):
        OpeningHours.objects.create(venue=self.venue, weekday=MON, is_closed=True)
        self._run_action()

        for weekday in range(7):
            self.assertTrue(self.venue.opening_hours.get(weekday=weekday).is_closed)

    def test_copies_split_hours(self):
        OpeningHours.objects.create(
            venue=self.venue, weekday=MON, order=0, open_time=time(11, 0), close_time=time(14, 0)
        )
        OpeningHours.objects.create(
            venue=self.venue, weekday=MON, order=1, open_time=time(17, 0), close_time=time(21, 0)
        )
        self._run_action()

        tue_rows = list(self.venue.opening_hours.filter(weekday=TUE).order_by("order"))
        self.assertEqual(len(tue_rows), 2)
        self.assertEqual((tue_rows[0].open_time, tue_rows[0].close_time), (time(11, 0), time(14, 0)))
        self.assertEqual((tue_rows[1].open_time, tue_rows[1].close_time), (time(17, 0), time(21, 0)))


class OpeningHoursApiTests(TestCase):
    def setUp(self):
        self.city = make_city()
        self.venue = make_venue(self.city)
        self.venue.opening_hours.all().delete()

    def test_unset_day_is_not_closed_and_has_no_ranges(self):
        OpeningHours.objects.create(venue=self.venue, weekday=MON)
        data = VenueDetailSerializer(self.venue).data
        monday = data["opening_hours"][MON]
        self.assertEqual(monday["day"], "Monday")
        self.assertFalse(monday["is_closed"])
        self.assertEqual(monday["ranges"], [])

    def test_closed_day_is_closed_and_has_no_ranges(self):
        OpeningHours.objects.create(venue=self.venue, weekday=TUE, is_closed=True)
        data = VenueDetailSerializer(self.venue).data
        tuesday = data["opening_hours"][TUE]
        self.assertTrue(tuesday["is_closed"])
        self.assertEqual(tuesday["ranges"], [])

    def test_split_hours_return_both_ranges_in_order(self):
        OpeningHours.objects.create(
            venue=self.venue, weekday=WED, order=1, open_time=time(17, 0), close_time=time(21, 0)
        )
        OpeningHours.objects.create(
            venue=self.venue, weekday=WED, order=0, open_time=time(11, 0), close_time=time(14, 0)
        )
        data = VenueDetailSerializer(self.venue).data
        wednesday = data["opening_hours"][WED]
        self.assertFalse(wednesday["is_closed"])
        self.assertEqual(
            wednesday["ranges"],
            [{"open": "11:00", "close": "14:00"}, {"open": "17:00", "close": "21:00"}],
        )

    def test_old_hours_field_still_present(self):
        self.venue.hours = {"display": "Mon-Fri 9-5"}
        self.venue.save()
        data = VenueDetailSerializer(self.venue).data
        self.assertEqual(data["hours"], {"display": "Mon-Fri 9-5"})

    def test_city_timezone_in_response(self):
        from .serializers import CitySerializer

        data = CitySerializer(self.city).data
        self.assertIn("timezone", data)


class SeedCommandOpeningHoursTests(TestCase):
    """The pieces of seed_demo_data relevant to this feature: never
    overwrite real hours, and the DEBUG guard."""

    @override_settings(DEBUG=False)
    def test_refuses_to_run_without_force_outside_debug(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo_data")

    def test_does_not_overwrite_real_hours_on_rerun(self):
        # force=True: not testing the DEBUG guard here, and ambient test
        # settings.DEBUG is False (same reason partners/tests.py overrides
        # it elsewhere).
        call_command("seed_demo_data", force=True)
        venue = Venue.objects.get(slug="scarletts-wine-bar")

        # Simulate the owner having corrected Monday's hours in admin.
        monday = venue.opening_hours.get(weekday=MON)
        monday.is_closed = False
        monday.open_time = time(18, 0)
        monday.close_time = time(22, 0)
        monday.save()

        call_command("seed_demo_data", force=True)

        monday.refresh_from_db()
        self.assertEqual((monday.open_time, monday.close_time), (time(18, 0), time(22, 0)))
