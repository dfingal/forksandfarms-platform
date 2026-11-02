"""
post_save signal: every new Venue gets 7 placeholder OpeningHours rows
(one per weekday, unset — not closed) so the admin inline always shows
a full pre-populated week instead of starting from a blank slate.

Existing venues (from before this feature) get the same treatment via
the 0004 data migration instead, since signals don't fire retroactively.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OpeningHours, Venue


@receiver(post_save, sender=Venue)
def create_default_opening_hours(sender, instance, created, **kwargs):
    if not created:
        return
    OpeningHours.objects.bulk_create(
        OpeningHours(venue=instance, weekday=weekday) for weekday in OpeningHours.Weekday.values
    )
