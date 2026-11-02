"""
Admin-only form helpers for entering coordinates.

Two problems these solve:
1. Google Maps gives coordinates with more than 6-7 decimal places when
   you copy them — the plain DecimalField admin widget would reject that
   outright. RoundedDecimalField rounds to COORD_DECIMAL_PLACES before
   Django's own digit-count validation runs, so it's just accepted.
2. Copying lat/lng separately into two fields is fiddly. CoordinatePasteFormMixin
   adds one "paste coordinates" box that accepts "lat, lng" (in whatever
   loose formatting Google Maps' own copy button gives you) and fills in
   both real fields.
"""

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from django import forms

COORD_DECIMAL_PLACES = 7
COORD_QUANTIZE = Decimal(1).scaleb(-COORD_DECIMAL_PLACES)  # Decimal("0.0000001")


def round_coordinate(value):
    """Round a Decimal to COORD_DECIMAL_PLACES using half-up rounding."""
    return value.quantize(COORD_QUANTIZE, rounding=ROUND_HALF_UP)


class RoundedDecimalField(forms.DecimalField):
    """A DecimalField that rounds its input to COORD_DECIMAL_PLACES before
    validating max_digits/decimal_places, instead of rejecting values with
    more decimal places than that (which is exactly what pasting straight
    from Google Maps gives you)."""

    def to_python(self, value):
        value = super().to_python(value)
        if value is not None:
            value = round_coordinate(value)
        return value


# Matches "lat, lng" tolerantly: optional surrounding parentheses/whitespace,
# a comma with or without a following space, either number optionally signed
# or decimal. Two capture groups are the raw number strings.
_COORD_PAIR_RE = re.compile(
    r"^\(?\s*([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)\s*\)?$"
)


class CoordinatePasteFormMixin(forms.ModelForm):
    """Adds a "Paste coordinates" field that fills in two real model
    fields from a single "lat, lng" string (as Google Maps' own "Copy
    coordinates" gives you, parentheses and all).

    Subclasses set lat_field_name / lng_field_name to the real field
    names on their model, and should also give those two fields the
    RoundedDecimalField class with required=False (so leaving them blank
    to paste instead doesn't trip Django's own "required" check before
    this mixin's clean() gets a chance to fill them in).
    """

    lat_field_name = "latitude"
    lng_field_name = "longitude"

    paste_coordinates = forms.CharField(
        required=False,
        label="Paste coordinates",
        help_text='Paste "lat, lng" as copied from Google Maps to fill in both fields below.',
    )

    def clean(self):
        cleaned_data = super().clean()
        raw = (cleaned_data.get("paste_coordinates") or "").strip()

        if raw:
            match = _COORD_PAIR_RE.match(raw)
            if not match:
                self.add_error(
                    "paste_coordinates",
                    'Enter coordinates as "lat, lng" (e.g. "38.6270, -90.1994").',
                )
                return cleaned_data

            try:
                lat = Decimal(match.group(1))
                lng = Decimal(match.group(2))
            except InvalidOperation:
                self.add_error("paste_coordinates", "Those don't look like valid numbers.")
                return cleaned_data

            if not (-90 <= lat <= 90):
                self.add_error("paste_coordinates", "Latitude must be between -90 and 90.")
                return cleaned_data
            if not (-180 <= lng <= 180):
                self.add_error("paste_coordinates", "Longitude must be between -180 and 180.")
                return cleaned_data

            # Pasting overrides whatever was typed directly into the two
            # fields below, if anything.
            cleaned_data[self.lat_field_name] = round_coordinate(lat)
            cleaned_data[self.lng_field_name] = round_coordinate(lng)
            return cleaned_data

        # No paste attempted — the two real fields are still required,
        # just enforced here instead of at the field level (they're
        # required=False on the field itself so a paste can fill them in
        # without tripping that check first).
        for field_name in (self.lat_field_name, self.lng_field_name):
            if cleaned_data.get(field_name) in (None, ""):
                self.add_error(field_name, "This field is required.")
        return cleaned_data
