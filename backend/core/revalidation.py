"""
On-demand page refresh: tell the Next.js site to rebuild pages after an
admin edit, so changes show up within seconds instead of waiting for the
10-minute fallback (spec §7).

How it fits together:
- core/signals.py calls request_revalidation(paths) whenever a City,
  Venue, VenuePhoto or OpeningHours row is saved or deleted.
- Paths are collected into one batch per database transaction. A single
  admin save (the venue + its 7 hours rows + photo inlines) runs inside
  one transaction, so it ends up as ONE request to the frontend.
- The request is only sent after the transaction commits
  (transaction.on_commit) — a save that fails and rolls back sends
  nothing — and runs in a background thread with a short timeout, so a
  slow or down frontend never slows down or breaks an admin save.
  Failures are only logged.
- If FRONTEND_REVALIDATE_URL or REVALIDATE_SECRET isn't set (e.g. local
  dev without the frontend), everything here quietly does nothing.

The frontend side is frontend/app/api/revalidate/route.ts — it only
accepts the path shapes built by the helpers below.
"""

import json
import logging
import threading
import urllib.error
import urllib.request

from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)

# Background (signal) sends: short, nobody is waiting on them.
BACKGROUND_TIMEOUT_SECONDS = 3
# The "Refresh live site pages" admin action waits for the answer so it
# can report success/failure, so give it a little longer.
ADMIN_ACTION_TIMEOUT_SECONDS = 5

# Both must match frontend/lib/revalidation.ts.
SECRET_HEADER = "X-Revalidate-Secret"
MAX_PATHS_PER_REQUEST = 100

# Pages that list venues across the whole site, refreshed on any change.
SITE_WIDE_PATHS = ["/", "/partner"]


# --- Which pages does a change affect? ---


def city_path(city_slug):
    return f"/locations/{city_slug}"


def venue_path(city_slug, venue_slug):
    return f"/locations/{city_slug}/{venue_slug}"


def paths_for_city(city):
    """Every page showing this city: the site-wide pages, the city page,
    and every venue page in it (they show the city's name). All venues,
    not just public ones — refreshing a paused venue's page is what makes
    it 404 promptly."""
    from .models import Venue

    venue_slugs = Venue.objects.filter(city_id=city.pk).values_list("slug", flat=True)
    return {
        *SITE_WIDE_PATHS,
        city_path(city.slug),
        *(venue_path(city.slug, slug) for slug in venue_slugs),
    }


def paths_for_venue(venue):
    """A venue change shows up on its own page, its city page, the
    site-wide pages, and every other venue page in the same city (the
    "Other locations" cards) — which is exactly paths_for_city, plus the
    venue's own path in case it was just deleted (and so no longer
    appears in the city's venue list)."""
    city = venue.city
    return paths_for_city(city) | {venue_path(city.slug, venue.slug)}


# --- Batching per transaction ---

# One pending batch per thread (each web request runs on its own thread).
_local = threading.local()


def is_configured():
    return bool(settings.FRONTEND_REVALIDATE_URL and settings.REVALIDATE_SECRET)


def request_revalidation(paths):
    """Queue `paths` to be refreshed once the current transaction commits.

    Safe to call many times in one transaction — paths are merged and
    sent as one request. Outside a transaction (autocommit) Django runs
    on_commit callbacks immediately, so this sends straight away.
    """
    if not is_configured():
        logger.debug("Revalidation not configured; skipping %s", sorted(paths))
        return

    batch = getattr(_local, "batch", None)
    if batch is not None and _still_pending(batch):
        batch.paths.update(paths)
        return

    batch = _Batch()
    # Paths must be added BEFORE on_commit: outside a transaction it runs
    # flush immediately, which would otherwise send an empty batch.
    batch.paths.update(paths)
    _local.batch = batch
    transaction.on_commit(batch.flush, robust=True)


class _Batch:
    def __init__(self):
        self.paths = set()

    def flush(self):
        if getattr(_local, "batch", None) is self:
            _local.batch = None
        if self.paths:
            _send_in_background(sorted(self.paths))


def _still_pending(batch):
    """True if batch.flush is still waiting to run on commit.

    It won't be if the transaction it was registered in rolled back —
    Django drops on_commit callbacks then — in which case we must start a
    new batch rather than add paths to one that will never be sent.
    (connection.run_on_commit is Django's own list of pending callbacks:
    a private attribute, but stable for years.)
    """
    connection = transaction.get_connection()
    return any(entry[1] == batch.flush for entry in connection.run_on_commit)


# --- Sending ---


def _send_in_background(paths):
    # daemon=True: never keeps a worker process alive at shutdown.
    thread = threading.Thread(
        target=send_revalidation,
        args=(paths,),
        kwargs={"timeout": BACKGROUND_TIMEOUT_SECONDS},
        daemon=True,
    )
    thread.start()


def send_revalidation(paths, timeout=BACKGROUND_TIMEOUT_SECONDS):
    """POST `paths` to the frontend's /api/revalidate. Never raises.

    Returns (ok, message) so the admin action can show the result;
    background sends just rely on the logging here. Normally one request;
    only a very large batch is split (the frontend caps paths per request).
    """
    if not is_configured():
        return False, "Live-site refresh isn't configured (FRONTEND_REVALIDATE_URL / REVALIDATE_SECRET)."

    paths = list(paths)
    for start in range(0, len(paths), MAX_PATHS_PER_REQUEST):
        ok, message = _post_paths(paths[start : start + MAX_PATHS_PER_REQUEST], timeout)
        if not ok:
            return False, message

    logger.info("Revalidated %d page(s): %s", len(paths), paths)
    return True, f"Refreshed {len(paths)} page(s) on the live site."


def _post_paths(paths, timeout):
    body = json.dumps({"paths": paths}).encode()
    request = urllib.request.Request(
        settings.FRONTEND_REVALIDATE_URL,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", SECRET_HEADER: settings.REVALIDATE_SECRET},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read()
    except urllib.error.HTTPError as error:
        message = f"Frontend refused the refresh (HTTP {error.code})."
        logger.warning("Revalidation failed for %s: %s", paths, message)
        return False, message
    except Exception as error:  # timeout, DNS, connection refused, ...
        message = f"Couldn't reach the frontend: {error}"
        logger.warning("Revalidation failed for %s: %s", paths, message)
        return False, message
    return True, ""
