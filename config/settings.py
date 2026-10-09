"""
Django settings for our shoe/clothing store.

This file controls:
    - Django itself
    - Django Oscar
    - our REST API
    - database connection
    - authentication
    - static files
    - uploaded product images
    - security settings

Important:
We keep configuration here rather than putting business logic
inside this file.
"""

import os
from pathlib import Path


# ---------------------------------------------------------
# Basic paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------


def env_bool(name: str, default: bool = False) -> bool:
    """
    Read a boolean environment variable.

    Examples:
        DEBUG=true
        DEBUG=false

    This allows us to use the same code in development
    and production without editing this file every time.
    """
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in ("1", "true", "yes", "on")


def env_list(name: str, default: list[str] | None = None) -> list[str]:
    """
    Read a comma-separated environment variable.

    Example:

        ALLOWED_HOSTS=localhost,127.0.0.1

    becomes:

        ["localhost", "127.0.0.1"]
    """
    value = os.getenv(name)

    if not value:
        return default or []

    return [item.strip() for item in value.split(",") if item.strip()]


# ---------------------------------------------------------
# Security
# ---------------------------------------------------------

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "dev-only-change-this-secret-key",
)

DEBUG = env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    [
        "localhost",
        "127.0.0.1",
    ],
)


# ---------------------------------------------------------
# Installed applications
# ---------------------------------------------------------

INSTALLED_APPS = [
    # -------------------------
    # Django
    # -------------------------
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "django.contrib.sitemaps",
    # -------------------------
    # Our API
    # -------------------------
    "api",
    # -------------------------
    # Django Oscar
    # -------------------------
    "oscar.config.Shop",
    "oscar.apps.analytics.apps.AnalyticsConfig",
    "oscar.apps.checkout.apps.CheckoutConfig",
    "oscar.apps.address.apps.AddressConfig",
    "oscar.apps.shipping.apps.ShippingConfig",
    "oscar.apps.catalogue.apps.CatalogueConfig",
    "oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig",
    "oscar.apps.communication.apps.CommunicationConfig",
    "oscar.apps.partner.apps.PartnerConfig",
    "oscar.apps.basket.apps.BasketConfig",
    "oscar.apps.payment.apps.PaymentConfig",
    "oscar.apps.offer.apps.OfferConfig",
    "oscar.apps.order.apps.OrderConfig",
    "oscar.apps.customer.apps.CustomerConfig",
    "oscar.apps.search.apps.SearchConfig",
    "oscar.apps.voucher.apps.VoucherConfig",
    "oscar.apps.wishlists.apps.WishlistsConfig",
    # Dashboard
    "oscar.apps.dashboard.apps.DashboardConfig",
    "oscar.apps.dashboard.reports.apps.ReportsDashboardConfig",
    "oscar.apps.dashboard.users.apps.UsersDashboardConfig",
    "oscar.apps.dashboard.orders.apps.OrdersDashboardConfig",
    "oscar.apps.dashboard.catalogue.apps.CatalogueDashboardConfig",
    "oscar.apps.dashboard.offers.apps.OffersDashboardConfig",
    "oscar.apps.dashboard.partners.apps.PartnersDashboardConfig",
    "oscar.apps.dashboard.pages.apps.PagesDashboardConfig",
    "oscar.apps.dashboard.ranges.apps.RangesDashboardConfig",
    "oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig",
    "oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig",
    "oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig",
    "oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig",
    # Oscar dependencies
    "widget_tweaks",
    "haystack",
    "treebeard",
    "sorl.thumbnail",
    "easy_thumbnails",
    "django_tables2",
]


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serve static assets efficiently.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # Protect POST/PUT/PATCH/DELETE requests.
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Oscar requires this so request.basket exists.
    "oscar.apps.basket.middleware.BasketMiddleware",
]


# ---------------------------------------------------------
# URLs
# ---------------------------------------------------------

ROOT_URLCONF = "config.urls"


# ---------------------------------------------------------
# Templates
# ---------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                # Oscar context processors
                "oscar.apps.search.context_processors.search_form",
                "oscar.apps.checkout.context_processors.checkout",
                "oscar.apps.communication.notifications.context_processors.notifications",
                "oscar.core.context_processors.metadata",
            ],
        },
    },
]


# ---------------------------------------------------------
# WSGI / ASGI
# ---------------------------------------------------------

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

DATABASE_ENGINE = os.getenv(
    "DATABASE_ENGINE",
    "django.db.backends.sqlite3",
)

if DATABASE_ENGINE == "django.db.backends.postgresql":
    DATABASES = {
        "default": {
            "ENGINE": DATABASE_ENGINE,
            "NAME": os.getenv("DATABASE_NAME", "shop"),
            "USER": os.getenv("DATABASE_USER", "shop"),
            "PASSWORD": os.getenv("DATABASE_PASSWORD", ""),
            "HOST": os.getenv("DATABASE_HOST", "127.0.0.1"),
            "PORT": os.getenv("DATABASE_PORT", "5432"),
        }
    }

