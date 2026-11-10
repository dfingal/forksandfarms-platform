"""
Tests for admin-editable SEO metadata (core/seo.py, docs/seo-plan.md):
fallbacks, overrides, noindex, the public `seo` object, target_phrases
never leaking, the admin SEO section, and live-site refresh on SEO edits.

Image fields are only given file *names* here (nothing is uploaded), and
media storage is forced to local disk so no test ever talks to
Cloudinary even if backend/.env sets CLOUDINARY_URL.
"""

from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from . import revalidation
from .seo import truncate_at_word
from .tests import make_city, make_venue

LOCAL_MEDIA = {
    "STORAGES": {
        **settings.STORAGES,
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    },
    "MEDIA_URL": "/media/",
}

# The revalidation signals fire on every save in these tests; keep them off.
NO_REVALIDATION = {"FRONTEND_REVALIDATE_URL": "", "REVALIDATE_SECRET": ""}


class TruncateAtWordTests(TestCase):
    def test_short_text_unchanged(self):
        self.assertEqual(truncate_at_word("Ferns and figs.", 160), "Ferns and figs.")

    def test_cuts_at_word_boundary_with_ellipsis(self):
        result = truncate_at_word("one two three four", 12)
        self.assertEqual(result, "one two…")
        self.assertLessEqual(len(result), 12)

    def test_never_exceeds_limit(self):
        text = "word " * 100
        self.assertLessEqual(len(truncate_at_word(text, 160)), 160)

    def test_collapses_whitespace_and_newlines(self):
        self.assertEqual(truncate_at_word("Ferns\n\nand   figs"), "Ferns and figs")

    def test_single_long_word_is_hard_cut(self):
        self.assertEqual(truncate_at_word("x" * 50, 10), "x" * 9 + "…")

    def test_strips_dangling_punctuation_before_ellipsis(self):
        self.assertEqual(truncate_at_word("Tower Grove — plants and coffee", 15), "Tower Grove…")


