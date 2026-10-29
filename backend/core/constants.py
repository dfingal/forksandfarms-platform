"""
Shared constants for the core app.

PUBLIC_VENUE_STATUSES is the single source of truth for "which Venue
statuses are visible on the public site" (spec §5) — every view that
touches Venue filters through this instead of repeating the list.
"""

from core.models import Venue

PUBLIC_VENUE_STATUSES = [
    Venue.Status.ACTIVE,
    Venue.Status.SEASONAL,
    Venue.Status.COMING_SOON,
]
