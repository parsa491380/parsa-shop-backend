"""
Main URL configuration.

There are two major parts here:

    /api/
        JSON API used by Next.js

    /dashboard/
        Django Oscar administration dashboard

Django will NOT be our customer-facing frontend.
Next.js will handle that.
"""

from django.contrib import admin
from django.urls import include, path
from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Django's built-in admin.
    path(
        "admin/",
        admin.site.urls,
    ),

    # Our API.
    path(
        "api/",
        include("api.urls"),
    ),

    # Oscar's dashboard and other Oscar URLs.
    #
    # We will mainly use the dashboard:
    #
    #   /dashboard/
    #
    # for managing products, stock, orders, offers, etc.
    path(
        "",
        include(
            apps.get_app_config("oscar").urls[0]
        ),
    ),
]


# During development Django can directly serve uploaded
# product images and static assets.
#
# In production Nginx will serve these files instead.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )