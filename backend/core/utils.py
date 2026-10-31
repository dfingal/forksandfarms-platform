"""
Shared request helpers.
"""

from django.conf import settings


def get_client_ip(request):
    """Return the real client IP, respecting Render's reverse proxy.

    Mirrors DRF's own throttle.get_ident() logic (see REST_FRAMEWORK
    NUM_PROXIES in settings.py) so the IP used for rate limiting and the
    one stored as PartnerApplication.source_ip always agree. Without this,
    every request behind Render's proxy would share the single proxy IP
    in REMOTE_ADDR and all visitors would share one rate limit bucket.
    """
    num_proxies = settings.REST_FRAMEWORK.get("NUM_PROXIES")
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    remote_addr = request.META.get("REMOTE_ADDR")

    if not num_proxies:
        return remote_addr
    if not xff:
        return remote_addr

    addrs = [addr.strip() for addr in xff.split(",")]
    # The trusted client IP is `num_proxies` entries from the right of the
    # X-Forwarded-For chain (each proxy appends the address it saw).
    return addrs[-min(num_proxies, len(addrs))]
