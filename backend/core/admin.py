from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import admin, messages
from django.db import transaction
from django.utils.html import format_html

from . import revalidation
from .admin_forms import CoordinatePasteFormMixin, RoundedDecimalField
from .models import City, OpeningHours, Venue, VenuePhoto
from .seo import DESCRIPTION_SOFT_LIMIT, TITLE_SOFT_LIMIT, truncate_at_word


class SEOAdminMixin:
    """Adds the "SEO" section (fields from core/seo.py's SEOFieldsMixin)
    with live character counters and a Google-result preview. The
    counters and live updating are core/static/core/admin/seo.js; this
    class renders the preview's starting state (including the automatic
    fallback values, which the script shows whenever a field is blank).

    Reuse on any admin whose model uses SEOFieldsMixin: subclass it and
    add SEO_FIELDSET to the fieldsets.
    """

    SEO_FIELDSET = (
        "SEO",
        {
            "fields": (
                "seo_preview",
                "seo_title",
                "meta_description",
                "target_phrases",
                "og_image",
                "noindex",
                "canonical_url",
            ),
            "classes": ("collapse",),
            "description": "Everything here is optional — leave a field blank to use the automatic "
            "value shown in the preview.",
        },
    )

    class Media:
        js = ("core/admin/seo.js",)
        css = {"all": ("core/admin/seo.css",)}

    def get_readonly_fields(self, request, obj=None):
        return (*super().get_readonly_fields(request, obj), "seo_preview")

    @admin.display(description="Google preview")
    def seo_preview(self, obj):
        saved = obj is not None and obj.pk is not None
        automatic = "(automatic — shown after saving)"
        # The automatic values, which the script shows whenever the
        # matching field is blank.
        fallback_title = obj.default_seo_title() if saved else automatic
        fallback_description = (
            truncate_at_word(obj.default_meta_description()) if saved else automatic
        )

        return format_html(
            '<div class="seo-preview" data-fallback-title="{}" data-fallback-description="{}" '
            'data-title-limit="{}" data-description-limit="{}">'
            '<div class="seo-preview__url">{}</div>'
            '<div class="seo-preview__title">{}</div>'
            '<div class="seo-preview__description">{}</div>'
            '<div class="seo-preview__noindex">Hidden from search engines — Google won\'t list this page.</div>'
            "</div>",
            fallback_title,
            fallback_description,
            TITLE_SOFT_LIMIT,
            DESCRIPTION_SOFT_LIMIT,
            self._preview_url(obj) if saved else "",
            obj.resolved_seo_title() if saved else automatic,
            obj.resolved_meta_description() if saved else automatic,
        )

    @staticmethod
    def _preview_url(obj):
        """Google-style breadcrumb URL, e.g. "forksandfarms.com › locations
        › st-louis". Just the path if PUBLIC_SITE_URL isn't set."""
        path = obj.public_path()
        site = urlsplit(settings.PUBLIC_SITE_URL).netloc if settings.PUBLIC_SITE_URL else ""
        parts = [site, *path.strip("/").split("/")] if site else [path]
        return " › ".join(part for part in parts if part)


@admin.action(description="Refresh live site pages")
def refresh_live_site_pages(modeladmin, request, queryset):
    """Manually ask the Next.js site to rebuild the selected cities'/
    venues' pages — handy if an automatic refresh after a save was missed
    (e.g. the site was briefly down). Unlike the automatic refresh this
    waits for the answer, so it can say whether it worked."""
    paths = set()
    for obj in queryset:
        if isinstance(obj, City):
            paths |= revalidation.paths_for_city(obj)
        else:
            paths |= revalidation.paths_for_venue(obj)

    ok, message = revalidation.send_revalidation(
        sorted(paths), timeout=revalidation.ADMIN_ACTION_TIMEOUT_SECONDS
    )
    modeladmin.message_user(request, message, level=messages.SUCCESS if ok else messages.ERROR)


class CityAdminForm(CoordinatePasteFormMixin):
    lat_field_name = "map_center_lat"
    lng_field_name = "map_center_lng"

    map_center_lat = RoundedDecimalField(max_digits=10, decimal_places=7, required=False)
    map_center_lng = RoundedDecimalField(max_digits=10, decimal_places=7, required=False)

    class Meta:
        model = City
        fields = "__all__"


