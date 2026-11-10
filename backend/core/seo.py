"""
Admin-editable SEO metadata (docs/seo-plan.md).

SEOFieldsMixin adds optional SEO fields to a model. Every field can be
left blank: the public API then falls back to automatic values built
from the model's own content. Each model using the mixin supplies those
fallbacks by overriding the three default_* methods (and public_path),
which is all Neighborhood/Tag will need to reuse this later.

Never exposed publicly: target_phrases (a note to help write copy).
seo_payload() below builds the one public shape — use it rather than
serializing the fields directly.
"""

from django.db import models

# Soft limits: roughly what Google shows before cutting text off. Going
# over only shows a warning in admin (core/static/core/admin/seo.js).
TITLE_SOFT_LIMIT = 60
DESCRIPTION_SOFT_LIMIT = 160


def truncate_at_word(text, limit=DESCRIPTION_SOFT_LIMIT):
    """Shorten `text` to at most `limit` characters without cutting a
    word in half, adding "…" when anything was removed."""
    text = " ".join(text.split())  # collapse newlines/double spaces
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]  # leave room for the "…"
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:—-") + "…"


class SEOFieldsMixin(models.Model):
    seo_title = models.CharField(
        "SEO title",
        max_length=200,
        blank=True,
        help_text=f"Shown as the page title in Google and browser tabs. Used exactly as written, "
        f'so include "Forks And Farms" yourself. Aim for about {TITLE_SOFT_LIMIT} characters. '
        "Leave blank for an automatic title.",
    )
    meta_description = models.CharField(
        max_length=320,
        blank=True,
        help_text=f"The snippet under the title in Google. Aim for about {DESCRIPTION_SOFT_LIMIT} "
        "characters. Leave blank for an automatic description.",
    )
    og_image = models.ImageField(
        "share image",
        upload_to="seo/",
        blank=True,
        help_text="Recommended 1200 × 630 px, landscape JPG/PNG. Shown when the page is shared "
        "on social media or in messages. Leave blank to use the automatic image.",
    )
    # Internal only — never serialize this (see seo_payload below).
    target_phrases = models.TextField(
        blank=True,
        help_text="Internal note, never published: phrases people might search for "
        '(e.g. "plants for sale near Tower Grove"). Use them as a guide when writing the '
        "title and description.",
    )
    noindex = models.BooleanField(
        "hide from search engines",
        default=False,
        help_text="Asks Google & co. not to list this page. It stays on the site and is still "
        "linked from other pages.",
    )
    canonical_url = models.URLField(
        "canonical URL",
        blank=True,
        help_text="Only if this content's main home is a different URL. Usually leave blank.",
    )

    class Meta:
        abstract = True

    # --- Override these in each model ---

    def default_seo_title(self):
        raise NotImplementedError

    def default_meta_description(self):
        raise NotImplementedError

    def default_og_image(self):
        """An ImageField file to fall back to, or None."""
        return None

    def public_path(self):
        """This object's page path on the public site, e.g. /locations/st-louis."""
        raise NotImplementedError

    # --- Resolved values (override, else automatic) ---

    def resolved_seo_title(self):
        return self.seo_title.strip() or self.default_seo_title()

    def resolved_meta_description(self):
        return self.meta_description.strip() or truncate_at_word(self.default_meta_description())

    def resolved_og_image(self):
        return self.og_image or self.default_og_image() or None


def seo_payload(obj, request=None):
    """The public `seo` object for the API. og_image is an absolute URL,
    or None (the frontend then uses the site-wide default image)."""
    image = obj.resolved_og_image()
    image_url = None
    if image:
        image_url = image.url
        if request is not None:
            # Leaves already-absolute URLs (Cloudinary) unchanged; makes
            # local-disk /media/... URLs absolute in dev.
            image_url = request.build_absolute_uri(image_url)

    return {
        "title": obj.resolved_seo_title(),
        "description": obj.resolved_meta_description(),
        "og_image": image_url,
        "canonical_url": obj.canonical_url or None,
        "noindex": obj.noindex,
    }
