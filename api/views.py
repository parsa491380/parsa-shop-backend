"""
JSON API used by the Next.js storefront.

Architecture:

    Next.js
        -> same-origin /api/*
        -> this module
        -> Django Oscar
        -> database

The API deliberately exposes a small storefront contract instead of
serializing Oscar's internal models wholesale.
"""

import logging
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from oscar.apps.address.models import Country, UserAddress
from oscar.apps.checkout.calculators import OrderTotalCalculator
from oscar.apps.order.models import Order, ShippingAddress
from oscar.apps.order.utils import OrderCreator
from oscar.apps.partner.strategy import Selector
from oscar.apps.shipping.methods import Free
from oscar.core.loading import get_model
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

Product = get_model("catalogue", "Product")
Category = get_model("catalogue", "Category")

logger = logging.getLogger(__name__)


# =========================================================
# Shared helpers
# =========================================================


def serialize_user(user):
    """Return only customer fields the storefront is allowed to see."""

    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
    }


def money(value):
    """Serialize Decimal-like values without floating point loss."""

    if value is None:
        return None
    return str(Decimal(value))


def get_strategy(request):
    """Return Oscar's pricing/availability strategy for this request."""

    return Selector().strategy(
        request=request,
        user=request.user,
    )


def get_price_information(product, request):
    """
    Resolve price, availability and stock through Oscar.

    The browser never calculates authoritative ecommerce prices.
    """

    strategy = get_strategy(request)

    # Oscar exposes a separate parent strategy because a parent product
    # can represent several purchasable child products.
    if product.is_parent:
        purchase_info = strategy.fetch_for_parent(product)
    else:
        purchase_info = strategy.fetch_for_product(product)

    price = purchase_info.price
    availability = purchase_info.availability
    stockrecord = purchase_info.stockrecord

    result = {
        "available": bool(availability.is_available_to_buy),
        "availability_message": availability.message,
        "currency": price.currency,
        "price": None,
        "price_excl_tax": None,
        "tax": None,
        "tax_included": False,
        "stock": None,
        "sku": None,
    }

    if stockrecord is not None:
        result["sku"] = stockrecord.partner_sku
        result["stock"] = stockrecord.num_in_stock

    if not price.exists:
        return result

    result["price_excl_tax"] = money(price.excl_tax)
    result["tax"] = money(price.tax)

    if price.is_tax_known:
        result["price"] = money(price.incl_tax)
        result["tax_included"] = True
    else:
        result["price"] = money(price.excl_tax)

    return result


def serialize_image(image):
    """Convert an Oscar product image to a small frontend DTO."""

    return {
        "url": image.original.url,
        "caption": image.caption or "",
        "is_primary": image.is_primary(),
    }


def serialize_variant(product, request):
    """Serialize one purchasable Oscar child product."""

    attributes = {
        value.attribute.code: value.value_as_text
        for value in product.get_attribute_values()
    }

    images = [serialize_image(image) for image in product.get_all_images()]

    return {
        "id": product.id,
        "title": product.title,
        "slug": product.slug,
        "attributes": attributes,
        "images": images,
        "price": get_price_information(product, request),
    }


def serialize_product(product, request):
    """Convert an Oscar product to the public storefront representation."""

    categories = [
        {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
        }
        for category in product.categories.all()
    ]

    images = [serialize_image(image) for image in product.get_all_images()]

    attributes = {
        value.attribute.code: value.value_as_text
        for value in product.get_attribute_values()
    }

    children = []

    if product.is_parent:
        children = [
            serialize_variant(child, request)
            for child in product.children.all()
            if child.is_public
        ]

    return {
        "id": product.id,
        "title": product.title,
        "slug": product.slug,
        "description": product.description,
        "rating": float(product.rating or 0),
        "images": images,
        "attributes": attributes,
        "categories": categories,
        "structure": product.structure,
        "price": get_price_information(product, request),
        "children": children,
    }


