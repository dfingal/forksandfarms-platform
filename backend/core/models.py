"""
Core models: City, Venue, VenuePhoto, OpeningHours.

See docs/phase1-spec.md §4 for field definitions and rationale.
"""

from zoneinfo import available_timezones

from django.core.exceptions import ValidationError
from django.db import models

from .seo import SEOFieldsMixin


def validate_timezone(value):
    if value not in available_timezones():
        raise ValidationError(f"{value!r} is not a known IANA timezone name.")


class TimestampedModel(models.Model):
    """Adds created_at/updated_at to every model, per CLAUDE.md convention."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class City(SEOFieldsMixin, TimestampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    state = models.CharField(max_length=2)
    intro = models.TextField(blank=True, help_text="One-liner shown on the city page.")
    # 7 decimal places matches the precision Google Maps copies/pastes give
    # (max_digits=10 covers the full +/-180.0000000 longitude range).
    map_center_lat = models.DecimalField(max_digits=10, decimal_places=7)
    map_center_lng = models.DecimalField(max_digits=10, decimal_places=7)
    map_zoom = models.PositiveSmallIntegerField(default=12)
    timezone = models.CharField(
        max_length=64,
        default="America/Chicago",
        validators=[validate_timezone],
        help_text="IANA timezone name, e.g. America/Chicago. Used to work out "
        "venues' current-day opening hours.",
    )
    is_active = models.BooleanField(
        default=True, help_text="Hidden from the public site if unchecked."
    )

    class Meta:
        verbose_name_plural = "cities"
        ordering = ["name"]

    def __str__(self):
        return self.name

    # SEO fallbacks (see core/seo.py)
    def default_seo_title(self):
        return f"Forks And Farms in {self.name}"

    def default_meta_description(self):
        return self.intro or f"Find Forks And Farms plant locations in {self.name}."

    def public_path(self):
        return f"/locations/{self.slug}"


class Venue(SEOFieldsMixin, TimestampedModel):
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
    # See City.map_center_lat for why max_digits=10, decimal_places=7.
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    # TODO(release): superseded by the OpeningHours model (structured,
    # per-day, supports split/overnight hours). Kept and still served by
    # the API for backward compatibility — drop this field once nothing
    # still reads it.
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

    # SEO fallbacks (see core/seo.py)
    def default_seo_title(self):
        return f"Plants at {self.name} · Forks And Farms"

    def default_meta_description(self):
        if self.short_description:
            return f"{self.neighborhood} — {self.short_description}"
        return f"Find Forks And Farms plants at {self.name} in {self.neighborhood}."

    def default_og_image(self):
        return self.hero_image or None

    def public_path(self):
        return f"/locations/{self.city.slug}/{self.slug}"


class OpeningHours(TimestampedModel):
    """One time range for one weekday of one venue.

    A day can have more than one row (split hours, e.g. 11-2 and 5-9) —
    `order` controls which comes first. Every venue is meant to always
    have exactly 7 "baseline" rows (one per weekday, created by the
    post_save signal below or the 0004 data migration); split hours just
    mean extra rows sharing the same weekday.

    Three states per row, not two:
    - is_closed=True (times blank): explicitly closed that day.
    - is_closed=False, both times blank: not set yet — a placeholder,
      NOT the same as closed. The admin/API/frontend must all treat
      this as "we don't know", never as "closed".
    - is_closed=False, both times set: open for that range.
    """

    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="opening_hours")
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    is_closed = models.BooleanField(default=False)
    open_time = models.TimeField(
        null=True, blank=True, help_text="Leave blank (with Closed unchecked) if not yet known."
    )
    close_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Earlier than open time means open past midnight (e.g. 6pm-2am).",
    )
    order = models.PositiveSmallIntegerField(
        default=0, help_text="For split hours (multiple ranges the same day) — lower shows first."
    )

    class Meta:
        verbose_name_plural = "opening hours"
        ordering = ["weekday", "order"]

    @property
    def is_unset(self):
        return not self.is_closed and self.open_time is None and self.close_time is None

    def clean(self):
        if self.is_closed:
            if self.open_time is not None or self.close_time is not None:
                raise ValidationError("A closed day shouldn't have open/close times set.")
            return

        has_open = self.open_time is not None
        has_close = self.close_time is not None
        if has_open != has_close:
            raise ValidationError(
                "Set both open and close time, or leave both blank if not yet known."
            )
        if has_open and has_close and self.open_time == self.close_time:
            # Deliberately not supporting "24 hours" via equal times — too
            # ambiguous with the placeholder/unset state. Not expected in
            # Phase I; revisit if a venue genuinely needs 24-hour hours.
            raise ValidationError("Open and close time can't be identical.")

    def __str__(self):
        label = self.get_weekday_display()
        if self.is_closed:
            return f"{self.venue.name} — {label}: Closed"
        if self.is_unset:
            return f"{self.venue.name} — {label}: (not set)"
        return f"{self.venue.name} — {label}: {self.open_time}–{self.close_time}"


class VenuePhoto(TimestampedModel):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="venues/gallery/")
    alt_text = models.CharField(max_length=200, help_text="Required for accessibility.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Photo for {self.venue.name} (#{self.order})"