@admin.register(City)
class CityAdmin(SEOAdminMixin, admin.ModelAdmin):
    form = CityAdminForm
    list_display = ("name", "state", "timezone", "is_active")
    list_filter = ("is_active", "state")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    actions = [refresh_live_site_pages]
    fieldsets = (
        (None, {"fields": ("name", "slug", "state", "intro", "is_active")}),
        (
            "Map",
            {
                "fields": (
                    "paste_coordinates",
                    ("map_center_lat", "map_center_lng"),
                    "map_zoom",
                    "timezone",
                )
            },
        ),
        SEOAdminMixin.SEO_FIELDSET,
    )


class VenuePhotoInline(admin.TabularInline):
    model = VenuePhoto
    extra = 1
    fields = ("image", "alt_text", "order")


class OpeningHoursInline(admin.TabularInline):
    model = OpeningHours
    # extra=0: every venue already has its 7 baseline rows (post_save
    # signal for new venues, the 0003 data migration for old ones) —
    # "Add another" still lets the admin add split-hours rows by hand.
    extra = 0
    fields = ("weekday", "is_closed", "open_time", "close_time", "order")
    ordering = ("weekday", "order")


@admin.action(description="Copy Monday's hours to all days")
def copy_monday_to_all_days(modeladmin, request, queryset):
    """For each selected venue, clear Tue-Sun and clone Monday's row(s)
    (handles split hours) onto every other day — including whether
    Monday is closed or still unset, not just its times."""
    updated = 0
    skipped = 0
    for venue in queryset:
        monday_rows = list(
            venue.opening_hours.filter(weekday=OpeningHours.Weekday.MONDAY).order_by("order")
        )
        if not monday_rows:
            skipped += 1
            continue

        new_rows = [
            OpeningHours(
                venue=venue,
                weekday=weekday,
                is_closed=row.is_closed,
                open_time=row.open_time,
                close_time=row.close_time,
                order=row.order,
            )
            for weekday in OpeningHours.Weekday.values
            if weekday != OpeningHours.Weekday.MONDAY
            for row in monday_rows
        ]
        # One transaction per venue: never left half-copied, and the
        # live-site refresh only goes out once the new rows are in place.
        # (bulk_create sends no signals, so ask for the refresh directly.)
        with transaction.atomic():
            venue.opening_hours.exclude(weekday=OpeningHours.Weekday.MONDAY).delete()
            OpeningHours.objects.bulk_create(new_rows)
            revalidation.request_revalidation(revalidation.paths_for_venue(venue))
        updated += 1

    if updated:
        modeladmin.message_user(request, f"Copied Monday's hours to all days for {updated} venue(s).")
    if skipped:
        modeladmin.message_user(
            request,
            f"Skipped {skipped} venue(s) with no Monday row (shouldn't normally happen).",
            level=messages.WARNING,
        )


class VenueAdminForm(CoordinatePasteFormMixin):
    lat_field_name = "latitude"
    lng_field_name = "longitude"

    latitude = RoundedDecimalField(max_digits=10, decimal_places=7, required=False)
    longitude = RoundedDecimalField(max_digits=10, decimal_places=7, required=False)

    class Meta:
        model = Venue
        fields = "__all__"


@admin.register(Venue)
class VenueAdmin(SEOAdminMixin, admin.ModelAdmin):
    form = VenueAdminForm
    list_display = ("name", "city", "neighborhood", "status", "partner_tier", "display_order")
    list_filter = ("city", "status", "partner_tier")
    search_fields = ("name", "neighborhood")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [OpeningHoursInline, VenuePhotoInline]
    actions = [copy_monday_to_all_days, refresh_live_site_pages]
    readonly_fields = ("google_maps_link",)
    fieldsets = (
        (None, {"fields": ("city", "name", "slug", "neighborhood", "venue_type")}),
        ("Status & partnership", {"fields": ("status", "partner_tier", "display_order")}),
        (
            "Location",
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    "postal_code",
                    "paste_coordinates",
                    ("latitude", "longitude"),
                    "google_maps_link",
                )
            },
        ),
        (
            "Details",
            {
                "fields": ("hours", "website_url", "instagram_handle"),
                "description": (
                    '"hours" (the old free-text field) is kept temporarily for backward '
                    "compatibility — enter real hours in the Opening hours section below instead."
                ),
            },
        ),
        ("Content", {"fields": ("short_description", "setup_description", "hero_image")}),
        SEOAdminMixin.SEO_FIELDSET,
        ("Phase II (do not use yet)", {"fields": ("square_location_id",), "classes": ("collapse",)}),
    )

    @admin.display(description="Google Maps")
    def google_maps_link(self, obj):
        # obj is None on the add form (nothing saved/pasted yet to link to).
        if not obj or obj.latitude is None or obj.longitude is None:
            return "— save first —"
        url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">View on Google Maps →</a>', url
        )