def serialize_category(category):
    """Return a category plus its storefront metadata."""

    # Count products assigned to this category or one of its descendants.
    # Oscar stores the tree path on the category model, so this avoids
    # issuing a separate descendant traversal for every category.
    product_count = (
        Product.objects.filter(
            is_public=True,
            categories__path__startswith=category.path,
        )
        .exclude(structure=Product.CHILD)
        .distinct()
        .count()
    )

    image_url = None
    if getattr(category, "image", None):
        try:
            image_url = category.image.url
        except ValueError:
            image_url = None

    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "product_count": product_count,
        "depth": category.depth,
        "image": image_url,
    }


def product_image_url(product):
    """Return the first available image URL for basket/order summaries."""

    images = product.get_all_images()
    if not images:
        return None
    return images[0].original.url


def serialize_basket_line(line, request):
    """Serialize one Oscar basket line."""

    product = line.product
    purchase_info = line.purchase_info

    if purchase_info.price.is_tax_known:
        unit_price = purchase_info.price.incl_tax
    else:
        unit_price = purchase_info.price.excl_tax

    # Oscar calculates line totals and offer discounts on the basket line.
    line_total = line.line_price_incl_tax_incl_discounts

    return {
        "id": line.id,
        "product_id": product.id,
        "title": product.title,
        "slug": product.slug,
        "quantity": line.quantity,
        "unit_price": money(unit_price),
        "line_total": money(line_total),
        "currency": purchase_info.price.currency,
        "sku": purchase_info.stockrecord.partner_sku
        if purchase_info.stockrecord
        else None,
        "image": product_image_url(product),
        "availability": {
            "available": purchase_info.availability.is_available_to_buy,
            "message": purchase_info.availability.message,
        },
    }


def serialize_basket(basket, request):
    """Return the current server-side Oscar basket."""

    lines = [serialize_basket_line(line, request) for line in basket.all_lines()]

    if basket.is_tax_known:
        total = basket.total_incl_tax
        total_excl_tax = basket.total_excl_tax
    else:
        total = basket.total_excl_tax
        total_excl_tax = basket.total_excl_tax

    return {
        "id": basket.id,
        "status": basket.status,
        "num_items": basket.num_items,
        "num_lines": basket.num_lines,
        "is_empty": basket.is_empty,
        "is_shipping_required": basket.is_shipping_required(),
        "currency": basket.currency,
        "total": money(total),
        "total_excl_tax": money(total_excl_tax),
        "lines": lines,
    }


def serialize_order(order):
    """Return an order belonging to the current customer."""

    lines = []

    for line in order.lines.select_related("product"):
        lines.append(
            {
                "id": line.id,
                "product_id": line.product_id,
                "title": line.title,
                "quantity": line.quantity,
                "unit_price": money(line.unit_price_incl_tax),
                "line_total": money(line.line_price_incl_tax),
            }
        )

    shipping_address = order.shipping_address

    address = None
    if shipping_address:
        address = {
            "first_name": shipping_address.first_name,
            "last_name": shipping_address.last_name,
            "line1": shipping_address.line1,
            "line2": shipping_address.line2,
            "state": shipping_address.state,
            "postcode": shipping_address.postcode,
            "country": shipping_address.country.iso_3166_1_a2,
            "phone_number": shipping_address.phone_number,
            "notes": shipping_address.notes,
        }

    return {
        "id": order.id,
        "number": order.number,
        "status": order.status,
        "date_placed": order.date_placed,
        "currency": order.currency,
        "total_incl_tax": money(order.total_incl_tax),
        "total_excl_tax": money(order.total_excl_tax),
        "shipping_charge": money(order.shipping_incl_tax),
        "lines": lines,
        "shipping_address": address,
    }


def parse_bool(value, default=False):
    """Parse a JSON/form-like boolean value safely."""
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def parse_positive_int(value, default=1, maximum=99):
    """Validate quantity-like integer input received from the browser."""

    try:
        result = int(value)
    except (TypeError, ValueError):
        return None

    if result < 1 or result > maximum:
        return None

    return result


