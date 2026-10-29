"""
Public read-only API views: cities and venues.

Every queryset here is restricted to public data — active cities and
venues in PUBLIC_VENUE_STATUSES — at the queryset level, not just in the
serializer, so there's no path (filtering, ordering, etc.) that leaks a
paused venue or an inactive city.
"""

from django.http import Http404
from django_filters import rest_framework as filters
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .constants import PUBLIC_VENUE_STATUSES
from .models import City, Venue
from .serializers import (
    CityDetailSerializer,
    CitySerializer,
    VenueCardSerializer,
    VenueDetailSerializer,
)


class CityListView(ListAPIView):
    serializer_class = CitySerializer
    queryset = City.objects.filter(is_active=True)


class CityDetailView(RetrieveAPIView):
    serializer_class = CityDetailSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "city_slug"
    queryset = City.objects.filter(is_active=True)


class VenueFilterSet(filters.FilterSet):
    city = filters.CharFilter(field_name="city__slug")

    class Meta:
        model = Venue
        fields = ["city"]


class VenueListView(ListAPIView):
    serializer_class = VenueCardSerializer
    filterset_class = VenueFilterSet

    def get_queryset(self):
        # city__is_active=True: a venue in an inactive city is never public,
        # even though the venue's own status might otherwise qualify.
        return (
            Venue.objects.filter(status__in=PUBLIC_VENUE_STATUSES, city__is_active=True)
            .order_by("display_order", "name")
        )


class VenueDetailView(RetrieveAPIView):
    serializer_class = VenueDetailSerializer

    def get_queryset(self):
        return Venue.objects.filter(status__in=PUBLIC_VENUE_STATUSES, city__is_active=True)

    def get_object(self):
        queryset = self.get_queryset()
        try:
            return queryset.get(
                city__slug=self.kwargs["city_slug"], slug=self.kwargs["venue_slug"]
            )
        except Venue.DoesNotExist:
            raise Http404
