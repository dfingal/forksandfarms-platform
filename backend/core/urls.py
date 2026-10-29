from django.urls import path

from . import views

urlpatterns = [
    path("cities/", views.CityListView.as_view(), name="city-list"),
    path("cities/<slug:city_slug>/", views.CityDetailView.as_view(), name="city-detail"),
    path("venues/", views.VenueListView.as_view(), name="venue-list"),
    path(
        "cities/<slug:city_slug>/venues/<slug:venue_slug>/",
        views.VenueDetailView.as_view(),
        name="venue-detail",
    ),
]
