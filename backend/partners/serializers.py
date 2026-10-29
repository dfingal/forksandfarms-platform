"""
Serializer for the public partner-application POST.

Only visitor-supplied fields are writable. status, internal_notes,
converted_venue, source_ip are server/admin-only and never appear here.
"""

from rest_framework import serializers

from .integrations import verify_turnstile
from .models import PartnerApplication


class PartnerApplicationCreateSerializer(serializers.ModelSerializer):
    # Not a model field — consumed in validate()/create(), stripped before save.
    turnstile_token = serializers.CharField(write_only=True)

    class Meta:
        model = PartnerApplication
        fields = [
            "contact_name",
            "email",
            "phone",
            "venue_name",
            "venue_type",
            "address",
            "space_description",
            "interested_tiers",
            "referral_source",
            "notes",
            "turnstile_token",
        ]

    def validate_interested_tiers(self, value):
        allowed = set(PartnerApplication.InterestedTier.values)
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Select at least one option.")
        invalid = set(value) - allowed
        if invalid:
            raise serializers.ValidationError(
                f"Invalid value(s): {', '.join(sorted(invalid))}. Allowed: {', '.join(sorted(allowed))}."
            )
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        remote_ip = getattr(request, "client_ip", None) if request else None
        if not verify_turnstile(attrs.get("turnstile_token"), remote_ip=remote_ip):
            raise serializers.ValidationError({"turnstile_token": "Verification failed."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("turnstile_token", None)
        return PartnerApplication.objects.create(**validated_data)
