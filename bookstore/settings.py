"""
Django settings for bookstore project.
Django 5.2.x
"""

from pathlib import Path
import os
import dj_database_url

# ---------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

def _split_hosts(val: str) -> list[str]:
    if not val:
        return []
    return [h.strip() for h in val.replace(",", " ").split() if h.strip()]

# NUNCA deixe segredo real committado; use variável de ambiente em prod
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")

# Local: default True; em prod (Heroku) defina DJANGO_DEBUG=0
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = _split_hosts(
    os.getenv(
        "ALLOWED_HOSTS",
        "localhost 127.0.0.1 0.0.0.0 .herokuapp.com",
    )
)

# ---------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "rest_framework.authtoken",
    "order",
    "product",
]

# Debug Toolbar só em DEBUG
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # estáticos em prod
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

ROOT_URLCONF = "bookstore.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bookstore.wsgi.application"

# ---------------------------------------------------------------------
# Database
#   - Heroku: usa DATABASE_URL
#   - Local/Compose: usa SQL_* ou POSTGRES_* (fallback p/ sqlite)
# ---------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    # Preferir Postgres se as envs existirem; senão sqlite
    if os.getenv("SQL_ENGINE") or os.getenv("POSTGRES_DB"):
        DATABASES = {
            "default": {
                "ENGINE": os.getenv("SQL_ENGINE", "django.db.backends.postgresql"),
                "NAME": os.getenv("SQL_DATABASE", os.getenv("POSTGRES_DB", "bookstore")),
                "USER": os.getenv("SQL_USER", os.getenv("POSTGRES_USER", "bookstore")),
                "PASSWORD": os.getenv("SQL_PASSWORD", os.getenv("POSTGRES_PASSWORD", "bookstore")),
                "HOST": os.getenv("SQL_HOST", os.getenv("POSTGRES_HOST", "db")),
                "PORT": os.getenv("SQL_PORT", os.getenv("POSTGRES_PORT", "5432")),
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

# ---------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------
# I18N
# ---------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Static / Whitenoise
# ---------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------------------------------------
# Security (para proxy TLS do Heroku)
# ---------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF: confia nos hosts públicos (https)
CSRF_TRUSTED_ORIGINS = [
    f"https://{h.lstrip('.')}"
    for h in ALLOWED_HOSTS
    if h and not any(x in h for x in ("localhost", "127.0.0.1", "0.0.0.0"))
]

# ---------------------------------------------------------------------
# DRF / Debug Toolbar
# ---------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
}

INTERNAL_IPS = ["127.0.0.1"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
