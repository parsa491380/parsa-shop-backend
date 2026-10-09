# BACKEND AI CONTEXT - CURRENT PROJECT STATE

PROJECT_PURPOSE = "Current Django/Oscar backend context for an AI continuation model."
SOURCE_OF_TRUTH = "Actual repository code is authoritative. This file is documentation only."
BUSINESS = "Small self-hosted shoes/clothing shop."
OWNER = "React/Next.js frontend developer; zero backend experience."
BACKEND = "Django 5.2.17 + Django Oscar 4.2 + Django REST Framework."
PRODUCTION_DB = "PostgreSQL."
LOCAL_DB = "SQLite is currently used for development."
SEARCH = "Haystack + Whoosh, local/self-hosted."
EXTERNAL_SERVICES = "None except payment provider."

============================================================
CURRENT SERVER ARCHITECTURE
============================================================

Browser
  -> Next.js same-origin /api/*
  -> Django API
  -> Oscar
  -> SQLite (dev) / PostgreSQL (prod)

Media
  -> local filesystem in Django
  -> Nginx in production

Admin
  -> Oscar Dashboard at /dashboard/

Production target:
Nginx -> Next.js
Next.js server proxy -> Django/Gunicorn
Django -> PostgreSQL
Nginx -> /media and /static

============================================================
DJANGO PROJECT
============================================================

manage.py uses:
DJANGO_SETTINGS_MODULE=config.settings

Key app:
api/

Important files:
config/settings.py
config/urls.py
api/views.py
api/urls.py
api/tests.py
api/management/commands/bootstrap_store.py

============================================================
DEPENDENCIES
============================================================

Django==5.2.17
django-oscar==4.2
djangorestframework
psycopg[binary]
Pillow
gunicorn
whitenoise
sorl-thumbnail
easy-thumbnails
django-haystack
Whoosh
django-widget-tweaks
django-treebeard
django-tables2
pycountry

requirements-dev.txt also exists for development tooling.

============================================================
DONT REBUILD OSCAR
============================================================

Oscar is authoritative for:
- catalogue
- product classes
- attributes
- parent/child variants
- stock records
- pricing strategy
- basket
- offers/vouchers
- addresses
- shipping abstractions
- orders
- dashboard
- customer/ecommerce models

Do not build a custom duplicate product/basket/order/stock system unless a real extension requirement exists.

============================================================
PRODUCT MODELING DECISION
============================================================

Product classes:
Shoes:
  brand
  color
  size
  material

Clothing:
  brand
  color
  size
  material
  fit

Shipping = required.
Stock tracking = enabled.

Variant model:
Parent product
  -> child product per purchasable variant

Example:
Nike Air Max 90
  -> 41
  -> 42
  -> 43
  -> 44

Stock, SKU and actual purchase price belong to the purchasable stock record/child product.

============================================================
CURRENT CUSTOM API
============================================================

Base prefix = /api/

Health:
GET /api/health/

Authentication:
GET /api/auth/csrf/
POST /api/auth/login/
POST /api/auth/register/
POST /api/auth/logout/
GET /api/auth/me/

Catalogue:
GET /api/products/
GET /api/products/<slug>/
GET /api/categories/
GET /api/countries/

Basket:
GET /api/basket/
DELETE /api/basket/
POST /api/basket/items/
PUT /api/basket/items/<line_id>/
DELETE /api/basket/items/<line_id>/

Shipping/checkout:
GET /api/shipping/methods/
POST /api/checkout/orders/

Customer/account:
GET /api/orders/
GET /api/orders/<number>/
GET /api/addresses/
POST /api/addresses/
DELETE /api/addresses/<id>/

============================================================
PRODUCT API CONTRACT
============================================================

Top-level product response:
{
  id,
  title,
  slug,
  description,
  rating,
  images,
  attributes,
  categories,
  structure,
  price,
  children
}

Price DTO:
{
  available,
  availability_message,
  currency,
  price,
  price_excl_tax,
  tax,
  tax_included,
  stock,
  sku
}

Money values are serialized as strings.

Product list:
- public products only
- excludes child products from top-level list
- prefetches images/categories/attributes/children
- supports search
- supports category slug
- supports sort latest/oldest/priority/price_asc/price_desc
- uses DRF page-number pagination, page size 24

IMPORTANT:
DB sort by stockrecord price is only a best-effort catalogue ordering.
Actual customer price is resolved by Oscar strategy.

============================================================
PRICE / AVAILABILITY
============================================================

get_price_information(product, request) uses Oscar's strategy.

Parent product:
strategy.fetch_for_parent(product)

Standalone/child:
strategy.fetch_for_product(product)

The API uses Oscar availability + stockrecord + price information.
Frontend does not determine authoritative price/stock.

============================================================
BASKET
============================================================

BasketMiddleware provides request.basket.

Basket endpoint behavior:
- anonymous baskets supported
- authenticated baskets supported
- parent products cannot be added directly
- child/standalone products are added
- Oscar availability checks are relied on for authoritative validation
- update/delete operations are server-side
- basket totals are serialized from Oscar

Basket strategy is explicitly assigned using get_strategy(request) before basket modifications.

============================================================
AUTHENTICATION
============================================================

Django session authentication.

Oscar email auth backend is configured.

Registration:
- email becomes username
- Django password validators run
- password is set with set_password()
- user is logged in immediately

CSRF:
- GET /api/auth/csrf/ initializes cookie
- unsafe endpoints use csrf_protect
- frontend sends X-CSRFToken

Do not disable CSRF.
Do not store authentication secrets in frontend local storage.

============================================================
CATEGORIES
============================================================

Category API returns public categories, ordered by tree path.
Each category includes:
- id
- name
- slug
- product_count
- depth
- image

product_count includes public non-child products assigned to the category or descendants.

============================================================
COUNTRIES
============================================================

Country API only exposes Oscar countries where is_shipping_country=True.

requirements.txt includes pycountry.

Project management command:
python manage.py bootstrap_store

Implementation calls Oscar's:
oscar_populate_countries

Run bootstrap after migrations in a fresh environment.

============================================================
SHIPPING
============================================================

Current shipping implementation = Oscar Free() shipping method.

GET /api/shipping/methods/
returns Standard shipping with zero charge.

This is intentional MVP behavior.
Future real shipping rates/methods should be integrated through Oscar shipping abstractions.

============================================================
CHECKOUT / PAYMENT
============================================================

POST /api/checkout/orders/ creates an Oscar order from the current basket only when:
CHECKOUT_ALLOW_PENDING_ORDERS = True

In production settings this is expected to be False until the real payment provider is integrated.

When enabled for development:
- basket is validated
- shipping country is validated
- shipping address is validated
- free shipping charge is calculated
- OrderTotalCalculator calculates total
- OrderCreator.place_order creates the pending order
- basket.submit() submits the basket

Payment is NOT marked successful by this endpoint.

CRITICAL:
"No frontend payment-success signal is trusted."

Production must add:
- payment initiation
- provider credentials in environment
- provider callback/webhook/verification
- idempotency
- only then mark/order transition to paid/completed state

Provider was intentionally not chosen because the project owner wants to decide the payment service later.

============================================================
ORDER PIPELINE
============================================================

Current settings:
Pending -> Being processed / Cancelled
Being processed -> Processed / Cancelled
Processed -> Shipped / Cancelled
Shipped -> Delivered
Delivered / Cancelled -> terminal

Initial order status = Pending.
Initial line status = Pending.

============================================================
ADDRESSES
============================================================

Oscar UserAddress is used for saved customer addresses.
Oscar ShippingAddress is used for order shipping address snapshot.

Address API is authenticated and validates country/address data.

============================================================
DATABASE
============================================================

Local:
SQLite db.sqlite3 currently exists as a development snapshot with sample catalogue/media.

Production:
PostgreSQL.

Never commit production credentials.
Use environment variables:
DATABASE_ENGINE
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD
DATABASE_HOST
DATABASE_PORT

============================================================
MEDIA / STATIC
============================================================

MEDIA_URL = /media/
MEDIA_ROOT = backend/media

Static root = backend/staticfiles

Development:
Django may serve media/static.

Production:
Nginx should serve static/media directly.

============================================================
SEARCH
============================================================

Haystack + Whoosh.
Local only.
No hosted search provider.

Whoosh index is regenerated automatically and is ignored by git.

============================================================
SETTINGS / SECURITY
============================================================

Settings are environment-driven.

Important variables:
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_CSRF_TRUSTED_ORIGINS
DATABASE_*
OSCAR_DEFAULT_CURRENCY
CHECKOUT_ALLOW_PENDING_ORDERS
DJANGO_SECURE_SSL_REDIRECT
DJANGO_HSTS_SECONDS

Production expectations:
- DEBUG=False
- strong secret
- correct ALLOWED_HOSTS
- HTTPS
- secure session cookie
- secure CSRF cookie
- trusted origins
- HSTS only after HTTPS is correct
- never expose DEBUG tracebacks

============================================================
TESTING STATUS
============================================================

api/tests.py contains basic tests for:
- health
- public product list
- public categories
- unknown product 404
- register/current-user with CSRF

Static verification:
- Python compileall passes on the current backend.

Runtime Django/Oscar tests were not executed in the analysis container because the Python dependencies were not installed there.
Run locally:
python manage.py check
python manage.py test

============================================================
DEVELOPMENT COMMANDS
============================================================

python -m venv venv

Windows:
venv\\Scripts\\activate

Install:
python -m pip install -r requirements.txt

Migrate:
python manage.py migrate

Bootstrap countries:
python manage.py bootstrap_store

Create admin:
python manage.py createsuperuser

Run:
python manage.py runserver

Dashboard:
http://127.0.0.1:8000/dashboard/

============================================================
NEXT STEPS
============================================================

1. Select and integrate a payment provider.
2. Add real shipping rates if required.
3. Add real review count/submission endpoints.
4. Persist wishlist if desired.
5. Improve search/filtering with product attributes.
6. PostgreSQL production deployment.
7. Nginx + Gunicorn production deployment.
8. Backups and operational hardening.
9. Customize Oscar dashboard after core checkout/payment is stable.

============================================================
AI RULES
============================================================

- inspect actual installed Oscar version/API before changing domain code
- do not modify Oscar package source
- do not create duplicate product/stock/basket/order models
- use Oscar extension points
- never trust browser price/stock/payment result
- never expose secrets to frontend
- keep API JSON explicit and minimal
- use transactions for ecommerce state changes
- return safe API errors; log internal details server-side
- explain backend concepts clearly to the project owner
