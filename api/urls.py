"""URL map for the JSON API consumed by the Next.js storefront."""

from django.urls import path

from .views import (
    AddressDetailView,
    AddressListCreateView,
    BasketItemCreateView,
    BasketLineView,
    BasketView,
    CategoryListView,
    CountryListView,
    CreateOrderView,
    CsrfTokenView,
    HealthCheckView,
    LoginView,
    LogoutView,
    MeView,
    OrderDetailView,
    OrderListView,
    ProductDetailView,
    ProductListView,
    RegisterView,
    ShippingMethodListView,
)

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    # Authentication
    path("auth/csrf/", CsrfTokenView.as_view(), name="csrf"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    # Catalogue
    path("products/", ProductListView.as_view(), name="products"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    # ======================================newly added apis
    path("categories/", CategoryListView.as_view(), name="categories"),
    path("countries/", CountryListView.as_view(), name="countries"),
    # Basket
    path("basket/", BasketView.as_view(), name="basket"),
    path("basket/items/", BasketItemCreateView.as_view(), name="basket-add"),
    path("basket/items/<int:line_id>/", BasketLineView.as_view(), name="basket-line"),
    # Checkout/orders
    path(
        "shipping/methods/", ShippingMethodListView.as_view(), name="shipping-methods"
    ),
    path("checkout/orders/", CreateOrderView.as_view(), name="create-order"),
    path("orders/", OrderListView.as_view(), name="orders"),
    path("orders/<str:number>/", OrderDetailView.as_view(), name="order-detail"),
    # Customer address book
    path("addresses/", AddressListCreateView.as_view(), name="addresses"),
    path(
        "addresses/<int:address_id>/",
        AddressDetailView.as_view(),
        name="address-detail",
    ),
]
