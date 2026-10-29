from django.contrib import admin

from .models import City, Venue, VenuePhoto


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "is_active")
    list_filter = ("is_active", "state")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class VenuePhotoInline(admin.TabularInline):
    model = VenuePhoto
    extra = 1
    fields = ("image", "alt_text", "order")


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "neighborhood", "status", "partner_tier", "display_order")
    list_filter = ("city", "status", "partner_tier")
    search_fields = ("name", "neighborhood")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [VenuePhotoInline]
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
                    ("latitude", "longitude"),
                )
            },
        ),
        ("Details", {"fields": ("hours", "website_url", "instagram_handle")}),
        ("Content", {"fields": ("short_description", "setup_description", "hero_image")}),
        ("Phase II (do not use yet)", {"fields": ("square_location_id",), "classes": ("collapse",)}),
    )
