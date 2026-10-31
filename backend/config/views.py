"""
Infra-level views (not domain logic, hence living in config/ rather than
an app) — currently just the health check.
"""

from django.http import HttpResponse


def health_check(request):
    """Bare 200 for Render's health checker.

    This path is listed in SECURE_REDIRECT_EXEMPT (settings.py) so it
    isn't caught by the HTTPS redirect: Render's health checker hits the
    service over plain HTTP internally, and if that got redirected to
    HTTPS, Render would see a 301 instead of a 200 and mark the deploy
    unhealthy.
    """
    return HttpResponse("ok")
