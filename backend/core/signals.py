"""
Model signals for the core app.

1. post_save on Venue: every new Venue gets 7 placeholder OpeningHours
   rows (one per weekday, unset — not closed) so the admin inline always
   shows a full pre-populated week instead of starting from a blank
   slate. Existing venues (from before this feature) get the same
   treatment via the 0003 data migration instead, since signals don't
   fire retroactively.

2. Live-site refresh: saving or deleting a City, Venue, VenuePhoto or
   OpeningHours row asks the Next.js site to rebuild the affected pages
   (see core/revalidation.py for batching/sending). If a venue's slug or
   city changes — or a city's slug — the OLD paths are refreshed too, so
   the old URL stops serving stale content and 404s promptly.
"""

import functools
import logging

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from . import revalidation
from .models import City, OpeningHours, Venue, VenuePhoto

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Venue)
def create_default_opening_hours(sender, instance, created, **kwargs):
    if not created:
        return
    OpeningHours.objects.bulk_create(
        OpeningHours(venue=instance, weekday=weekday) for weekday in OpeningHours.Weekday.values
    )


# --- Live-site refresh ---


def never_breaks_save(handler):
    """A refresh is nice-to-have; a bug in working out which pages to
    refresh must never stop the admin from saving. Log it and move on
    (the 10-minute fallback still refreshes the page)."""

    @functools.wraps(handler)
    def wrapper(sender, instance, **kwargs):
        # raw=True means loaddata/fixtures — related rows may not exist yet.
        if kwargs.get("raw"):
            return
        try:
            handler(sender, instance, **kwargs)
        except Exception:
            logger.exception("Couldn't work out pages to refresh for %r", instance)

    return wrapper


@receiver(pre_save, sender=Venue)
@never_breaks_save
def remember_old_venue_location(sender, instance, **kwargs):
    """Stash the venue's current (pre-save) slug + city so post_save can
    tell whether its URL is about to change."""
    instance._revalidation_old = (
        Venue.objects.filter(pk=instance.pk).select_related("city").first() if instance.pk else None
    )


@receiver(post_save, sender=Venue)
@receiver(post_delete, sender=Venue)
@never_breaks_save
def refresh_venue_pages(sender, instance, **kwargs):
    paths = revalidation.paths_for_venue(instance)

    old = getattr(instance, "_revalidation_old", None)
    if old and (old.slug != instance.slug or old.city_id != instance.city_id):
        # Old URL (so it 404s) + everything under the old city, whose
        # city page and "Other locations" cards listed this venue.
        paths |= revalidation.paths_for_venue(old)

    revalidation.request_revalidation(paths)


@receiver(pre_save, sender=City)
@never_breaks_save
def remember_old_city_slug(sender, instance, **kwargs):
    instance._revalidation_old_slug = (
        City.objects.filter(pk=instance.pk).values_list("slug", flat=True).first()
        if instance.pk
        else None
    )


@receiver(post_save, sender=City)
@receiver(post_delete, sender=City)
@never_breaks_save
def refresh_city_pages(sender, instance, **kwargs):
    paths = revalidation.paths_for_city(instance)

    old_slug = getattr(instance, "_revalidation_old_slug", None)
    if old_slug and old_slug != instance.slug:
        # Every old URL under the renamed city.
        venue_slugs = instance.venues.values_list("slug", flat=True)
        paths.add(revalidation.city_path(old_slug))
        paths.update(revalidation.venue_path(old_slug, slug) for slug in venue_slugs)

    revalidation.request_revalidation(paths)


@receiver(post_save, sender=VenuePhoto)
@receiver(post_delete, sender=VenuePhoto)
@receiver(post_save, sender=OpeningHours)
@receiver(post_delete, sender=OpeningHours)
@never_breaks_save
def refresh_pages_for_venue_child(sender, instance, **kwargs):
    """Photos and hours only show on their venue's page, but the same
    batch as the venue itself — so asking for the venue's full path set
    costs nothing extra (it's merged into one request)."""
    revalidation.request_revalidation(revalidation.paths_for_venue(instance.venue))
