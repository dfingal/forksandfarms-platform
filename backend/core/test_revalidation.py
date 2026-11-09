"""
Tests for on-demand live-site refresh (core/revalidation.py, the
signals in core/signals.py, and the "Refresh live site pages" admin
action).

No test here makes a real HTTP request: background sends are patched
out, and send_revalidation's own tests patch urllib's urlopen.

Revalidation is switched OFF for the whole module (backend/.env may set
it locally) and only switched on inside `capture_sends()`, so test setup
(creating cities/venues) never queues a refresh of its own.
"""

import urllib.error
from contextlib import contextmanager
from unittest import mock

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from . import revalidation
from .models import City, OpeningHours, Venue, VenuePhoto
from .test_admin import venue_form_data
from .tests import make_city, make_venue

FRONTEND_URL = "http://frontend.test/api/revalidate"
SECRET = "test-secret"
ON = {"FRONTEND_REVALIDATE_URL": FRONTEND_URL, "REVALIDATE_SECRET": SECRET}
OFF = {"FRONTEND_REVALIDATE_URL": "", "REVALIDATE_SECRET": ""}


@override_settings(**OFF)
class RevalidationTestCase(TestCase):
    def setUp(self):
        self.stl = make_city()
        self.venue = make_venue(self.stl, slug="northwest-coffee")
        self.sibling = make_venue(self.stl, name="Sibling", slug="sibling")

    @contextmanager
    def capture_sends(self):
        """Turn revalidation on, run on_commit callbacks at the end of the
        block (TestCase never really commits), and record each send."""
        with (
            self.settings(**ON),
            mock.patch.object(revalidation, "_send_in_background") as send,
            self.captureOnCommitCallbacks(execute=True),
        ):
            yield send

    def sent_paths(self, send):
        """The single batch sent, as a set. Fails if there wasn't exactly one."""
        self.assertEqual(send.call_count, 1, f"expected 1 request, got {send.call_args_list}")
        return set(send.call_args.args[0])


class PathsTests(RevalidationTestCase):
    def test_venue_change_refreshes_site_city_own_and_sibling_pages(self):
        with self.capture_sends() as send:
            self.venue.short_description = "New copy"
            self.venue.save()

        self.assertEqual(
            self.sent_paths(send),
            {
                "/",
                "/partner",
                "/locations/st-louis",
                "/locations/st-louis/northwest-coffee",
                "/locations/st-louis/sibling",  # "Other locations" cards
            },
        )

    def test_other_cities_venues_are_not_refreshed(self):
        kc = make_city(name="Kansas City", slug="kansas-city")
        make_venue(kc, slug="kc-venue")

        with self.capture_sends() as send:
            self.venue.save()

        paths = self.sent_paths(send)
        self.assertNotIn("/locations/kansas-city", paths)
        self.assertNotIn("/locations/kansas-city/kc-venue", paths)

    def test_paused_venue_is_still_refreshed_so_it_404s(self):
        with self.capture_sends() as send:
            self.venue.status = Venue.Status.PAUSED
            self.venue.save()

        self.assertIn("/locations/st-louis/northwest-coffee", self.sent_paths(send))

    def test_city_change_refreshes_every_venue_page_in_it(self):
        with self.capture_sends() as send:
            self.stl.name = "Saint Louis"
            self.stl.save()

        self.assertEqual(
            self.sent_paths(send),
            {
                "/",
                "/partner",
                "/locations/st-louis",
                "/locations/st-louis/northwest-coffee",
                "/locations/st-louis/sibling",
            },
        )

    def test_photo_save_and_delete_refresh_its_venue(self):
        with self.capture_sends() as send:
            photo = VenuePhoto.objects.create(venue=self.venue, image="x.jpg", alt_text="Ferns")
        self.assertIn("/locations/st-louis/northwest-coffee", self.sent_paths(send))

        with self.capture_sends() as send:
            photo.delete()
        self.assertIn("/locations/st-louis/northwest-coffee", self.sent_paths(send))

    def test_opening_hours_save_and_delete_refresh_its_venue(self):
        row = self.venue.opening_hours.first()
        with self.capture_sends() as send:
            row.is_closed = True
            row.save()
        self.assertIn("/locations/st-louis/northwest-coffee", self.sent_paths(send))

        with self.capture_sends() as send:
            row.delete()
        self.assertIn("/locations/st-louis/northwest-coffee", self.sent_paths(send))


