"""
API views used by the Next.js application.

Important architecture rule:

    Next.js = presentation

    Django/Oscar = business logic

The API should therefore ask Oscar for the information
instead of rebuilding ecommerce calculations in TypeScript.
"""

from decimal import Decimal

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.exceptions import ValidationError
from django.middleware.csrf import get_token
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.password_validation import validate_password
from django.db.models import Q

from oscar.core.loading import get_model
from oscar.apps.partner.strategy import Selector


# ---------------------------------------------------------
# Oscar models
# ---------------------------------------------------------

Product = get_model("catalogue", "Product")
Category = get_model("catalogue", "Category")


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def serialize_user(user) -> dict:
    """
    Convert Django's User model into JSON safe for our frontend.

    We intentionally expose only fields that the frontend
    actually needs.
    """

    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
    }


def get_price_information(product, request) -> dict:
    """
    Ask Oscar's pricing/availability strategy for the
    current price and stock information.

    NEVER calculate the real shop price in Next.js.

    Oscar supports pricing strategies because pricing can
    eventually depend on things such as:

        customer
        country
        taxes
        partner
        stock
        offers
    """

    strategy = Selector().strategy(
        request=request,
        user=request.user,
    )

    purchase_info = strategy.fetch_for_product(product)

    price = purchase_info.price
    availability = purchase_info.availability
    stockrecord = purchase_info.stockrecord

    result = {
        "available": availability.is_available_to_buy,
        "availability_message": availability.message,
        "currency": price.currency,
        "price": None,
        "price_excl_tax": None,
        "tax": None,
        "tax_included": False,
        "stock": None,
        "sku": None,
    }

    if stockrecord:
        result["sku"] = stockrecord.partner_sku

        # num_in_stock is Oscar's actual inventory value.
        result["stock"] = stockrecord.num_in_stock

    if price.exists:

        if price.excl_tax is not None:
            result["price_excl_tax"] = str(
                Decimal(price.excl_tax)
            )

        if price.tax is not None:
            result["tax"] = str(
                Decimal(price.tax)
            )

        # When tax is known, use the tax-inclusive value.
        #
        # When tax isn't configured yet, fall back to the
        # tax-exclusive price.
        if price.is_tax_known:
            result["price"] = str(
                Decimal(price.incl_tax)
            )

            result["tax_included"] = True

        else:
            result["price"] = str(
                Decimal(price.excl_tax)
            )

    return result


def serialize_image(image) -> dict:
    """
    Convert an Oscar ProductImage into frontend-friendly JSON.

    We return a relative URL such as:

        /media/images/...

    instead of hardcoding localhost:8000.

    That means the same JSON works in development and
    production.
    """

    return {
        "url": image.original.url,
        "caption": image.caption,
        "is_primary": image.is_primary(),
    }


def serialize_product(product, request) -> dict:
    """
    Convert an Oscar Product object into the JSON shape used
    by our Next.js frontend.

    This is deliberately our own API representation.

    We do NOT expose Oscar's entire internal database model.
    """

    categories = [
        {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
        }
        for category in product.categories.all()
    ]

    images = [
        serialize_image(image)
        for image in product.get_all_images()
    ]

    attributes = {}

    for attribute_value in product.get_attribute_values():
        attributes[
            attribute_value.attribute.code
        ] = attribute_value.value_as_text

    result = {
        "id": product.id,
        "title": product.title,
        "slug": product.slug,
        "description": product.description,
        "rating": float(product.rating) if product.rating is not None else 0.0, 
        "images": images,
        "attributes": attributes,
        "categories": categories,
        "structure": product.structure,
        "price": get_price_information(
            product,
            request,
        ),
        "children": [],
    }

    # Parent products represent a group of variants.
    #
    # Example:
    #
    # Nike Air Max
    #   ├── size 41
    #   ├── size 42
    #   └── size 43
    #
    # We expose the variants so the Next.js product page can
    # let the customer choose a specific child product.
    if product.is_parent:

        for child in product.children.all():

            result["children"].append(
                {
                    "id": child.id,
                    "title": child.title,
                    "attributes": {
                        value.attribute.code:
                        value.value_as_text
                        for value in child.get_attribute_values()
                    },
                    "price": get_price_information(
                        child,
                        request,
                    ),
                }
            )

    return result


def serialize_category(category) -> dict:
    """
    Convert an Oscar category into simple JSON.
    """

    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
    }


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

class HealthCheckView(APIView):
    """
    Very small endpoint used to check whether Django is alive.

    URL:

        GET /api/health/
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "django",
            }
        )


# ---------------------------------------------------------
# CSRF endpoint
# ---------------------------------------------------------

class CsrfTokenView(APIView):
    """
    Gives our Next.js frontend a CSRF cookie.

    Before sending login/register/logout or any future
    basket/order mutation, the frontend will call:

        GET /api/auth/csrf/

    Django then gives the browser a csrftoken cookie.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        token = get_token(request)

        return Response(
            {
                "csrfToken": token,
            }
        )


# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------

@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    """
    Login a customer using Django's session authentication.

    POST /api/auth/login/

    Body:

        {
            "email": "customer@example.com",
            "password": "password"
        }

    A successful login creates a secure Django session cookie.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        email = str(
            request.data.get("email", "")
        ).strip().lower()

        password = request.data.get(
            "password",
            "",
        )

        if not email or not password:
            return Response(
                {
                    "detail": (
                        "Email and password are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            request=request,
            username=email,
            password=password,
        )

        if user is None:

            return Response(
                {
                    "detail": "Invalid email or password."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:

            return Response(
                {
                    "detail": (
                        "This account is not active."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        login(request, user)

        return Response(
            {
                "user": serialize_user(user),
            }
        )


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    """
    Logout the currently authenticated customer.

    POST /api/auth/logout/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        logout(request)

        return Response(
            {
                "detail": "Logged out successfully."
            }
        )


@method_decorator(csrf_protect, name="dispatch")
class RegisterView(APIView):
    """
    Create a new customer account.

    POST /api/auth/register/

    Example:

        {
            "email": "customer@example.com",
            "password": "very-secure-password",
            "first_name": "John",
            "last_name": "Doe"
        }

    Django's password validation system is used so we do not
    invent our own password-security rules.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        email = str(
            request.data.get("email", "")
        ).strip().lower()

        password = request.data.get(
            "password",
            "",
        )

        first_name = str(
            request.data.get("first_name", "")
        ).strip()

        last_name = str(
            request.data.get("last_name", "")
        ).strip()

        if not email or not password:

            return Response(
                {
                    "detail": (
                        "Email and password are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        User = get_user_model()

        if User.objects.filter(
            email__iexact=email
        ).exists():

            return Response(
                {
                    "detail": (
                        "An account with this email "
                        "already exists."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # We use the email as username because Oscar's
        # email authentication backend will later allow the
        # customer to sign in using that email.
        username = email

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )

        try:
            validate_password(
                password,
                user=user,
            )

        except ValidationError as exc:

            return Response(
                {
                    "detail": exc.messages,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)

        user.save()

        login(request, user)

        return Response(
            {
                "user": serialize_user(user),
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    """
    Return the currently logged-in customer.

    GET /api/auth/me/

    The frontend can use this when the application starts
    to determine whether a customer is logged in.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response(
            {
                "user": serialize_user(
                    request.user
                )
            }
        )


# ---------------------------------------------------------
# Product listing
# ---------------------------------------------------------

class ProductListView(ListAPIView):
    """
    Return public products for the storefront.

    Supported query parameters:

        /api/products/

        /api/products/?search=nike

        /api/products/?category=shoes

    We only expose parent and standalone products here.

    Child variants are returned inside the parent product.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):

        queryset = (
            Product.objects
            .filter(
                is_public=True,
            )
            .exclude(
                structure=Product.CHILD,
            )
            .order_by(
                "-priority",
                "-date_created",
            )
        )

        search = self.request.query_params.get(
            "search"
        )

        if search:

            search = search.strip()

            queryset = queryset.filter(
                Q(title__icontains=search)
                |
                Q(description__icontains=search)
            )

        category_slug = (
            self.request.query_params.get(
                "category"
            )
        )

        if category_slug:

            queryset = queryset.filter(
                categories__slug=category_slug
            )

        return queryset.distinct()

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(
            self.get_queryset()
        )

        page = self.paginate_queryset(
            queryset
        )

        if page is not None:

            data = [
                serialize_product(
                    product,
                    request,
                )
                for product in page
            ]

            return self.get_paginated_response(
                data
            )

        data = [
            serialize_product(
                product,
                request,
            )
            for product in queryset
        ]

        return Response(data)


# ---------------------------------------------------------
# Product details
# ---------------------------------------------------------

class ProductDetailView(APIView):
    """
    Return one product.

    Example:

        GET /api/products/15/
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, slug):

        try:

            product = (
                Product.objects
                .prefetch_related(
                    "images",
                    "children__images",
                    "categories",
                )
                .get(
                    slug=slug,
                    is_public=True,
                )
)

        except Product.DoesNotExist:

            return Response(
                {
                    "detail": "Product not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Customers should not request a child as if it
        # were a separate storefront product.
        if product.is_child:

            return Response(
                {
                    "detail": "Product not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            serialize_product(
                product,
                request,
            )
        )


# ---------------------------------------------------------
# Categories
# ---------------------------------------------------------

class CategoryListView(APIView):
    """
    Return the root categories.

    Example response:

        [
            {
                "id": 1,
                "name": "Shoes",
                "slug": "shoes"
            }
        ]
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):

        categories = (
            Category.get_root_nodes()
            .filter(
                is_public=True
            )
        )

        return Response(
            [
                serialize_category(
                    category
                )
                for category in categories
            ]
        )