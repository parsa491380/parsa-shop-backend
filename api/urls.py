"""
URLs belonging to our JSON API.

The browser will communicate with:

    /api/...

instead of directly using Oscar's HTML views.
"""

from django.urls import path

from .views import (
    CategoryListView,
    CsrfTokenView,
    HealthCheckView,
    LoginView,
    LogoutView,
    MeView,
    ProductDetailView,
    ProductListView,
    RegisterView,
)


urlpatterns = [
    # -----------------------------------------------------
    # Health
    # -----------------------------------------------------

    path(
        "health/",
        HealthCheckView.as_view(),
        name="health",
    ),

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    path(
        "auth/csrf/",
        CsrfTokenView.as_view(),
        name="csrf",
    ),

    path(
        "auth/login/",
        LoginView.as_view(),
        name="login",
    ),

    path(
        "auth/register/",
        RegisterView.as_view(),
        name="register",
    ),

    path(
        "auth/logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    path(
        "auth/me/",
        MeView.as_view(),
        name="me",
    ),

    # -----------------------------------------------------
    # Catalogue
    # -----------------------------------------------------

    path(
        "products/",
        ProductListView.as_view(),
        name="products",
    ),

    path(
    "products/<slug:slug>/",
    ProductDetailView.as_view(),
    name="product-detail",
    ),

    path(
        "categories/",
        CategoryListView.as_view(),
        name="categories",
    ),
]