class UrlChangeTests(RevalidationTestCase):
    def test_venue_slug_change_refreshes_old_and_new_path(self):
        with self.capture_sends() as send:
            self.venue.slug = "nw-coffee"
            self.venue.save()

        paths = self.sent_paths(send)
        self.assertIn("/locations/st-louis/northwest-coffee", paths)  # old
        self.assertIn("/locations/st-louis/nw-coffee", paths)  # new

    def test_venue_moving_city_refreshes_both_cities(self):
        kc = make_city(name="Kansas City", slug="kansas-city")

        with self.capture_sends() as send:
            self.venue.city = kc
            self.venue.save()

        paths = self.sent_paths(send)
        self.assertIn("/locations/st-louis", paths)
        self.assertIn("/locations/st-louis/northwest-coffee", paths)
        self.assertIn("/locations/st-louis/sibling", paths)  # listed it in "Other locations"
        self.assertIn("/locations/kansas-city", paths)
        self.assertIn("/locations/kansas-city/northwest-coffee", paths)

    def test_city_slug_change_refreshes_old_city_and_venue_paths(self):
        with self.capture_sends() as send:
            self.stl.slug = "stl"
            self.stl.save()

        paths = self.sent_paths(send)
        self.assertIn("/locations/st-louis", paths)
        self.assertIn("/locations/st-louis/northwest-coffee", paths)
        self.assertIn("/locations/st-louis/sibling", paths)
        self.assertIn("/locations/stl", paths)
        self.assertIn("/locations/stl/northwest-coffee", paths)

    def test_venue_delete_refreshes_its_own_path(self):
        with self.capture_sends() as send:
            self.venue.delete()

        paths = self.sent_paths(send)
        self.assertIn("/locations/st-louis/northwest-coffee", paths)
        self.assertIn("/locations/st-louis", paths)

    def test_city_delete_refreshes_its_venue_paths(self):
        with self.capture_sends() as send:
            self.stl.delete()

        paths = self.sent_paths(send)
        self.assertIn("/locations/st-louis", paths)
        self.assertIn("/locations/st-louis/northwest-coffee", paths)
        self.assertIn("/locations/st-louis/sibling", paths)


class BatchingTests(RevalidationTestCase):
    def test_many_saves_in_one_transaction_send_one_request(self):
        with self.capture_sends() as send:
            with transaction.atomic():
                self.venue.save()
                for row in self.venue.opening_hours.all():
                    row.save()
                VenuePhoto.objects.create(venue=self.venue, image="x.jpg", alt_text="Ferns")
                self.stl.save()

        self.sent_paths(send)  # asserts exactly one request

    def test_admin_save_with_inline_changes_sends_one_request(self):
        admin_user = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.client.force_login(admin_user)

        # Change two of the venue's 7 hours rows alongside the venue itself.
        rows = list(self.venue.opening_hours.order_by("weekday"))
        data = venue_form_data(
            self.stl,
            name=self.venue.name,
            slug=self.venue.slug,
            short_description="Edited in admin",
            **{
                "opening_hours-TOTAL_FORMS": str(len(rows)),
                "opening_hours-INITIAL_FORMS": str(len(rows)),
            },
        )
        for i, row in enumerate(rows):
            prefix = f"opening_hours-{i}-"
            data.update(
                {
                    f"{prefix}id": row.pk,
                    f"{prefix}venue": self.venue.pk,
                    f"{prefix}weekday": row.weekday,
                    f"{prefix}order": row.order,
                    f"{prefix}open_time": "07:00" if i < 2 else "",
                    f"{prefix}close_time": "15:00" if i < 2 else "",
                }
            )

        with self.capture_sends() as send:
            response = self.client.post(
                reverse("admin:core_venue_change", args=[self.venue.pk]), data
            )

        self.assertEqual(response.status_code, 302, getattr(response, "context", None) and response.context.get("errors"))
        self.assertEqual(self.venue.opening_hours.exclude(open_time=None).count(), 2)
        self.assertIn("/locations/st-louis/northwest-coffee", self.sent_paths(send))

    def test_rolled_back_save_sends_nothing(self):
        kc = make_city(name="Kansas City", slug="kansas-city")
        kc_venue = make_venue(kc, slug="kc-venue")

        with self.capture_sends() as send:
            try:
                with transaction.atomic():
                    kc_venue.save()
                    raise RuntimeError("simulated failed save")
            except RuntimeError:
                pass
            # A later, successful save must start a fresh batch rather
            # than add to the dead one (which would never be sent).
            self.venue.save()

        paths = self.sent_paths(send)
        self.assertNotIn("/locations/kansas-city", paths)
        self.assertIn("/locations/st-louis/northwest-coffee", paths)

    def test_nothing_sent_until_commit(self):
        with self.settings(**ON), mock.patch.object(revalidation, "_send_in_background") as send:
            with self.captureOnCommitCallbacks(execute=False) as callbacks:
                self.venue.save()
            send.assert_not_called()
            self.assertEqual(len(callbacks), 1)


@override_settings(**ON)
class AutocommitTests(TransactionTestCase):
    """Outside any transaction (shell, scripts) Django runs on_commit
    callbacks immediately — the paths must still be sent. TestCase can't
    show this: it wraps every test in a transaction."""

    def test_save_outside_transaction_sends_immediately(self):
        with mock.patch.object(revalidation, "_send_in_background") as send:
            make_venue(make_city(), slug="northwest-coffee")

        self.assertTrue(send.called)
        self.assertIn("/locations/st-louis/northwest-coffee", send.call_args.args[0])


