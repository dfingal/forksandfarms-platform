"""
Django settings for the Forks And Farms platform.

All runtime config comes from environment variables (see backend/.env.example).
Nothing secret lives in this file.
"""

from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
)
# Read backend/.env when it exists (local dev). In production (Render),
# real env vars are injected by the platform and this is a no-op.
environ.Env.read_env(BASE_DIR / ".env")


# --- Core ---

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Render sets this automatically to the service's *.onrender.com hostname —
# append it so ALLOWED_HOSTS doesn't need that hostname hand-typed into the
# ALLOWED_HOSTS env var too (it's still there for the Vercel domain, a
# future custom domain, etc). A no-op locally, where this var is unset.
RENDER_EXTERNAL_HOSTNAME = env("RENDER_EXTERNAL_HOSTNAME", default="")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


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
    "whitenoise.middleware.WhiteNoiseMiddleware",
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

# Vercel gives every branch/PR its own preview URL
# (forksandfarms-frontend-<hash>-<team>.vercel.app), so a fixed origin list
# can't cover them. CORS_ALLOWED_ORIGIN_REGEX_VERCEL holds just this
# project's preview pattern (set once the Vercel project exists — see the
# deploy walkthrough) rather than trusting every *.vercel.app site.
_vercel_preview_regex = env("CORS_ALLOWED_ORIGIN_REGEX_VERCEL", default="")
CORS_ALLOWED_ORIGIN_REGEXES = [_vercel_preview_regex] if _vercel_preview_regex else []


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
    # Deliberately NOT adding "cloudinary_storage"/"cloudinary" to
    # INSTALLED_APPS: the storage backend below is just an import path
    # and doesn't need app registration, and django-cloudinary-storage's
    # bundled `collectstatic` command override still assumes Django's
    # pre-6.0 STATICFILES_STORAGE setting — it crashes under STORAGES
    # (which is what we use, and what WhiteNoise's static backend needs).
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

# WhiteNoise serves static files (admin CSS/JS) directly from the app —
# no separate static host needed. This only overrides the "staticfiles"
# backend set just above; it never touches "default" (media/Cloudinary).
STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
}


# --- Production hardening ---

if not DEBUG:
    # Cloudinary required outside DEBUG: Render's disk isn't persistent
    # across deploys, so a venue/application photo saved to local disk
    # (the dev fallback above) would vanish on the next deploy. Fail
    # loudly at startup rather than silently losing uploads later.
    if not CLOUDINARY_URL:
        raise ImproperlyConfigured(
            "CLOUDINARY_URL must be set when DJANGO_DEBUG=False — local disk "
            "storage is not persistent in production."
        )

    # Render terminates TLS at its own proxy and forwards plain HTTP to
    # this app; without telling Django to trust that header, every
    # request looks insecure and SECURE_SSL_REDIRECT below would loop.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    SECURE_SSL_REDIRECT = True
    # /healthz/ is exempted: Render's health checker calls it over plain
    # HTTP internally, and a 301 there (instead of the expected 200)
    # would make Render think the deploy is unhealthy.
    SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # The admin's login form needs these for its CSRF check to pass
    # behind a proxy — the onrender.com service URL and the Vercel
    # frontend's own domain (admin is same-origin, but Django's CSRF
    # check also consults this for cross-origin form posts).
    CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])


# --- Django REST Framework ---

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_THROTTLE_RATES": {
        "partner_application": "5/hour",
    },
    # Render puts one reverse proxy in front of the app, which appends the
    # real client IP to X-Forwarded-For. Without this, DRF's throttle (and
    # our source_ip capture in core.utils.get_client_ip) would read
    # REMOTE_ADDR — the proxy's own IP — and every visitor in production
    # would share a single rate-limit bucket. Set to 0 (or unset) for a
    # setup with no reverse proxy, e.g. plain local development.
    "NUM_PROXIES": env.int("NUM_PROXIES", default=1),
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
