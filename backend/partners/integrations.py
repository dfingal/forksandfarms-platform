"""
The two external checks the application POST needs: Turnstile
verification and the Resend confirmation/notification emails.

Both degrade safely when their key isn't configured: Turnstile fails
closed (rejects the application — see verify_turnstile), emails are
best-effort and simply skipped (a missing RESEND_API_KEY, or Resend
itself being down, should never be the reason an application is lost —
it's already saved to the database by the time emails are attempted).
"""

import logging

import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
RESEND_SEND_URL = "https://api.resend.com/emails"


def verify_turnstile(token, remote_ip=None):
    """Verify a Cloudflare Turnstile token. Returns True/False.

    - In DEBUG (local dev), always passes without a network call, so the
      form can be built before TURNSTILE_SECRET_KEY exists.
    - Outside DEBUG, fails closed if no secret key is configured — a
      misconfigured production deploy must reject applications, not
      silently accept spam.
    - Outside DEBUG with a secret configured, does the real Cloudflare
      siteverify call.
    """
    if settings.DEBUG:
        return True

    if not settings.TURNSTILE_SECRET_KEY:
        return False

    try:
        response = requests.post(
            TURNSTILE_VERIFY_URL,
            data={
                "secret": settings.TURNSTILE_SECRET_KEY,
                "response": token,
                **({"remoteip": remote_ip} if remote_ip else {}),
            },
            timeout=5,
        )
        response.raise_for_status()
        return bool(response.json().get("success"))
    except (requests.RequestException, ValueError):
        # Network/Cloudflare trouble: fail closed rather than let spam through.
        return False


def _send_resend_email(*, to, subject, text):
    """POST one email via Resend's HTTP API. Returns True on success.

    Never raises: a Resend outage or bad key must not turn an already-
    saved application into a 500 for the applicant. Logs and returns
    False instead, so the caller can decide whether to try the next one.
    """
    try:
        response = requests.post(
            RESEND_SEND_URL,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"from": settings.FNF_FROM_EMAIL, "to": [to], "subject": subject, "text": text},
            timeout=5,
        )
        if not response.ok:
            logger.warning("Resend send to %s failed: %s %s", to, response.status_code, response.text)
            return False
        return True
    except requests.RequestException:
        logger.warning("Resend send to %s failed", to, exc_info=True)
        return False


def send_application_emails(application, request):
    """Send the two emails spec §7 describes via Resend.

    Silently skipped (no network call, not an error) when RESEND_API_KEY
    is unset — lets the endpoint work end-to-end in any environment that
    hasn't configured Resend yet, same as the dev-local default.
    """
    if not settings.RESEND_API_KEY:
        logger.info("RESEND_API_KEY not set — skipping application emails for #%s", application.pk)
        return

    admin_path = reverse("admin:partners_partnerapplication_change", args=[application.pk])
    admin_url = request.build_absolute_uri(admin_path)

    tiers = ", ".join(application.interested_tiers) or "(none selected)"
    summary = (
        f"New partner application: {application.venue_name}\n\n"
        f"Contact: {application.contact_name}\n"
        f"Email: {application.email}\n"
        f"Phone: {application.phone or '(not provided)'}\n"
        f"Venue type: {application.venue_type}\n"
        f"Address: {application.address}\n"
        f"Space/plants: {application.space_description or '(not provided)'}\n"
        f"Interested in: {tiers}\n"
        f"Referral source: {application.referral_source or '(not provided)'}\n"
        f"Notes: {application.notes or '(none)'}\n\n"
        f"View in admin: {admin_url}"
    )
    _send_resend_email(
        to=settings.FNF_NOTIFY_EMAIL,
        subject=f"New partner application: {application.venue_name}",
        text=summary,
    )

    confirmation = (
        f"Hi {application.contact_name},\n\n"
        "Thanks — we got your application to partner with Forks And Farms. "
        "We'll reach out soon to schedule a walkthrough.\n\n"
        "— Forks And Farms"
    )
    _send_resend_email(
        to=application.email,
        subject="We got your Forks And Farms application",
        text=confirmation,
    )
