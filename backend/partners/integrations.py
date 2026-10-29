"""
Stubs for the two external checks the application POST needs:
Turnstile verification and the Resend confirmation/notification emails.

Both are wired into the view now so the frontend form can be built and
tested against this endpoint before real keys exist. Replace the bodies
marked TODO when Turnstile/Resend keys are added — the function
signatures are the contract the rest of the app relies on.
"""

import requests
from django.conf import settings

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


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


def send_application_emails(application):
    """Send the two emails spec §7 describes via Resend.

    TODO(resend): send
      1. to FNF_NOTIFY_EMAIL — summary of all fields + admin record link
      2. to application.email — "thanks, we got your application"
    No-op for now so the endpoint works end-to-end before RESEND_API_KEY
    is wired up.
    """
    pass
