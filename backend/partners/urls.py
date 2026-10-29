from django.urls import path

from . import views

urlpatterns = [
    path(
        "partner-applications/",
        views.PartnerApplicationCreateView.as_view(),
        name="partner-application-create",
    ),
]
