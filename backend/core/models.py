"""
Core models: City, Venue, VenuePhoto.

See docs/phase1-spec.md §4 for field definitions and rationale.
"""

from django.db import models


class TimestampedModel(models.Model):
    """Adds created_at/updated_at to every model, per CLAUDE.md convention."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class City(TimestampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    state = models.CharField(max_length=2)
    intro = models.TextField(blank=True, help_text="One-liner shown on the city page.")
    map_center_lat = models.DecimalField(max_digits=9, decimal_places=6)
    map_center_lng = models.DecimalField(max_digits=9, decimal_places=6)
    map_zoom = models.PositiveSmallIntegerField(default=12)
    is_active = models.BooleanField(
        default=True, help_text="Hidden from the public site if unchecked."
    )

    class Meta:
        verbose_name_plural = "cities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Venue(TimestampedModel):
    class VenueType(models.TextChoices):
        COFFEE_SHOP = "coffee_shop", "Coffee shop"
        RESTAURANT = "restaurant", "Restaurant"
        BAR = "bar", "Bar"
        WINE_BAR = "wine_bar", "Wine bar"
        BREWERY = "brewery", "Brewery"
        RETAIL = "retail", "Retail"
        HOTEL = "hotel", "Hotel"
        LIBRARY = "library", "Library"
        OFFICE = "office", "Office"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SEASONAL = "seasonal", "Seasonal"
        COMING_SOON = "coming_soon", "Coming soon"
        PAUSED = "paused", "Paused"  # hidden from every public endpoint/page

    class PartnerTier(models.TextChoices):
        RETAIL_SHELF = "retail_shelf", "Retail shelf"
        DESIGN_INSTALL = "design_install", "Design & install"
        LEASE_MAINTENANCE = "lease_maintenance", "Lease + maintenance"

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="venues")
    name = models.CharField(max_length=150)
    slug = models.SlugField()
    neighborhood = models.CharField(max_length=100)
    venue_type = models.CharField(max_length=20, choices=VenueType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMING_SOON)
    # Internal only — never serialize this on a public endpoint (spec §5).
    partner_tier = models.CharField(max_length=20, choices=PartnerTier.choices)

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    hours = models.JSONField(
        default=dict,
        blank=True,
        help_text='e.g. {"mon": "7:00–18:00", ...} or {"display": "Mon–Fri 7–6"}',
    )
    website_url = models.URLField(blank=True)
    instagram_handle = models.CharField(max_length=100, blank=True)

    short_description = models.CharField(max_length=280, help_text="Used on cards.")
    setup_description = models.TextField(help_text='Body copy for "The plant setup" section.')
    hero_image = models.ImageField(
        upload_to="venues/hero/",
        blank=True,
        help_text="Required before a venue goes public; left blank on draft venues from applications.",
    )

    display_order = models.PositiveIntegerField(default=0, help_text="Lower shows first.")

    # Phase II hook (Square catalog/inventory). Leave blank in Phase I — do
    # not build anything that reads or writes this field yet.
    square_location_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ("city", "slug")
        ordering = ["display_order", "name"]

    def __str__(self):
        return f"{self.name} ({self.city.name})"


class VenuePhoto(TimestampedModel):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="venues/gallery/")
    alt_text = models.CharField(max_length=200, help_text="Required for accessibility.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Photo for {self.venue.name} (#{self.order})"
