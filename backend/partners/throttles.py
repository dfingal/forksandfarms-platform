from rest_framework.throttling import AnonRateThrottle


class PartnerApplicationThrottle(AnonRateThrottle):
    """5/hour per client IP (spec §5). Rate is set in settings.py.

    get_ident() (inherited from BaseThrottle) already respects the
    REST_FRAMEWORK NUM_PROXIES setting, so this is safe behind Railway's
    reverse proxy — see core/utils.get_client_ip for the matching logic
    used to populate PartnerApplication.source_ip.
    """

    scope = "partner_application"
