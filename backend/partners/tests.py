from unittest.mock import patch

from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .integrations import send_application_emails, verify_turnstile
from .models import PartnerApplication


def valid_payload(**overrides):
    payload = {
        "contact_name": "Jamie Owner",
        "email": "jamie@example.com",
        "phone": "314-555-0100",
        "venue_name": "Jamie's Cafe",
        "venue_type": "coffee_shop",
        "address": "100 Main St, St. Louis, MO 63101",
        "space_description": "About 10 plants",
        "interested_tiers": ["retail_shelf"],
        "referral_source": "Instagram",
        "notes": "",
        "turnstile_token": "test-token",
    }
    payload.update(overrides)
    return payload


@override_settings(DEBUG=True, RESEND_API_KEY="")  # Turnstile auto-passes; emails skipped (no network)
class PartnerApplicationCreateTests(TestCase):
    url = reverse("partner-application-create")

    def setUp(self):
        # Throttle counts are cache-backed; a leftover count from a previous
        # test (or test order) would make the 429 test flaky.
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_valid_submission_creates_application_and_returns_201(self):
        response = self.client.post(self.url, valid_payload(), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(set(body.keys()), {"id", "contact_name"})
        self.assertEqual(body["contact_name"], "Jamie Owner")

        application = PartnerApplication.objects.get(pk=body["id"])
        self.assertEqual(application.status, PartnerApplication.Status.NEW)
        self.assertEqual(application.email, "jamie@example.com")
        # source_ip is set from the request, not client-supplied.
        self.assertIsNotNone(application.source_ip)

    def test_missing_required_field_returns_400(self):
        payload = valid_payload()
        del payload["contact_name"]
        response = self.client.post(self.url, payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(PartnerApplication.objects.count(), 0)

    def test_invalid_interested_tier_returns_400(self):
        response = self.client.post(
            self.url,
            valid_payload(interested_tiers=["retail_shelf", "not_a_real_tier"]),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("interested_tiers", response.json())
        self.assertEqual(PartnerApplication.objects.count(), 0)

    def test_empty_interested_tiers_returns_400(self):
        response = self.client.post(
            self.url, valid_payload(interested_tiers=[]), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_client_cannot_set_internal_fields(self):
        response = self.client.post(
            self.url,
            valid_payload(status="signed", internal_notes="sneaky"),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        application = PartnerApplication.objects.get(pk=response.json()["id"])
        self.assertEqual(application.status, PartnerApplication.Status.NEW)
        self.assertEqual(application.internal_notes, "")

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_sixth_request_in_an_hour_is_throttled(self):
        for _ in range(5):
            response = self.client.post(self.url, valid_payload(), content_type="application/json")
            self.assertEqual(response.status_code, 201)

        response = self.client.post(self.url, valid_payload(), content_type="application/json")
        self.assertEqual(response.status_code, 429)


class TurnstileVerificationTests(TestCase):
    """Unit tests for the verify_turnstile stub's DEBUG/fail-closed behavior."""

    @override_settings(DEBUG=True)
    def test_debug_mode_always_passes_without_network_call(self):
        with patch("partners.integrations.requests.post") as mock_post:
            self.assertTrue(verify_turnstile("any-token"))
            mock_post.assert_not_called()

    @override_settings(DEBUG=False, TURNSTILE_SECRET_KEY="")
    def test_no_secret_configured_fails_closed(self):
        with patch("partners.integrations.requests.post") as mock_post:
            self.assertFalse(verify_turnstile("any-token"))
            mock_post.assert_not_called()

    @override_settings(DEBUG=False, TURNSTILE_SECRET_KEY="test-secret")
    def test_real_check_calls_cloudflare_and_honors_result(self):
        with patch("partners.integrations.requests.post") as mock_post:
            mock_post.return_value.json.return_value = {"success": True}
            mock_post.return_value.raise_for_status.return_value = None
            self.assertTrue(verify_turnstile("good-token"))

            mock_post.return_value.json.return_value = {"success": False}
            self.assertFalse(verify_turnstile("bad-token"))

    @override_settings(DEBUG=False, TURNSTILE_SECRET_KEY="test-secret")
    def test_network_error_fails_closed(self):
        import requests

        with patch("partners.integrations.requests.post", side_effect=requests.RequestException):
            self.assertFalse(verify_turnstile("any-token"))


def make_application(**overrides):
    defaults = dict(
        contact_name="Jamie Owner",
        email="jamie@example.com",
        phone="314-555-0100",
        venue_name="Jamie's Cafe",
        venue_type="coffee_shop",
        address="100 Main St, St. Louis, MO 63101",
        space_description="About 10 plants",
        interested_tiers=["retail_shelf"],
        referral_source="Instagram",
        notes="",
    )
    defaults.update(overrides)
    return PartnerApplication.objects.create(**defaults)


class SendApplicationEmailsTests(TestCase):
    """Unit tests for the Resend integration's skip/best-effort behavior."""

    def setUp(self):
        self.application = make_application()
        self.request = RequestFactory().get("/")

    @override_settings(RESEND_API_KEY="")
    def test_no_key_configured_skips_without_network_call(self):
        with patch("partners.integrations.requests.post") as mock_post:
            send_application_emails(self.application, self.request)
            mock_post.assert_not_called()

    @override_settings(
        RESEND_API_KEY="re_test",
        FNF_NOTIFY_EMAIL="hello@forksandfarms.com",
        FNF_FROM_EMAIL="Forks And Farms <hello@forksandfarms.com>",
    )
    def test_key_configured_sends_both_emails(self):
        with patch("partners.integrations.requests.post") as mock_post:
            mock_post.return_value.ok = True
            send_application_emails(self.application, self.request)

            self.assertEqual(mock_post.call_count, 2)
            recipients = [call.kwargs["json"]["to"] for call in mock_post.call_args_list]
            self.assertIn(["hello@forksandfarms.com"], recipients)
            self.assertIn(["jamie@example.com"], recipients)

            # The owner-notification email includes a working admin link.
            owner_call = next(
                c for c in mock_post.call_args_list if c.kwargs["json"]["to"] == ["hello@forksandfarms.com"]
            )
            self.assertIn(f"/admin/partners/partnerapplication/{self.application.pk}/change/",
                           owner_call.kwargs["json"]["text"])

    @override_settings(RESEND_API_KEY="re_test", FNF_NOTIFY_EMAIL="hello@forksandfarms.com")
    def test_resend_failure_does_not_raise(self):
        import requests

        with patch("partners.integrations.requests.post", side_effect=requests.RequestException):
            # Must not raise — an already-saved application shouldn't 500
            # just because the email provider is down.
            send_application_emails(self.application, self.request)