else:
    # SQLite is convenient for local development.
    #
    # IMPORTANT:
    # Oscar officially recommends PostgreSQL for production.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ---------------------------------------------------------
# Password validation
# ---------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": ("django.contrib.auth.password_validation.MinimumLengthValidator"),
        "OPTIONS": {
            "min_length": 9,
        },
    },
    {
        "NAME": ("django.contrib.auth.password_validation.CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation.NumericPasswordValidator"),
    },
]


# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")

USE_I18N = True
USE_TZ = True


# Oscar provides an authentication backend that allows
# customers to authenticate using their email address.
AUTHENTICATION_BACKENDS = (
    "oscar.apps.customer.auth_backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
)


# ---------------------------------------------------------
# Django Sites
# ---------------------------------------------------------

SITE_ID = 1


# ---------------------------------------------------------
# Static files
# ---------------------------------------------------------

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# ---------------------------------------------------------
# User-uploaded media
#
# Product images uploaded through Oscar will eventually
# live here.
# ---------------------------------------------------------

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------
# Default primary key
# ---------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------
# Oscar defaults
#
# Oscar has many ecommerce-specific settings.
# Importing its defaults allows us to start with sane values.
# ---------------------------------------------------------

from oscar.defaults import *  # noqa: E402,F401,F403


# We allow anonymous customers to create baskets and later
# decide whether checkout requires login.
OSCAR_ALLOW_ANON_CHECKOUT = True


# Number of products stored in the recently viewed cookie.
OSCAR_RECENTLY_VIEWED_PRODUCTS = 20

# Order workflow used by the store. The dashboard can move an order
# through these states as fulfilment progresses.
OSCAR_INITIAL_ORDER_STATUS = "Pending"
OSCAR_INITIAL_LINE_STATUS = "Pending"
OSCAR_ORDER_STATUS_PIPELINE = {
    "Pending": ("Being processed", "Cancelled"),
    "Being processed": ("Processed", "Cancelled"),
    "Processed": ("Shipped", "Cancelled"),
    "Shipped": ("Delivered",),
    "Delivered": (),
    "Cancelled": (),
}

# Used when a new stock record is created in Oscar's dashboard.
# Existing stock records retain their own configured currency.
OSCAR_DEFAULT_CURRENCY = os.getenv("OSCAR_DEFAULT_CURRENCY", "ریال")


# ---------------------------------------------------------
# Search
#
# Whoosh runs locally on this server.
# There is no external search service.
# ---------------------------------------------------------

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.whoosh_backend.WhooshEngine",
        "PATH": BASE_DIR / "whoosh_index",
    },
}

HAYSTACK_SIGNAL_PROCESSOR = "haystack.signals.RealtimeSignalProcessor"


# ---------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------

REST_FRAMEWORK = {
    # We use Django sessions instead of JWT initially.
    #
    # This is especially useful because Next.js and Django
    # will eventually be served under the same website.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Public API endpoints are explicitly protected with
    # IsAuthenticated where necessary.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    # Our frontend only needs JSON.
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": ("rest_framework.pagination.PageNumberPagination"),
    "PAGE_SIZE": 24,
}


# ---------------------------------------------------------
# CSRF
# ---------------------------------------------------------

CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
)


# The JavaScript frontend needs to be able to read the
# CSRF cookie and copy it into the X-CSRFToken header.
CSRF_COOKIE_HTTPONLY = False


# Browser cookies should not be sent cross-site.
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"


# The actual session ID must not be readable by JavaScript.
SESSION_COOKIE_HTTPONLY = True


# Enable these automatically when DEBUG=False.
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# ---------------------------------------------------------
# Security headers
# ---------------------------------------------------------

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = "same-origin"

X_FRAME_OPTIONS = "DENY"


# Tell Django that Nginx terminates HTTPS.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)


# We will turn these on in the production deployment.
SECURE_SSL_REDIRECT = env_bool(
    "DJANGO_SECURE_SSL_REDIRECT",
    False,
)

SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_HSTS_SECONDS", "0"))

# ---------------------------------------------------------
# Checkout/payment safety
#
# Pending orders are useful while developing locally, but a
# production store must not consider an order paid until the
# payment provider has confirmed the transaction.
# ---------------------------------------------------------

CHECKOUT_ALLOW_PENDING_ORDERS = env_bool(
    "CHECKOUT_ALLOW_PENDING_ORDERS",
    DEBUG,
)


# ---------------------------------------------------------
# Email
#
# For development we don't need an external email service.
# Django simply prints emails to the terminal.
#
# Later we can replace this with your own SMTP setup.
# ---------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