class NotConfiguredTests(RevalidationTestCase):
    def test_skips_silently_when_not_configured(self):
        for settings in (OFF, {**ON, "REVALIDATE_SECRET": ""}, {**ON, "FRONTEND_REVALIDATE_URL": ""}):
            with self.subTest(settings=settings):
                with (
                    self.settings(**settings),
                    mock.patch.object(revalidation, "_send_in_background") as send,
                    self.captureOnCommitCallbacks(execute=True) as callbacks,
                ):
                    self.venue.save()
                self.assertEqual(callbacks, [])
                send.assert_not_called()


class NeverBreaksSaveTests(RevalidationTestCase):
    def test_bug_working_out_paths_is_logged_and_save_still_succeeds(self):
        with (
            self.capture_sends() as send,
            mock.patch.object(revalidation, "paths_for_venue", side_effect=ValueError("boom")),
            self.assertLogs("core.signals", level="ERROR"),
        ):
            self.venue.name = "Still saved"
            self.venue.save()

        send.assert_not_called()
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.name, "Still saved")


@override_settings(**ON)
class SendRevalidationTests(TestCase):
    """send_revalidation itself: the actual HTTP call, with urlopen mocked."""

    @mock.patch("urllib.request.urlopen")
    def test_success_posts_paths_with_secret_header(self, urlopen):
        with self.assertLogs("core.revalidation", level="INFO"):
            ok, message = revalidation.send_revalidation(["/", "/partner"], timeout=3)

        self.assertTrue(ok)
        self.assertIn("2 page(s)", message)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, FRONTEND_URL)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("X-revalidate-secret"), SECRET)
        self.assertEqual(request.data, b'{"paths": ["/", "/partner"]}')
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 3)

    @mock.patch("urllib.request.urlopen")
    def test_large_batch_is_split_to_fit_frontend_limit(self, urlopen):
        paths = [f"/locations/city-{i}" for i in range(revalidation.MAX_PATHS_PER_REQUEST + 1)]
        with self.assertLogs("core.revalidation", level="INFO"):
            ok, _ = revalidation.send_revalidation(paths)

        self.assertTrue(ok)
        self.assertEqual(urlopen.call_count, 2)

    @mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused"))
    def test_network_error_is_logged_not_raised(self, urlopen):
        with self.assertLogs("core.revalidation", level="WARNING"):
            ok, message = revalidation.send_revalidation(["/"])
        self.assertFalse(ok)
        self.assertIn("Couldn't reach", message)

    @mock.patch("urllib.request.urlopen", side_effect=TimeoutError("timed out"))
    def test_timeout_is_logged_not_raised(self, urlopen):
        with self.assertLogs("core.revalidation", level="WARNING"):
            ok, _ = revalidation.send_revalidation(["/"])
        self.assertFalse(ok)

    @mock.patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.HTTPError(FRONTEND_URL, 401, "Unauthorized", {}, None),
    )
    def test_http_error_is_logged_not_raised(self, urlopen):
        with self.assertLogs("core.revalidation", level="WARNING"):
            ok, message = revalidation.send_revalidation(["/"])
        self.assertFalse(ok)
        self.assertIn("401", message)

    @override_settings(**OFF)
    @mock.patch("urllib.request.urlopen")
    def test_not_configured_sends_nothing(self, urlopen):
        ok, _ = revalidation.send_revalidation(["/"])
        self.assertFalse(ok)
        urlopen.assert_not_called()


@override_settings(**OFF)
class RefreshAdminActionTests(TestCase):
    def setUp(self):
        self.stl = make_city()
        self.venue = make_venue(self.stl, slug="northwest-coffee")
        admin_user = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.client.force_login(admin_user)

    def run_action(self, model_name, pk):
        return self.client.post(
            reverse(f"admin:core_{model_name}_changelist"),
            {"action": "refresh_live_site_pages", "_selected_action": [pk]},
            follow=True,
        )

    @mock.patch.object(revalidation, "send_revalidation", return_value=(True, "Refreshed 5 page(s) on the live site."))
    def test_venue_action_reports_success(self, send):
        response = self.run_action("venue", self.venue.pk)

        self.assertContains(response, "Refreshed 5 page(s)")
        self.assertIn("/locations/st-louis/northwest-coffee", send.call_args.args[0])
        self.assertEqual(send.call_args.kwargs["timeout"], revalidation.ADMIN_ACTION_TIMEOUT_SECONDS)

    @mock.patch.object(revalidation, "send_revalidation", return_value=(False, "Couldn't reach the frontend: refused"))
    def test_city_action_reports_failure(self, send):
        response = self.run_action("city", self.stl.pk)

        self.assertContains(response, "Couldn&#x27;t reach the frontend")
        self.assertIn("/locations/st-louis", send.call_args.args[0])
