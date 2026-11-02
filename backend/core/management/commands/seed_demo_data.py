"""
Seed St. Louis + the 4 current partner venues with placeholder content.

Safe to re-run: every record is looked up by its natural key (city slug,
or (city, venue slug)) and updated in place rather than duplicated.
Opening hours are the one exception to "update in place" — see
_seed_opening_hours below for why.

Usage: python manage.py seed_demo_data
Refuses to run with DJANGO_DEBUG=False unless passed --force (this
seeds placeholder/demo content — a production run should be deliberate).
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.models import City, OpeningHours, Venue

# Coordinates and addresses below are realistic-looking St. Louis placeholders
# (TODO(copy): owner to confirm/correct exact address, neighborhood, and
# coordinates for each venue in admin — these are not verified real addresses).
VENUES = [
    {
        "name": "Northwest Coffee",
        "slug": "northwest-coffee",
        "neighborhood": "The Hill",
        "venue_type": Venue.VenueType.COFFEE_SHOP,
        "status": Venue.Status.ACTIVE,
        "partner_tier": Venue.PartnerTier.RETAIL_SHELF,
        "address_line1": "2101 Hartford St",
        "postal_code": "63104",
        "latitude": "38.609700",
        "longitude": "-90.237000",
        "hours": {"display": "Mon–Fri 6:30–17:00 · Sat–Sun 7:00–16:00"},
        "short_description": "TODO(copy): one or two sentences about the plant shelf here.",
        "setup_description": "TODO(copy): describe the plant setup at Northwest Coffee.",
        "display_order": 1,
    },
    {
        "name": "Scarlett's Wine Bar",
        "slug": "scarletts-wine-bar",
        "neighborhood": "Lafayette Square",
        "venue_type": Venue.VenueType.WINE_BAR,
        "status": Venue.Status.ACTIVE,
        "partner_tier": Venue.PartnerTier.DESIGN_INSTALL,
        "address_line1": "2042 Lafayette Ave",
        "postal_code": "63104",
        "latitude": "38.615500",
        "longitude": "-90.213500",
        "hours": {"display": "Tue–Sun 16:00–23:00"},
        "short_description": "TODO(copy): one or two sentences about the plant design here.",
        "setup_description": "TODO(copy): describe the plant setup at Scarlett's Wine Bar.",
        "display_order": 2,
    },
    {
        "name": "Egg Midtown",
        "slug": "egg-midtown",
        "neighborhood": "Midtown",
        "venue_type": Venue.VenueType.RESTAURANT,
        "status": Venue.Status.ACTIVE,
        "partner_tier": Venue.PartnerTier.LEASE_MAINTENANCE,
        "address_line1": "3701 Lindell Blvd",
        "postal_code": "63108",
        "latitude": "38.635500",
        "longitude": "-90.230500",
        "hours": {"display": "Daily 7:00–14:00"},
        "short_description": "TODO(copy): one or two sentences about the plant lease here.",
        "setup_description": "TODO(copy): describe the plant setup at Egg Midtown.",
        "display_order": 3,
    },
    {
        "name": "Rockwell Beer Co.",
        "slug": "rockwell-beer-co",
        "neighborhood": "Forest Park Southeast",
        "venue_type": Venue.VenueType.BREWERY,
        "status": Venue.Status.COMING_SOON,
        "partner_tier": Venue.PartnerTier.RETAIL_SHELF,
        "address_line1": "4336 Manchester Ave",
        "postal_code": "63110",
        "latitude": "38.619700",
        "longitude": "-90.255000",
        "hours": {"display": "Wed–Sun 15:00–22:00"},
        "short_description": "TODO(copy): one or two sentences about the plant shelf here.",
        "setup_description": "TODO(copy): describe the plant setup at Rockwell Beer Co.",
        "display_order": 4,
    },
]

MON, TUE, WED, THU, FRI, SAT, SUN = range(7)

# Per-venue weekday -> (open, close) in "HH:MM" strings, or None for closed.
# Roughly matches each venue's old free-text `hours.display` above.
OPENING_HOURS = {
    "northwest-coffee": {
        MON: ("06:30", "17:00"), TUE: ("06:30", "17:00"), WED: ("06:30", "17:00"),
        THU: ("06:30", "17:00"), FRI: ("06:30", "17:00"),
        SAT: ("07:00", "16:00"), SUN: ("07:00", "16:00"),
    },
    "scarletts-wine-bar": {
        MON: None,
        TUE: ("16:00", "23:00"), WED: ("16:00", "23:00"), THU: ("16:00", "23:00"),
        FRI: ("16:00", "23:00"), SAT: ("16:00", "23:00"), SUN: ("16:00", "23:00"),
    },
    "egg-midtown": {
        MON: ("07:00", "14:00"), TUE: ("07:00", "14:00"), WED: ("07:00", "14:00"),
        THU: ("07:00", "14:00"), FRI: ("07:00", "14:00"),
        SAT: ("07:00", "14:00"), SUN: ("07:00", "14:00"),
    },
    "rockwell-beer-co": {
        MON: None, TUE: None,
        WED: ("15:00", "22:00"), THU: ("15:00", "22:00"), FRI: ("15:00", "22:00"),
        SAT: ("15:00", "22:00"), SUN: ("15:00", "22:00"),
    },
}


class Command(BaseCommand):
    help = "Seed (or update) St. Louis and the 4 current partner venues with placeholder content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Required to run this when DJANGO_DEBUG=False (it seeds placeholder/demo content).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                "Refusing to run with DJANGO_DEBUG=False — this seeds placeholder/demo "
                "content, which almost certainly isn't what you want in production. "
                "Pass --force if you really mean it."
            )

        city, created = City.objects.update_or_create(
            slug="st-louis",
            defaults={
                "name": "St. Louis",
                "state": "MO",
                "intro": "TODO(copy): one-line intro for the St. Louis locations page.",
                "map_center_lat": "38.627000",
                "map_center_lng": "-90.199400",
                "map_zoom": 12,
                "timezone": "America/Chicago",
                "is_active": True,
            },
        )
        self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Updated'} city: {city.name}"))

        for data in VENUES:
            slug = data.pop("slug")
            venue, created = Venue.objects.update_or_create(
                city=city, slug=slug, defaults=data
            )
            # Restore slug into the dict in case handle() is ever called twice
            # in the same process (defaults mutation would otherwise lose it).
            data["slug"] = slug
            self.stdout.write(
                self.style.SUCCESS(f"  {'Created' if created else 'Updated'} venue: {venue.name}")
            )
            self._seed_opening_hours(venue, slug)

        self.stdout.write(self.style.SUCCESS("Seed complete."))

    def _seed_opening_hours(self, venue, slug):
        """Only ever fills in hours for a venue that has none set yet —
        never overwrites real hours an owner has already entered.

        "None set yet" means every row is unset (is_closed=False, no
        times) — which includes the 7 placeholder rows the post_save
        signal just created for a brand-new venue. A row that's
        explicitly closed, or has times, counts as "already set" and
        stops this from touching that venue at all.
        """
        existing = list(venue.opening_hours.all())
        if any(not row.is_unset for row in existing):
            self.stdout.write(f"    Opening hours already set for {venue.name} — left alone.")
            return

        day_hours = OPENING_HOURS.get(slug)
        if not day_hours:
            return  # no seed data for this venue; leave the unset placeholders

        venue.opening_hours.all().delete()
        rows = []
        for weekday in OpeningHours.Weekday.values:
            times = day_hours.get(weekday)
            if times is None:
                rows.append(OpeningHours(venue=venue, weekday=weekday, is_closed=True))
            else:
                open_time, close_time = times
                rows.append(
                    OpeningHours(
                        venue=venue, weekday=weekday,
                        open_time=open_time, close_time=close_time,
                    )
                )
        OpeningHours.objects.bulk_create(rows)
        self.stdout.write(f"    Set opening hours for {venue.name}")