@override_settings(**LOCAL_MEDIA, **NO_REVALIDATION)
class ApiSeoTests(TestCase):
    def setUp(self):
        self.city = make_city(intro="Plants in the places you already go.")
        self.venue = make_venue(
            self.city,
            name="Northwest Coffee",
            slug="northwest-coffee",
            neighborhood="Central West End",
            short_description="Ferns by the espresso bar.",
        )

    def city_seo(self):
        response = self.client.get(reverse("city-detail", kwargs={"city_slug": "st-louis"}))
        self.assertEqual(response.status_code, 200)
        return response.json()["seo"]

    def venue_seo(self):
        url = reverse("venue-detail", kwargs={"city_slug": "st-louis", "venue_slug": "northwest-coffee"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.json()["seo"]

    # --- Fallbacks ---

    def test_venue_fallbacks(self):
        self.assertEqual(
            self.venue_seo(),
            {
                "title": "Plants at Northwest Coffee · Forks And Farms",
                "description": "Central West End — Ferns by the espresso bar.",
                "og_image": None,
                "canonical_url": None,
                "noindex": False,
            },
        )

    def test_city_fallbacks(self):
        self.assertEqual(
            self.city_seo(),
            {
                "title": "Forks And Farms in St. Louis",
                "description": "Plants in the places you already go.",
                "og_image": None,  # frontend substitutes the site-wide default image
                "canonical_url": None,
                "noindex": False,
            },
        )

    def test_city_without_intro_gets_generic_description(self):
        self.city.intro = ""
        self.city.save()
        self.assertEqual(self.city_seo()["description"], "Find Forks And Farms plant locations in St. Louis.")

    def test_long_fallback_description_truncated_at_word_boundary(self):
        # 25 + 13 * 19 = 272 characters: over 160, under the field's 280 max.
        self.venue.short_description = ("Lush trailing pothos and " + "big monstera " * 19).strip()
        self.venue.save()

        description = self.venue_seo()["description"]
        self.assertLessEqual(len(description), 160)
        self.assertTrue(description.endswith("…"))
        # The word before the "…" is a whole word from the source text.
        self.assertIn(description[:-1].split()[-1], {"big", "monstera"})

    def test_venue_og_image_falls_back_to_hero_image_as_absolute_url(self):
        self.venue.hero_image = "venues/hero/nw.jpg"
        self.venue.save()
        self.assertEqual(self.venue_seo()["og_image"], "http://testserver/media/venues/hero/nw.jpg")

    # --- Overrides ---

    def test_overrides_win_over_fallbacks(self):
        self.venue.seo_title = "  Buy plants at Northwest Coffee  "
        self.venue.meta_description = "Custom description."
        self.venue.og_image = "seo/share.jpg"
        self.venue.hero_image = "venues/hero/nw.jpg"
        self.venue.canonical_url = "https://example.com/elsewhere"
        self.venue.save()

        seo = self.venue_seo()
        self.assertEqual(seo["title"], "Buy plants at Northwest Coffee")
        self.assertEqual(seo["description"], "Custom description.")
        self.assertEqual(seo["og_image"], "http://testserver/media/seo/share.jpg")
        self.assertEqual(seo["canonical_url"], "https://example.com/elsewhere")

    def test_city_og_image_override(self):
        self.city.og_image = "seo/stl.jpg"
        self.city.save()
        self.assertEqual(self.city_seo()["og_image"], "http://testserver/media/seo/stl.jpg")

    def test_override_description_is_not_truncated(self):
        # The owner's own text is theirs to control — the admin warns
        # about length, the API doesn't silently chop it.
        long_text = "word " * 50
        self.venue.meta_description = long_text.strip()
        self.venue.save()
        self.assertEqual(self.venue_seo()["description"], long_text.strip())

    # --- noindex ---

    def test_noindex_passes_through(self):
        self.venue.noindex = True
        self.venue.save()
        self.city.noindex = True
        self.city.save()

        self.assertTrue(self.venue_seo()["noindex"])
        self.assertTrue(self.city_seo()["noindex"])

    def test_noindex_venue_still_listed_publicly(self):
        # Decision: noindex only asks search engines to skip the page; it
        # stays on the site and in lists/cards.
        self.venue.noindex = True
        self.venue.save()
        slugs = [v["slug"] for v in self.client.get(reverse("venue-list")).json()]
        self.assertIn("northwest-coffee", slugs)

    # --- What's exposed where ---

    def test_target_phrases_never_exposed_on_any_public_endpoint(self):
        secret = "SECRET-PHRASE-plants-near-me"
        self.city.target_phrases = secret
        self.city.save()
        self.venue.target_phrases = secret
        self.venue.save()

        urls = [
            reverse("city-list"),
            reverse("city-detail", kwargs={"city_slug": "st-louis"}),
            reverse("venue-list"),
            reverse("venue-detail", kwargs={"city_slug": "st-louis", "venue_slug": "northwest-coffee"}),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, secret)
                self.assertNotContains(response, "target_phrases")

    def test_seo_object_only_on_detail_endpoints(self):
        self.assertNotIn("seo", self.client.get(reverse("city-list")).json()[0])
        self.assertNotIn("seo", self.client.get(reverse("venue-list")).json()[0])
        city_detail = self.client.get(reverse("city-detail", kwargs={"city_slug": "st-louis"})).json()
        self.assertNotIn("seo", city_detail["venues"][0])  # nested venue cards

    def test_raw_seo_fields_not_exposed(self):
        url = reverse("venue-detail", kwargs={"city_slug": "st-louis", "venue_slug": "northwest-coffee"})
        data = self.client.get(url).json()
        for field in ("seo_title", "meta_description", "og_image", "noindex", "canonical_url"):
            self.assertNotIn(field, data)  # only inside the resolved `seo` object

    def test_rows_without_any_seo_data_work(self):
        # Simulates rows that existed before the migration: every SEO
        # field at its default.
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.seo_title, "")
        self.assertFalse(self.venue.noindex)
        self.assertEqual(self.venue_seo()["title"], "Plants at Northwest Coffee · Forks And Farms")


@override_settings(**LOCAL_MEDIA, **NO_REVALIDATION)
class SeoAdminTests(TestCase):
    def setUp(self):
        self.city = make_city()
        self.venue = make_venue(self.city, name="Northwest Coffee", slug="northwest-coffee")
        admin_user = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.client.force_login(admin_user)

    def venue_change_page(self):
        return self.client.get(reverse("admin:core_venue_change", args=[self.venue.pk]))

    def test_venue_change_page_has_seo_section_preview_and_assets(self):
        response = self.venue_change_page()
        self.assertContains(response, "seo-preview")
        # Possibly with a cache-busting hash, e.g. seo.3f2a1b.js
        html = response.content.decode()
        self.assertRegex(html, r"core/admin/seo(\.[0-9a-f]+)?\.js")
        self.assertRegex(html, r"core/admin/seo(\.[0-9a-f]+)?\.css")
        self.assertContains(response, 'data-fallback-title="Plants at Northwest Coffee · Forks And Farms"')
        self.assertContains(response, "Recommended 1200 × 630 px, landscape JPG/PNG.")
        self.assertContains(response, "never published")  # target_phrases help text

    def test_city_change_page_has_seo_section(self):
        response = self.client.get(reverse("admin:core_city_change", args=[self.city.pk]))
        self.assertContains(response, "seo-preview")
        self.assertContains(response, 'data-fallback-title="Forks And Farms in St. Louis"')

    def test_add_page_shows_automatic_placeholder(self):
        response = self.client.get(reverse("admin:core_venue_add"))
        self.assertContains(response, "seo-preview")
        self.assertContains(response, "(automatic — shown after saving)")

    @override_settings(PUBLIC_SITE_URL="https://forksandfarms.com")
    def test_preview_url_uses_public_site_url(self):
        self.assertContains(
            self.venue_change_page(), "forksandfarms.com › locations › st-louis › northwest-coffee"
        )

    @override_settings(PUBLIC_SITE_URL="")
    def test_preview_url_is_path_only_without_public_site_url(self):
        self.assertContains(self.venue_change_page(), "/locations/st-louis/northwest-coffee")

    def test_preview_escapes_html(self):
        self.venue.seo_title = '<script>alert("x")</script>'
        self.venue.save()
        response = self.venue_change_page()
        self.assertNotContains(response, '<script>alert("x")</script>')
        self.assertContains(response, "&lt;script&gt;")


@override_settings(**NO_REVALIDATION)
class SeoEditRefreshesLiveSiteTests(TestCase):
    def test_seo_only_edit_triggers_revalidation(self):
        city = make_city()
        venue = make_venue(city, slug="northwest-coffee")

        with (
            self.settings(FRONTEND_REVALIDATE_URL="http://frontend.test/api/revalidate", REVALIDATE_SECRET="s"),
            mock.patch.object(revalidation, "_send_in_background") as send,
            self.captureOnCommitCallbacks(execute=True),
        ):
            venue.meta_description = "New description for Google."
            venue.save(update_fields=["meta_description"])

        send.assert_called_once()
        self.assertIn("/locations/st-louis/northwest-coffee", send.call_args.args[0])
