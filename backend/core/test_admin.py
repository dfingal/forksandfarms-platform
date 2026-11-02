"""
Tests for the admin-only coordinate handling: widened precision,
RoundedDecimalField, the "paste coordinates" mixin, and the Venue
admin's "View on Google Maps" link.

See core/tests.py for make_city/make_venue helpers, reused here.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .admin import CityAdminForm, VenueAdminForm
from .models import City, Venue
from .tests import make_city, make_venue


class CoordinatePrecisionModelTests(TestCase):
    """The widened fields actually store 7 decimal places, not just 6."""

    def test_venue_latitude_longitude_round_trip_7_decimals(self):
        city = make_city()
        venue = make_venue(
            city,
            latitude=Decimal("38.6270123"),
            longitude=Decimal("-90.1994123"),
        )
        venue.refresh_from_db()
        self.assertEqual(venue.latitude, Decimal("38.6270123"))
        self.assertEqual(venue.longitude, Decimal("-90.1994123"))

    def test_city_map_center_round_trips_7_decimals(self):
        city = make_city(
            map_center_lat=Decimal("38.6270123"),
            map_center_lng=Decimal("-90.1994123"),
        )
        city.refresh_from_db()
        self.assertEqual(city.map_center_lat, Decimal("38.6270123"))
        self.assertEqual(city.map_center_lng, Decimal("-90.1994123"))


def venue_form_data(city, **overrides):
    """Minimal valid POST data for VenueAdminForm, all required fields."""
    data = {
        "city": city.pk,
        "name": "Test Venue",
        "slug": "test-venue",
        "neighborhood": "Downtown",
        "venue_type": Venue.VenueType.COFFEE_SHOP,
        "status": Venue.Status.ACTIVE,
        "partner_tier": Venue.PartnerTier.RETAIL_SHELF,
        "display_order": 0,
        "address_line1": "123 Main St",
        "address_line2": "",
        "postal_code": "63101",
        "paste_coordinates": "",
        "latitude": "38.600000",
        "longitude": "-90.200000",
        "hours": "{}",
        "website_url": "",
        "instagram_handle": "",
        "short_description": "A test venue.",
        "setup_description": "Setup details.",
        "square_location_id": "",
        # VenuePhoto inline management form, required even with 0 photos.
        "photos-TOTAL_FORMS": "0",
        "photos-INITIAL_FORMS": "0",
        "photos-MIN_NUM_FORMS": "0",
        "photos-MAX_NUM_FORMS": "1000",
    }
    data.update(overrides)
    return data


class RoundedDecimalFieldTests(TestCase):
    """Direct entry of more than 7 decimal places is rounded, not rejected."""

    def test_extra_decimal_places_rounds_instead_of_rejecting(self):
        city = make_city()
        form = VenueAdminForm(
            data=venue_form_data(
                city, latitude="38.12345678", longitude="-90.98765432"
            )
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["latitude"], Decimal("38.1234568"))
        self.assertEqual(form.cleaned_data["longitude"], Decimal("-90.9876543"))


class CoordinatePasteTests(TestCase):
    """VenueAdminForm's paste_coordinates field, tolerant parsing included."""

    def setUp(self):
        self.city = make_city()

    def test_valid_paste_fills_both_fields(self):
        form = VenueAdminForm(
            data=venue_form_data(
                self.city, latitude="", longitude="", paste_coordinates="38.6270, -90.1994"
            )
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["latitude"], Decimal("38.6270000"))
        self.assertEqual(form.cleaned_data["longitude"], Decimal("-90.1994000"))

    def test_paste_rounds_extra_decimal_places(self):
        form = VenueAdminForm(
            data=venue_form_data(
                self.city,
                latitude="",
                longitude="",
                paste_coordinates="38.62701234567, -90.19941234567",
            )
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["latitude"], Decimal("38.6270123"))
        self.assertEqual(form.cleaned_data["longitude"], Decimal("-90.1994123"))

    def test_paste_tolerates_no_space_after_comma(self):
        form = VenueAdminForm(
            data=venue_form_data(
                self.city, latitude="", longitude="", paste_coordinates="38.6270,-90.1994"
            )
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["latitude"], Decimal("38.6270000"))

    def test_paste_tolerates_surrounding_whitespace_and_parens(self):
        form = VenueAdminForm(
            data=venue_form_data(
                self.city,
                latitude="",
                longitude="",
                paste_coordinates="  ( 38.6270 ,  -90.1994 )  ",
            )
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["latitude"], Decimal("38.6270000"))
        self.assertEqual(form.cleaned_data["longitude"], Decimal("-90.1994000"))

    def test_malformed_paste_errors_on_paste_field(self):
        form = VenueAdminForm(
            data=venue_form_data(
                self.city, latitude="", longitude="", paste_coordinates="not coordinates"
            )
        )
        self.assertFalse(form.is_valid())
        self.assertIn("paste_coordinates", form.errors)

    def test_latitude_out_of_range_errors(self):
        form = VenueAdminForm(
            data=venue_form_data(
                self.city, latitude="", longitude="", paste_coordinates="95.0, -90.1994"
            )
        )
        self.assertFalse(form.is_valid())
        self.assertIn("paste_coordinates", form.errors)
        self.assertIn("Latitude", form.errors["paste_coordinates"][0])

    def test_longitude_out_of_range_errors(self):
        form = VenueAdminForm(
            data=venue_form_data(
                self.city, latitude="", longitude="", paste_coordinates="38.6270, -190.0"
            )
        )
        self.assertFalse(form.is_valid())
        self.assertIn("paste_coordinates", form.errors)
        self.assertIn("Longitude", form.errors["paste_coordinates"][0])

    def test_paste_overrides_manually_typed_values(self):
        form = VenueAdminForm(
            data=venue_form_data(
                self.city,
                latitude="1.000000",
                longitude="2.000000",
                paste_coordinates="38.6270, -90.1994",
            )
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["latitude"], Decimal("38.6270000"))
        self.assertEqual(form.cleaned_data["longitude"], Decimal("-90.1994000"))

    def test_no_paste_and_no_direct_entry_is_required_error(self):
        form = VenueAdminForm(
            data=venue_form_data(self.city, latitude="", longitude="", paste_coordinates="")
        )
        self.assertFalse(form.is_valid())
        self.assertIn("latitude", form.errors)
        self.assertIn("longitude", form.errors)

    def test_direct_entry_without_paste_still_works(self):
        """Regression: normal manual entry, unchanged from before this feature."""
        form = VenueAdminForm(
            data=venue_form_data(self.city, latitude="38.600000", longitude="-90.200000")
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["latitude"], Decimal("38.6000000"))
        self.assertEqual(form.cleaned_data["longitude"], Decimal("-90.2000000"))


