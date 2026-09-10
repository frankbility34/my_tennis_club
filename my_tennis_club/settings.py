"""
Django settings for my_tennis_club project.
"""

import os
from pathlib import Path

import cloudinary
import dj_database_url
import resend


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set."
    )


DEBUG = os.environ.get("DEBUG", "True").lower() == "true"


# ============================================================
# HOST CONFIGURATION
# ============================================================

render_hostname = os.environ.get(
    "RENDER_EXTERNAL_HOSTNAME"
)


allowed_hosts = os.environ.get(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost"
).split(",")


# Add Render hostname automatically
if render_hostname:
    allowed_hosts.append(render_hostname)


# Add your custom domain
allowed_hosts.extend([
    "msannewsblog.com",
    "www.msannewsblog.com",
])


ALLOWED_HOSTS = [
    host.strip()
    for host in allowed_hosts
    if host.strip()
]


# ============================================================
# CSRF TRUSTED ORIGINS
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    "https://msannewsblog.com",
    "https://www.msannewsblog.com",
]


if render_hostname:
    CSRF_TRUSTED_ORIGINS.append(
        f"https://{render_hostname}"
    )


extra_csrf_origins = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    ""
)


if extra_csrf_origins:
    CSRF_TRUSTED_ORIGINS.extend(
        origin.strip()
        for origin in extra_csrf_origins.split(",")
        if origin.strip()
    )


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    "members",

    "jazzmin",
    "cloudinary",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.sitemaps',
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # Serve static files efficiently in production
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL CONFIGURATION
# ============================================================

ROOT_URLCONF = "my_tennis_club.urls"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django.DjangoTemplates"
        ),

        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors.request"
                ),
                (
                    "django.contrib.auth.context_processors.auth"
                ),
                (
                    "django.contrib.messages.context_processors.messages"
                ),
            ],
        },
    },
]


# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = "my_tennis_club.wsgi.application"


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL")


if DATABASE_URL:

    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

else:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# MEDIA FILES
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# FILE STORAGE
# ============================================================

STORAGES = {
    "default": {
        "BACKEND": (
            "django.core.files.storage.FileSystemStorage"
        ),
    },

    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedStaticFilesStorage"
        ),
    },
}


# ============================================================
# CLOUDINARY CONFIGURATION
# ============================================================

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get(
        "CLOUDINARY_CLOUD_NAME"
    ),

    "API_KEY": os.environ.get(
        "CLOUDINARY_API_KEY"
    ),

    "API_SECRET": os.environ.get(
        "CLOUDINARY_API_SECRET"
    ),
}


# ============================================================
# CLOUDINARY MEDIA STORAGE
# ============================================================

if os.environ.get("CLOUDINARY_CLOUD_NAME"):

    STORAGES["default"] = {
        "BACKEND": (
            "cloudinary_storage.storage."
            "MediaCloudinaryStorage"
        ),
    }


# ============================================================
# CLOUDINARY PYTHON SDK
# ============================================================

cloudinary.config(
    cloud_name=os.environ.get(
        "CLOUDINARY_CLOUD_NAME"
    ),

    api_key=os.environ.get(
        "CLOUDINARY_API_KEY"
    ),

    api_secret=os.environ.get(
        "CLOUDINARY_API_SECRET"
    ),
)


# ============================================================
# EMAIL CONFIGURATION — RESEND
# ============================================================

RESEND_API_KEY = os.environ.get(
    "RESEND_API_KEY",
    ""
)


resend.api_key = RESEND_API_KEY


DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "info@msannewsblog.com"
)


ADMIN_EMAIL = os.environ.get(
    "ADMIN_EMAIL",
    "info@msannewsblog.com"
)


# ============================================================
# PRODUCTION EMAIL CHECK
# ============================================================

if os.environ.get("RENDER") and not RESEND_API_KEY:

    raise RuntimeError(
        "RESEND_API_KEY environment variable is not set."
    )


# ============================================================
# HTTPS / PRODUCTION SECURITY
# ============================================================

if not DEBUG:

    # Render handles HTTPS at the proxy.
    # Redirect normal HTTP requests to HTTPS.
    SECURE_SSL_REDIRECT = True


    # Tell Django that Render's forwarded HTTPS
    # connection should be trusted.
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )


    # Send session cookies only over HTTPS.
    SESSION_COOKIE_SECURE = True


    # Send CSRF cookies only over HTTPS.
    CSRF_COOKIE_SECURE = True


    # Protect against clickjacking.
    X_FRAME_OPTIONS = "DENY"


    # HSTS
    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True


else:

    # Development settings
    SECURE_SSL_REDIRECT = False

    SESSION_COOKIE_SECURE = False

    CSRF_COOKIE_SECURE = False

    SECURE_HSTS_SECONDS = 0

    SECURE_HSTS_INCLUDE_SUBDOMAINS = False

    SECURE_HSTS_PRELOAD = False


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


# ============================================================
# LOGGING
# ============================================================

LOGGING = {
    "version": 1,

    "disable_existing_loggers": False,

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },

    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}


# ============================================================
# WEBSITE URL
# ============================================================

if DEBUG:

    SITE_URL = "http://127.0.0.1:8000"

else:

    SITE_URL = "https://www.msannewsblog.com"

