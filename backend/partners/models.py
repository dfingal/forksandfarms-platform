"""
PartnerApplication model — submitted via the /partner form.

See docs/phase1-spec.md §4.4. Never exposed on any public GET endpoint.
"""

from django.db import models

from core.models import TimestampedModel, Venue


class PartnerApplication(TimestampedModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        WALKTHROUGH_SCHEDULED = "walkthrough_scheduled", "Walkthrough scheduled"
        PROPOSAL_SENT = "proposal_sent", "Proposal sent"
        SIGNED = "signed", "Signed"
        DECLINED = "declined", "Declined"

    class InterestedTier(models.TextChoices):
        RETAIL_SHELF = "retail_shelf", "Retail shelf"
        DESIGN_INSTALL = "design_install", "Design & install"
        LEASE_MAINTENANCE = "lease_maintenance", "Lease + maintenance"
        NOT_SURE = "not_sure", "Not sure yet"

    contact_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)

    venue_name = models.CharField(max_length=150)
    # Same choices as Venue.VenueType (spec §4.4) — kept independent here
    # since an application isn't a Venue yet.
    venue_type = models.CharField(max_length=20, choices=Venue.VenueType.choices)
    address = models.CharField(max_length=255)
    space_description = models.CharField(
        max_length=255, blank=True, help_text="Approx. space or number of plants."
    )
    interested_tiers = models.JSONField(
        default=list, help_text="Any of: retail_shelf, design_install, lease_maintenance, not_sure"
    )
    referral_source = models.CharField(
        max_length=150, blank=True, help_text="How did you hear about us?"
    )
    notes = models.TextField(blank=True)

    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NEW)
    internal_notes = models.TextField(blank=True, help_text="Admin only.")
    converted_venue = models.ForeignKey(
        Venue, on_delete=models.SET_NULL, null=True, blank=True, related_name="source_applications"
    )
    source_ip = models.GenericIPAddressField(null=True, blank=True, help_text="For spam review.")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.venue_name} — {self.contact_name}"
