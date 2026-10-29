"""
Seed St. Louis + the 4 current partner venues with placeholder content.

Safe to re-run: every record is looked up by its natural key (city slug,
or (city, venue slug)) and updated in place rather than duplicated.

Usage: python manage.py seed_demo_data
"""

from django.core.management.base import BaseCommand

from core.models import City, Venue

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


class Command(BaseCommand):
    help = "Seed (or update) St. Louis and the 4 current partner venues with placeholder content."

    def handle(self, *args, **options):
        city, created = City.objects.update_or_create(
            slug="st-louis",
            defaults={
                "name": "St. Louis",
                "state": "MO",
                "intro": "TODO(copy): one-line intro for the St. Louis locations page.",
                "map_center_lat": "38.627000",
                "map_center_lng": "-90.199400",
                "map_zoom": 12,
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

        self.stdout.write(self.style.SUCCESS("Seed complete."))
