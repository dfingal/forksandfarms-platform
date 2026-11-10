"""
Public-facing serializers for City and Venue.

Every serializer here lists its fields explicitly — never `fields = "__all__"`
— so partner_tier and square_location_id can't leak onto a public endpoint
by accident when a field is later added to the model.
"""

from rest_framework import serializers

from .models import City, OpeningHours, Venue, VenuePhoto
from .seo import seo_payload


class SEOField(serializers.Field):
    """The public `seo` object (core/seo.py) — resolved title,
    description, share image, canonical and noindex, with fallbacks
    already applied. Never includes target_phrases."""

    def __init__(self, **kwargs):
        super().__init__(source="*", read_only=True, **kwargs)

    def to_representation(self, obj):
        return seo_payload(obj, self.context.get("request"))


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            "name",
            "slug",
            "state",
            "intro",
            "map_center_lat",
            "map_center_lng",
            "map_zoom",
            "timezone",
        ]


class VenueCardSerializer(serializers.ModelSerializer):
    """Card fields only — used in list endpoints and nested under a City."""

    city = serializers.SlugField(source="city.slug", read_only=True)
    hero_image = serializers.ImageField(use_url=True)

    class Meta:
        model = Venue
        fields = [
            "id",
            "name",
            "slug",
            "city",
            "neighborhood",
            "status",
            "short_description",
            "hero_image",
            "latitude",
            "longitude",
        ]


class CityDetailSerializer(serializers.ModelSerializer):
    """City + its public venues (card fields), for GET /cities/{slug}/."""

    venues = serializers.SerializerMethodField()
    seo = SEOField()

    class Meta:
        model = City
        fields = [
            "name",
            "slug",
            "state",
            "intro",
            "map_center_lat",
            "map_center_lng",
            "map_zoom",
            "timezone",
            "venues",
            "seo",
        ]

    def get_venues(self, city):
        from core.constants import PUBLIC_VENUE_STATUSES

        queryset = city.venues.filter(status__in=PUBLIC_VENUE_STATUSES).order_by("display_order", "name")
        return VenueCardSerializer(queryset, many=True, context=self.context).data


class VenuePhotoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = VenuePhoto
        fields = ["image", "alt_text", "order"]


class VenueDetailSerializer(serializers.ModelSerializer):
    """Full venue detail: card fields + hours, website, photos, setup copy."""

    city = serializers.SlugField(source="city.slug", read_only=True)
    hero_image = serializers.ImageField(use_url=True)
    photos = VenuePhotoSerializer(many=True, read_only=True)
    opening_hours = serializers.SerializerMethodField()
    seo = SEOField()

    class Meta:
        model = Venue
        fields = [
            "id",
            "name",
            "slug",
            "city",
            "neighborhood",
            "status",
            "short_description",
            "setup_description",
            "hero_image",
            "photos",
            "latitude",
            "longitude",
            "address_line1",
            "address_line2",
            "postal_code",
            # TODO(release): drop once nothing reads it — see the TODO on
            # Venue.hours itself. opening_hours (below) is the real data now.
            "hours",
            "opening_hours",
            "website_url",
            "instagram_handle",
            "seo",
        ]

    def get_opening_hours(self, venue):
        """One entry per weekday, in order. A day is "closed" only if a
        row explicitly says so (is_closed=True) — a day with no times
        and is_closed=False is unset, not closed, and comes back the
        same way: is_closed=False with an empty ranges list. The
        frontend is responsible for telling those two apart (it must
        NOT render an unset day as "Closed")."""
        rows_by_weekday = {}
        for row in venue.opening_hours.order_by("weekday", "order"):
            rows_by_weekday.setdefault(row.weekday, []).append(row)

        result = []
        for weekday, label in OpeningHours.Weekday.choices:
            day_rows = rows_by_weekday.get(weekday, [])
            is_closed = any(r.is_closed for r in day_rows)
            ranges = (
                []
                if is_closed
                else [
                    {"open": r.open_time.strftime("%H:%M"), "close": r.close_time.strftime("%H:%M")}
                    for r in day_rows
                    if r.open_time is not None and r.close_time is not None
                ]
            )
            result.append({"day": label, "is_closed": is_closed, "ranges": ranges})
        return result
