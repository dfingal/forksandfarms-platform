from django.contrib import admin

from django.contrib import messages

from core.models import City, Venue

from .models import PartnerApplication


@admin.action(description="Create Venue from application")
def create_venue_from_application(modeladmin, request, queryset):
    """Pre-fill a draft Venue (status=coming_soon) from each selected application.

    Only city/name/address/slug/partner_tier can be guessed here; the owner
    still needs to open the new draft Venue in admin to set neighborhood,
    coordinates, hero image, and finished copy before it can go live.
    """
    default_city = City.objects.order_by("name").first()
    if default_city is None:
        modeladmin.message_user(
            request, "Add a City in admin first — can't create a Venue without one.", messages.ERROR
        )
        return

    created = 0
    for application in queryset:
        if application.converted_venue_id:
            continue  # already converted; don't create a duplicate
        base_slug = application.venue_name.lower().replace(" ", "-")[:50] or "venue"
        slug = base_slug
        suffix = 1
        while Venue.objects.filter(city=default_city, slug=slug).exists():
            suffix += 1
            slug = f"{base_slug}-{suffix}"

        venue = Venue.objects.create(
            city=default_city,
            name=application.venue_name,
            slug=slug,
            neighborhood="TODO: set neighborhood",
            venue_type=application.venue_type,
            status=Venue.Status.COMING_SOON,
            partner_tier=(
                application.interested_tiers[0]
                if application.interested_tiers
                and application.interested_tiers[0] in Venue.PartnerTier.values
                else Venue.PartnerTier.RETAIL_SHELF
            ),
            address_line1=application.address,
            postal_code="",
            latitude=default_city.map_center_lat,
            longitude=default_city.map_center_lng,
            short_description="TODO(copy): add a short description.",
            setup_description="TODO(copy): add the plant setup description.",
        )
        application.converted_venue = venue
        application.status = PartnerApplication.Status.SIGNED
        application.save(update_fields=["converted_venue", "status"])
        created += 1
    if created:
        modeladmin.message_user(request, f"Created {created} draft venue(s) — finish setup in Venues.")
    else:
        modeladmin.message_user(request, "Nothing to do — selected applications already converted.")


@admin.register(PartnerApplication)
class PartnerApplicationAdmin(admin.ModelAdmin):
    list_display = ("venue_name", "contact_name", "email", "status", "created_at")
    list_filter = ("status", "venue_type", "interested_tiers")
    search_fields = ("contact_name", "email", "venue_name")
    list_editable = ("status",)
    readonly_fields = ("source_ip", "created_at", "updated_at")
    actions = [create_venue_from_application]
