"""
Tests for SiteSettings: the one-record rule, alt text validation, the
admin (no list page, no add once it exists, no delete), the public
/api/v1/site-settings/ endpoint, and the home + partner page refresh.

Uploads go to a temporary folder on local disk (never Cloudinary, even
if backend/.env sets CLOUDINARY_URL).
"""

import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import SiteSettings
from .test_revalidation import RevalidationTestCase

# Smallest valid GIF (1×1 px), so ImageField's Pillow check accepts it.
TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00"
    b"\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)

TEMP_MEDIA = tempfile.mkdtemp()
LOCAL_STORAGE = {
    "STORAGES": {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
    "MEDIA_ROOT": TEMP_MEDIA,
}


def tiny_image(name="photo.gif"):
    return SimpleUploadedFile(name, TINY_GIF, content_type="image/gif")


def tearDownModule():
    shutil.rmtree(TEMP_MEDIA, ignore_errors=True)


@override_settings(**LOCAL_STORAGE)
class SiteSettingsModelTests(TestCase):
    def test_load_without_a_record_returns_unsaved_empty_settings(self):
        settings = SiteSettings.load()
        self.assertFalse(settings.home_hero_image)
        self.assertFalse(SiteSettings.objects.exists(), "load() must not write to the database")

    def test_only_one_record_can_exist(self):
        SiteSettings().save()
        SiteSettings(home_hero_alt="second").save()
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(SiteSettings.load().home_hero_alt, "second")

    def test_alt_text_is_required_when_an_image_is_set(self):
        settings = SiteSettings(partner_hero_image=tiny_image())
        with self.assertRaises(ValidationError) as caught:
            settings.full_clean()
        self.assertIn("partner_hero_alt", caught.exception.message_dict)

        settings.partner_hero_alt = "Ferns on a café shelf"
        settings.full_clean()  # no error now

    def test_everything_blank_is_valid(self):
        SiteSettings().full_clean()


@override_settings(**LOCAL_STORAGE)
class SiteSettingsAdminTests(TestCase):
    def setUp(self):
        self.client.force_login(
            get_user_model().objects.create_superuser("admin", "admin@example.com", "pw")
        )
        self.list_url = reverse("admin:core_sitesettings_changelist")
        self.add_url = reverse("admin:core_sitesettings_add")
        self.change_url = reverse("admin:core_sitesettings_change", args=[SiteSettings.SINGLETON_PK])

    def test_list_page_goes_to_the_add_form_before_a_record_exists(self):
        self.assertRedirects(self.client.get(self.list_url), self.add_url)

    def test_list_page_goes_to_the_record_once_it_exists(self):
        SiteSettings().save()
        self.assertRedirects(self.client.get(self.list_url), self.change_url)

    def test_no_add_once_it_exists_and_never_delete(self):
        SiteSettings().save()
        self.assertEqual(self.client.get(self.add_url).status_code, 403)
        delete_url = reverse("admin:core_sitesettings_delete", args=[SiteSettings.SINGLETON_PK])
        self.assertEqual(self.client.get(delete_url).status_code, 403)

    def test_upload_without_alt_text_is_rejected(self):
        response = self.client.post(self.add_url, {"home_hero_image": tiny_image()})
        self.assertEqual(response.status_code, 200)  # form redisplayed with errors
        self.assertContains(response, "Add alt text for this image")
        self.assertFalse(SiteSettings.objects.exists())

    def test_upload_with_alt_text_saves(self):
        response = self.client.post(
            self.add_url, {"home_hero_image": tiny_image(), "home_hero_alt": "Plants at a bar"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SiteSettings.load().home_hero_image.name.startswith("site/"))

    def test_help_text_gives_the_recommended_size(self):
        SiteSettings().save()
        self.assertContains(
            self.client.get(self.change_url),
            "Landscape 4:3, about 2000 × 1500 px, JPG under 500 KB.",
            count=3,
        )


@override_settings(**LOCAL_STORAGE)
class SiteSettingsApiTests(TestCase):
    url = "/api/v1/site-settings/"

    def test_no_record_yet_returns_all_nulls(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"home_hero": None, "partner_hero": None, "why_image": None}
        )
        self.assertFalse(SiteSettings.objects.exists(), "a GET must not create the record")

    def test_set_images_return_absolute_url_and_alt_empty_ones_null(self):
        SiteSettings(home_hero_image=tiny_image("hero.gif"), home_hero_alt="Plants at a bar").save()

        data = self.client.get(self.url).json()
        self.assertEqual(set(data), {"home_hero", "partner_hero", "why_image"})
        self.assertEqual(data["home_hero"]["alt"], "Plants at a bar")
        self.assertRegex(data["home_hero"]["url"], r"^http://testserver/media/site/hero.*\.gif$")
        self.assertIsNone(data["partner_hero"])
        self.assertIsNone(data["why_image"])

    def test_is_read_only(self):
        self.assertEqual(self.client.post(self.url, {}).status_code, 405)


@override_settings(**LOCAL_STORAGE)
class SiteSettingsRevalidationTests(RevalidationTestCase):
    def test_saving_settings_refreshes_home_and_partner_pages_only(self):
        settings = SiteSettings()
        with self.capture_sends() as send:
            settings.why_alt = "Our team potting plants"
            settings.save()
        self.assertEqual(self.sent_paths(send), {"/", "/partner"})
