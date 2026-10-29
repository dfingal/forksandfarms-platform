"""
Django settings for the Forks And Farms platform.

All runtime config comes from environment variables (see backend/.env.example).
Nothing secret lives in this file.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
)
# Read backend/.env when it exists (local dev). In production (Railway),
# real env vars are injected by the platform and this is a no-op.
environ.Env.read_env(BASE_DIR / ".env")


# --- Core ---

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])


# --- Applications ---

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    "django_filters",
    # Local apps
    "core",
    "partners",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --- Database ---
# DATABASE_URL, e.g. postgres://user:pass@localhost:5432/fnf_dev

DATABASES = {
    "default": env.db("DATABASE_URL"),
}


# --- CORS ---
# Comma-separated list in CORS_ALLOWED_ORIGINS, e.g. http://localhost:3000

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"])


# --- Password validation ---

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Internationalization ---

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Chicago"  # St. Louis
USE_I18N = True
USE_TZ = True


# --- Static & media files ---

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Image storage (Cloudinary, with a local-disk fallback) ---
#
# CLOUDINARY_URL is optional in dev: when it's not set, Cloudinary isn't
# configured and image fields just use Django's default local filesystem
# storage under MEDIA_ROOT (backend/media/, gitignored). This lets the owner
# upload venue photos through /admin before Cloudinary keys exist.
# Set CLOUDINARY_URL (see .env.example) to switch to Cloudinary — no code
# change needed, just add the env var and reinstall/migrate isn't required.
CLOUDINARY_URL = env("CLOUDINARY_URL", default="")

if CLOUDINARY_URL:
    INSTALLED_APPS = [
        "cloudinary_storage",
        *INSTALLED_APPS,
        "cloudinary",
    ]
    # django-cloudinary-storage reads CLOUDINARY_URL from the environment
    # itself, so nothing further to parse here.
    STORAGES = {
        "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }


# --- Django REST Framework ---

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}


# --- Email (Resend), Turnstile, revalidation ---
# Read here now so settings is the one place that touches env vars; wired
# into views in the API step (spec §5/§7).

RESEND_API_KEY = env("RESEND_API_KEY", default="")
FNF_NOTIFY_EMAIL = env("FNF_NOTIFY_EMAIL", default="")
FNF_FROM_EMAIL = env("FNF_FROM_EMAIL", default="")
TURNSTILE_SECRET_KEY = env("TURNSTILE_SECRET_KEY", default="")
FRONTEND_REVALIDATE_URL = env("FRONTEND_REVALIDATE_URL", default="")
REVALIDATE_SECRET = env("REVALIDATE_SECRET", default="")