# =========================================================
# Health / CSRF
# =========================================================


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok", "service": "django"})


class CsrfTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"csrfToken": get_token(request)})


# =========================================================
# Authentication
# =========================================================


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        password = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            request=request,
            username=email,
            password=password,
        )

        if user is None:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {"detail": "This account is not active."},
                status=status.HTTP_403_FORBIDDEN,
            )

        login(request, user)
        return Response({"user": serialize_user(user)})


@method_decorator(csrf_protect, name="dispatch")
class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        password = request.data.get("password", "")
        first_name = str(request.data.get("first_name", "")).strip()
        last_name = str(request.data.get("last_name", "")).strip()

        if not email or not password:
            return Response(
                {"detail": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        User = get_user_model()

        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"detail": "An account with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )

        try:
            validate_password(password, user=user)
        except ValidationError as exc:
            return Response(
                {"detail": exc.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save()
        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        return Response(
            {"user": serialize_user(user)},
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": serialize_user(request.user)})


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Logged out successfully."})


# =========================================================
# Catalogue
# =========================================================


class ProductListView(ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        queryset = (
            Product.objects.filter(is_public=True)
            .exclude(structure=Product.CHILD)
            .prefetch_related(
                "images",
                "categories",
                "attribute_values__attribute",
                "children__images",
                "children__attribute_values__attribute",
            )
        )

        search = str(self.request.query_params.get("search", "")).strip()
        category = str(self.request.query_params.get("category", "")).strip()
        sort = str(self.request.query_params.get("sort", "latest")).strip()

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        if category:
            queryset = queryset.filter(categories__slug=category)

        if sort == "oldest":
            queryset = queryset.order_by("date_created")
        elif sort == "priority":
            queryset = queryset.order_by("-priority", "-date_created")
        elif sort == "price_asc":
            # The exact customer price is strategy-driven. This DB ordering
            # is only a best-effort catalogue order and must not be used for
            # checkout calculations.
            queryset = queryset.order_by("stockrecords__price", "title")
        elif sort == "price_desc":
            queryset = queryset.order_by("-stockrecords__price", "title")
        else:
            queryset = queryset.order_by("-date_created", "-priority")

        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        data_source = page if page is not None else queryset
        data = [serialize_product(product, request) for product in data_source]

        if page is not None:
            return self.get_paginated_response(data)

        return Response(data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, slug):
        try:
            product = Product.objects.prefetch_related(
                "images",
                "children__images",
                "children__attribute_values__attribute",
                "attribute_values__attribute",
                "categories",
            ).get(slug=slug, is_public=True)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if product.is_child:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(serialize_product(product, request))


class CategoryListView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        categories = Category.objects.filter(
            is_public=True, ancestors_are_public=True
        ).order_by("path")
        return Response([serialize_category(category) for category in categories])


class CountryListView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        countries = Country.objects.filter(
            printable_name__isnull=False, is_shipping_country=True
        ).order_by("printable_name")
        return Response(
            [
                {
                    "code": country.iso_3166_1_a2,
                    "name": country.printable_name or country.name,
                }
                for country in countries
            ]
        )


# =========================================================
# Basket
# =========================================================


class BasketView(APIView):
    """Return the current anonymous or authenticated Oscar basket."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(serialize_basket(request.basket, request))

    @method_decorator(csrf_protect)
    def delete(self, request):
        basket = request.basket
        if not basket.is_empty:
            basket.flush()
        return Response(serialize_basket(basket, request))


@method_decorator(csrf_protect, name="dispatch")
class BasketItemCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = parse_positive_int(request.data.get("quantity"), default=1)

        if quantity is None:
            return Response(
                {"detail": "Quantity must be between 1 and 99."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(id=product_id, is_public=True)
        except (Product.DoesNotExist, TypeError, ValueError):
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if product.is_parent:
            return Response(
                {"detail": "Select a product variant before adding it to the basket."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        basket = request.basket

        try:
            basket.strategy = get_strategy(request)
            line, _created = basket.add_product(product, quantity=quantity)
        except Exception as exc:
            # Oscar performs the actual availability/quantity checks.
            # We log the exception server-side and return a safe message
            # instead of exposing Python/Oscar internals to customers.
            logger.exception("Unable to add product %s to basket.", product.id)
            return Response(
                {"detail": "The product could not be added to the basket."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "basket": serialize_basket(basket, request),
                "line_id": line.id,
            },
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_protect, name="dispatch")
class BasketLineView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, line_id):
        basket = request.basket
        basket.strategy = get_strategy(request)
        quantity = parse_positive_int(request.data.get("quantity"), default=1)

        if quantity is None:
            return Response(
                {"detail": "Quantity must be between 1 and 99."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            line = basket.lines.get(id=line_id)
        except basket.lines.model.DoesNotExist:
            return Response(
                {"detail": "Basket line not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        allowed, reason = line.purchase_info.availability.is_purchase_permitted(
            quantity
        )
        if not allowed:
            return Response(
                {"detail": reason},
                status=status.HTTP_400_BAD_REQUEST,
            )

        line.quantity = quantity
        line.save()
        basket.reset_offer_applications()

        return Response(serialize_basket(basket, request))

    def delete(self, request, line_id):
        basket = request.basket

        try:
            line = basket.lines.get(id=line_id)
        except basket.lines.model.DoesNotExist:
            return Response(
                {"detail": "Basket line not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        line.delete()
        basket.reset_offer_applications()

        return Response(serialize_basket(basket, request))


# =========================================================
# Shipping + orders
# =========================================================


class ShippingMethodListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        basket = request.basket
        method = Free()
        charge = method.calculate(basket)

        return Response(
            [
                {
                    "code": "free",
                    "name": "Standard shipping",
                    "description": "Standard delivery",
                    "price": money(
                        charge.incl_tax if charge.is_tax_known else charge.excl_tax
                    ),
                    "currency": charge.currency,
                }
            ]
        )


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = (
            Order.objects.filter(user=request.user)
            .prefetch_related("lines", "shipping_address")
            .order_by("-date_placed")
        )

        return Response([serialize_order(order) for order in orders])


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, number):
        try:
            order = (
                Order.objects.filter(user=request.user)
                .prefetch_related("lines", "shipping_address")
                .get(number=number)
            )
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(serialize_order(order))


@method_decorator(csrf_protect, name="dispatch")
class CreateOrderView(APIView):
    """
    Create a pending Oscar order from the current basket.

    Payment is intentionally NOT marked as successful here.
    A payment provider must later verify payment before the order
    moves beyond its pending state.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        basket = request.basket
        basket.strategy = request.strategy

        if basket.is_empty:
            return Response(
                {"detail": "Your basket is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data

        required_fields = [
            "first_name",
            "last_name",
            "line1",
            "postcode",
            "country",
        ]

        missing = [
            field for field in required_fields if not str(data.get(field, "")).strip()
        ]

        if missing:
            return Response(
                {
                    "detail": "Required shipping fields are missing.",
                    "fields": missing,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            country = Country.objects.get(
                iso_3166_1_a2__iexact=str(data["country"]).strip(),
                is_shipping_country=True,
            )
        except Country.DoesNotExist:
            return Response(
                {
                    "detail": "Invalid country. Configure countries in Oscar before checkout."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        shipping_address = ShippingAddress(
            first_name=str(data.get("first_name", "")).strip(),
            last_name=str(data.get("last_name", "")).strip(),
            line1=str(data.get("line1", "")).strip(),
            line2=str(data.get("line2", "")).strip(),
            line3=str(data.get("line3", "")).strip(),
            line4=str(data.get("city", data.get("line4", ""))).strip(),
            state=str(data.get("state", "")).strip(),
            postcode=str(data.get("postcode", "")).strip(),
            country=country,
            phone_number=str(data.get("phone_number", "")).strip(),
            notes=str(data.get("notes", "")).strip(),
        )

        try:
            shipping_address.full_clean()
        except ValidationError as exc:
            return Response(
                {"detail": exc.message_dict},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shipping_method = Free()
        shipping_charge = shipping_method.calculate(basket)
        order_total = OrderTotalCalculator().calculate(
            basket,
            shipping_charge,
        )

        # The order starts as Pending. It must not be represented as
        # paid until the payment provider has confirmed the transaction.
        order_status = getattr(Order, "PENDING", "Pending")

        if not settings.CHECKOUT_ALLOW_PENDING_ORDERS:
            return Response(
                {
                    "detail": (
                        "A payment provider is not configured for this store. "
                        "Checkout order creation is disabled until payment is connected."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            order = OrderCreator().place_order(
                basket=basket,
                total=order_total,
                shipping_method=shipping_method,
                shipping_charge=shipping_charge,
                user=request.user,
                shipping_address=shipping_address,
                billing_address=None,
                status=order_status,
                request=request,
            )
        except Exception:
            logger.exception(
                "Unable to create order for user %s.",
                request.user.pk,
            )
            return Response(
                {"detail": "The order could not be created."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Oscar's checkout flow marks the basket submitted after the order
        # has been placed. This also prevents the same basket from being reused.
        basket.submit()

        return Response(
            {
                "order": serialize_order(order),
                "payment": {
                    "status": "pending",
                    "required": True,
                    "message": "Connect the production payment provider before treating this order as paid.",
                },
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# Customer address book
# =========================================================


class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = request.user.addresses.all().select_related("country")
        return Response(
            [
                {
                    "id": address.id,
                    "first_name": address.first_name,
                    "last_name": address.last_name,
                    "line1": address.line1,
                    "line2": address.line2,
                    "line3": address.line3,
                    "line4": address.line4,
                    "state": address.state,
                    "postcode": address.postcode,
                    "country": address.country.iso_3166_1_a2,
                    "country_name": address.country.printable_name,
                    "phone_number": address.phone_number,
                    "is_default_for_shipping": address.is_default_for_shipping,
                    "is_default_for_billing": address.is_default_for_billing,
                }
                for address in addresses
            ]
        )

    @method_decorator(csrf_protect)
    def post(self, request):
        data = request.data

        try:
            country = Country.objects.get(
                iso_3166_1_a2__iexact=str(data.get("country", "")).strip()
            )
        except Country.DoesNotExist:
            return Response(
                {"detail": "Invalid country."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        address = UserAddress(
            user=request.user,
            first_name=str(data.get("first_name", "")).strip(),
            last_name=str(data.get("last_name", "")).strip(),
            line1=str(data.get("line1", "")).strip(),
            line2=str(data.get("line2", "")).strip(),
            line3=str(data.get("line3", "")).strip(),
            line4=str(data.get("line4", "")).strip(),
            state=str(data.get("state", "")).strip(),
            postcode=str(data.get("postcode", "")).strip(),
            country=country,
            phone_number=str(data.get("phone_number", "")).strip(),
            is_default_for_shipping=parse_bool(
                data.get("is_default_for_shipping"), False
            ),
            is_default_for_billing=parse_bool(
                data.get("is_default_for_billing"), False
            ),
        )

        try:
            address.full_clean()
            address.save()
        except ValidationError as exc:
            return Response(
                {"detail": exc.message_dict},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "id": address.id,
                "detail": "Address saved.",
            },
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_protect, name="dispatch")
class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, address_id):
        try:
            address = request.user.addresses.get(id=address_id)
        except UserAddress.DoesNotExist:
            return Response(
                {"detail": "Address not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
