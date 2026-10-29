from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import City, Venue


def make_city(**kwargs):
    defaults = {
        "name": "St. Louis",
        "slug": "st-louis",
        "state": "MO",
        "map_center_lat": Decimal("38.627000"),
        "map_center_lng": Decimal("-90.199400"),
    }
    defaults.update(kwargs)
    return City.objects.create(**defaults)


def make_venue(city, **kwargs):
    defaults = {
        "city": city,
        "name": "Test Venue",
        "slug": "test-venue",
        "neighborhood": "Downtown",
        "venue_type": Venue.VenueType.COFFEE_SHOP,
        "status": Venue.Status.ACTIVE,
        "partner_tier": Venue.PartnerTier.RETAIL_SHELF,
        "address_line1": "123 Main St",
        "postal_code": "63101",
        "latitude": Decimal("38.600000"),
        "longitude": Decimal("-90.200000"),
        "short_description": "A test venue.",
        "setup_description": "Setup details.",
        "square_location_id": "sq-loc-secret-123",
    }
    defaults.update(kwargs)
    return Venue.objects.create(**defaults)


class VenuePublicFilteringTests(TestCase):
    """Only active/seasonal/coming_soon venues in active cities are public."""

    def setUp(self):
        self.city = make_city()
        self.active = make_venue(self.city, slug="active-venue", status=Venue.Status.ACTIVE)
        self.seasonal = make_venue(self.city, slug="seasonal-venue", status=Venue.Status.SEASONAL)
        self.coming_soon = make_venue(self.city, slug="coming-soon-venue", status=Venue.Status.COMING_SOON)
        self.paused = make_venue(self.city, slug="paused-venue", status=Venue.Status.PAUSED)

    def _slugs(self, response):
        return {item["slug"] for item in response.json()}

    def test_venue_list_excludes_paused(self):
        response = self.client.get(reverse("venue-list"))
        self.assertEqual(response.status_code, 200)
        slugs = self._slugs(response)
        self.assertIn("active-venue", slugs)
        self.assertIn("seasonal-venue", slugs)
        self.assertIn("coming-soon-venue", slugs)
        self.assertNotIn("paused-venue", slugs)

    def test_venue_list_filtered_by_city(self):
        other_city = make_city(name="Other City", slug="other-city")
        make_venue(other_city, slug="other-city-venue", status=Venue.Status.ACTIVE)

        response = self.client.get(reverse("venue-list"), {"city": "st-louis"})
        slugs = self._slugs(response)
        self.assertNotIn("other-city-venue", slugs)
        self.assertIn("active-venue", slugs)

    def test_venue_list_excludes_inactive_city(self):
        inactive_city = make_city(name="Inactive City", slug="inactive-city", is_active=False)
        make_venue(inactive_city, slug="venue-in-inactive-city", status=Venue.Status.ACTIVE)

        response = self.client.get(reverse("venue-list"))
        self.assertNotIn("venue-in-inactive-city", self._slugs(response))

    def test_paused_venue_detail_is_404(self):
        url = reverse("venue-detail", kwargs={"city_slug": "st-louis", "venue_slug": "paused-venue"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_venue_in_inactive_city_detail_is_404(self):
        inactive_city = make_city(name="Inactive City", slug="inactive-city", is_active=False)
        make_venue(inactive_city, slug="hidden-venue", status=Venue.Status.ACTIVE)

        url = reverse("venue-detail", kwargs={"city_slug": "inactive-city", "venue_slug": "hidden-venue"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_active_venue_detail_is_200(self):
        url = reverse("venue-detail", kwargs={"city_slug": "st-louis", "venue_slug": "active-venue"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["slug"], "active-venue")

    def test_city_detail_only_lists_public_venues(self):
        url = reverse("city-detail", kwargs={"city_slug": "st-louis"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        slugs = {v["slug"] for v in response.json()["venues"]}
        self.assertIn("active-venue", slugs)
        self.assertNotIn("paused-venue", slugs)

    def test_city_detail_404_for_unknown_slug(self):
        url = reverse("city-detail", kwargs={"city_slug": "nowhere"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_city_detail_404_for_inactive_city(self):
        make_city(name="Inactive City", slug="inactive-city", is_active=False)
        url = reverse("city-detail", kwargs={"city_slug": "inactive-city"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class VenueHiddenFieldsTests(TestCase):
    """partner_tier and square_location_id must never appear in public JSON."""

    def setUp(self):
        self.city = make_city()
        self.venue = make_venue(self.city)

    def test_venue_list_omits_hidden_fields(self):
        response = self.client.get(reverse("venue-list"))
        body = response.json()
        self.assertTrue(len(body) >= 1)
        for item in body:
            self.assertNotIn("partner_tier", item)
            self.assertNotIn("square_location_id", item)

    def test_venue_detail_omits_hidden_fields(self):
        url = reverse(
            "venue-detail", kwargs={"city_slug": self.city.slug, "venue_slug": self.venue.slug}
        )
        response = self.client.get(url)
        body = response.json()
        self.assertNotIn("partner_tier", body)
        self.assertNotIn("square_location_id", body)

    def test_city_detail_nested_venues_omit_hidden_fields(self):
        url = reverse("city-detail", kwargs={"city_slug": self.city.slug})
        response = self.client.get(url)
        for item in response.json()["venues"]:
            self.assertNotIn("partner_tier", item)
            self.assertNotIn("square_location_id", item)
