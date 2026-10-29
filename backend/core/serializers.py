"""
Public-facing serializers for City and Venue.

Every serializer here lists its fields explicitly — never `fields = "__all__"`
— so partner_tier and square_location_id can't leak onto a public endpoint
by accident when a field is later added to the model.
"""

from rest_framework import serializers

from .models import City, Venue, VenuePhoto


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["name", "slug", "state", "intro", "map_center_lat", "map_center_lng", "map_zoom"]


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

    class Meta:
        model = City
        fields = ["name", "slug", "state", "intro", "map_center_lat", "map_center_lng", "map_zoom", "venues"]

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
            "hours",
            "website_url",
            "instagram_handle",
        ]