def city_form_data(**overrides):
    data = {
        "name": "St. Louis",
        "slug": "st-louis",
        "state": "MO",
        "intro": "",
        "is_active": True,
        "paste_coordinates": "",
        "map_center_lat": "38.627000",
        "map_center_lng": "-90.199400",
        "map_zoom": 12,
    }
    data.update(overrides)
    return data


class CityCoordinatePasteTests(TestCase):
    """Same mixin, applied to City — proves it generalizes beyond Venue."""

    def test_valid_paste_fills_both_fields(self):
        form = CityAdminForm(
            data=city_form_data(
                map_center_lat="", map_center_lng="", paste_coordinates="38.6270, -90.1994"
            )
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["map_center_lat"], Decimal("38.6270000"))
        self.assertEqual(form.cleaned_data["map_center_lng"], Decimal("-90.1994000"))

    def test_malformed_paste_errors(self):
        form = CityAdminForm(
            data=city_form_data(
                map_center_lat="", map_center_lng="", paste_coordinates="nope"
            )
        )
        self.assertFalse(form.is_valid())
        self.assertIn("paste_coordinates", form.errors)


class VenueAdminViewTests(TestCase):
    """End-to-end: posting to the real Venue admin add view, not just the
    form in isolation — proves this works through Django admin itself."""

    def setUp(self):
        self.city = make_city()
        self.superuser = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.client.force_login(self.superuser)

    def test_add_venue_via_paste_coordinates(self):
        url = reverse("admin:core_venue_add")
        response = self.client.post(
            url,
            venue_form_data(
                self.city,
                slug="paste-test-venue",
                latitude="",
                longitude="",
                paste_coordinates="38.62701234567, -90.19941234567",
            ),
        )
        if response.status_code == 200:
            self.fail(f"Form errors: {response.context['adminform'].errors}")
        self.assertEqual(response.status_code, 302)
        venue = Venue.objects.get(slug="paste-test-venue")
        self.assertEqual(venue.latitude, Decimal("38.6270123"))
        self.assertEqual(venue.longitude, Decimal("-90.1994123"))

    def test_google_maps_link_shown_on_change_page(self):
        venue = make_venue(self.city, slug="maps-link-venue")
        # The admin view re-fetches from the DB, which pads to the field's
        # full 7 decimal places — refresh so the expected string matches.
        venue.refresh_from_db()
        url = reverse("admin:core_venue_change", args=[venue.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View on Google Maps")
        self.assertContains(response, f"q={venue.latitude},{venue.longitude}")

    def test_google_maps_link_not_shown_on_add_page(self):
        url = reverse("admin:core_venue_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "save first")
