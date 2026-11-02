from django.contrib import admin
from django.utils.html import format_html

from .admin_forms import CoordinatePasteFormMixin, RoundedDecimalField
from .models import City, Venue, VenuePhoto


class CityAdminForm(CoordinatePasteFormMixin):
    lat_field_name = "map_center_lat"
    lng_field_name = "map_center_lng"

    map_center_lat = RoundedDecimalField(max_digits=10, decimal_places=7, required=False)
    map_center_lng = RoundedDecimalField(max_digits=10, decimal_places=7, required=False)

    class Meta:
        model = City
        fields = "__all__"


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityAdminForm
    list_display = ("name", "state", "is_active")
    list_filter = ("is_active", "state")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "state", "intro", "is_active")}),
        (
            "Map",
            {
                "fields": (
                    "paste_coordinates",
                    ("map_center_lat", "map_center_lng"),
                    "map_zoom",
                )
            },
        ),
    )


class VenuePhotoInline(admin.TabularInline):
    model = VenuePhoto
    extra = 1
    fields = ("image", "alt_text", "order")


class VenueAdminForm(CoordinatePasteFormMixin):
    lat_field_name = "latitude"
    lng_field_name = "longitude"

    latitude = RoundedDecimalField(max_digits=10, decimal_places=7, required=False)
    longitude = RoundedDecimalField(max_digits=10, decimal_places=7, required=False)

    class Meta:
        model = Venue
        fields = "__all__"


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    form = VenueAdminForm
    list_display = ("name", "city", "neighborhood", "status", "partner_tier", "display_order")
    list_filter = ("city", "status", "partner_tier")
    search_fields = ("name", "neighborhood")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [VenuePhotoInline]
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
        ("Details", {"fields": ("hours", "website_url", "instagram_handle")}),
        ("Content", {"fields": ("short_description", "setup_description", "hero_image")}),
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
