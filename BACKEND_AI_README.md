# BACKEND AI PROJECT CONTEXT / README

DOCUMENT_PURPOSE = "AI-oriented persistent context for the backend of a self-hosted ecommerce application."
DOCUMENT_SCOPE = "BACKEND ONLY"
PRIMARY_GOAL = "Give a future AI model enough project-specific context to continue backend development without the original conversation."
READABILITY_PRIORITY = "AI/machine context > human prose."
SOURCE_OF_TRUTH = "Project owner supplied code, configuration, errors, and confirmed outcomes from the development conversation."
CAUTION = "Do not silently replace this project's architecture with a generic Django ecommerce architecture. Preserve Django Oscar as the commerce authority and inspect the current repository before making changes."

============================================================
0. PROJECT IDENTITY
============================================================

PROJECT_TYPE = "Self-owned ecommerce website."
BUSINESS_DOMAIN = "Shoes and clothing."
BUSINESS_STAGE = "Small / early-stage business."
OWNER_PROFILE = "Frontend developer, React + Next.js, ~2 years frontend experience, zero backend development experience."
OWNER_BACKEND_KNOWLEDGE = "Beginner / zero prior backend knowledge."
OWNER_EXPECTATION = "AI assistant should explain backend concepts clearly, provide exact file paths and commands, and add useful comments to important backend code."
BUDGET = "User is not willing to pay for infrastructure/services at this stage."
HOSTING = "Completely self-hosted on user's own server."
EXTERNAL_SERVICES = "No external services except payment provider/payment processing service."
BACKEND_FRAMEWORK = "Django."
ECOMMERCE_ENGINE = "Django Oscar."
API_FRAMEWORK = "Django REST Framework."
DATABASE_DEVELOPMENT = "SQLite is acceptable for local development."
DATABASE_PRODUCTION = "PostgreSQL."
SEARCH = "Local/self-hosted search only; currently planned with Haystack + Whoosh."
APPLICATION_SERVER = "Gunicorn in production."
WEB_SERVER = "Nginx in production."
STATIC_FILES = "Django static/staticfiles; WhiteNoise during application-serving stages."
MEDIA = "Local filesystem media; production may be served by Nginx."
BACKEND_AUTH = "Django authentication/session system, with Oscar email authentication backend target."
SECURITY_PRINCIPLE = "Django/Oscar is authoritative for products, prices, stock, basket, checkout, payment verification, and orders."

============================================================
1. ORIGINAL ARCHITECTURAL GOAL
============================================================

INITIAL_FRONTEND = "NextMerce nextjs-ecommerce-template."
INITIAL_BACKEND = "Django Oscar."
FINAL_INTENDED_SYSTEM:

Browser
  -> Next.js storefront
  -> same-origin Next.js /api/*
  -> Django API
  -> Django Oscar
  -> PostgreSQL

Admin:
  -> Django Oscar Dashboard
  -> catalogue / inventory / orders / customers / offers / vouchers / etc.

Media:
  -> Django local media storage
  -> same-origin Next.js /media/* in current development architecture
  -> Nginx/local serving possible in production

PAYMENT:
  -> only planned external service
  -> payment provider performs payment processing
  -> Django/Oscar verifies the payment result before order completion

IMPORTANT_ARCHITECTURE:
"Next.js is the storefront/presentation layer. Django/Oscar is the ecommerce/business-logic/data layer."

============================================================
2. WHY DJANGO OSCAR WAS CHOSEN
============================================================

PRIMARY_REASON:
"Owner has zero backend experience and should not build ecommerce primitives from scratch."

OSCAR SHOULD PROVIDE/OWN:
- product catalogue
- categories
- product classes
- product attributes
- parent/child products (variants)
- partner
- stock records
- prices
- basket
- offers
- vouchers
- addresses
- checkout infrastructure
- orders
- customer-related ecommerce models
- dashboard/admin functionality
- shipping abstractions
- payment abstractions

DO_NOT_REIMPLEMENT_IN_CUSTOM_MODELS:
- product core
- stock core
- basket core
- order core
- offer/voucher core
unless a concrete business extension is required.

CORE_RULE:
"Extend Oscar where necessary; do not duplicate Oscar's core domain model unless there is a deliberate architecture decision."

============================================================
3. IMPORTANT DOMAIN MODEL FOR SHOES/CLOTHING
============================================================

PRODUCT_CLASS:
Defines product type and applicable attributes.

PLANNED_PRODUCT_CLASSES:
1. Shoes
   Requires shipping = Yes
   Track stock = Yes
   attributes:
      brand
      color
      size
      material

2. Clothing
   Requires shipping = Yes
   Track stock = Yes
   attributes:
      brand
      color
      size
      material
      fit

EXAMPLE_ATTRIBUTE_VALUES:
brand = Nike
color = Black
size = 42
material = Mesh

CATEGORY:
Customer-facing merchandising/grouping concept.

PLANNED_CATEGORY_TREE:
Shoes
  Sneakers
  Running
  Casual
  Boots
  Sandals

Clothing
  T-Shirts
  Hoodies
  Pants
  Jackets
  Shorts

IMPORTANT_DISTINCTION:
"Product class != category."

PRODUCT_VARIATION_MODEL:
Parent product:
  Nike Air Max 90

Child products:
  Nike Air Max 90 - size 41
  Nike Air Max 90 - size 42
  Nike Air Max 90 - size 43
  Nike Air Max 90 - size 44

STOCK/PURCHASE_RULE:
"Purchasable inventory is represented by child/standalone products and their Oscar stock records. Parent is primarily the catalogue presentation/group."

============================================================
4. BACKEND REPOSITORY STRUCTURE KNOWN
============================================================

ACTUAL_OR_REPORTED_ROOT:

backend/
  api/
  justfile
  manage.py
  requirements.txt
  venv/

DJANGO_SETTINGS_MODULE:
"core.settings" was reported from manage.py during early setup.

NOTE:
"Some prior examples used config.settings as a generic project name, but the user's actual existing manage.py was reported with core.settings. Inspect the current repository and follow the actual project module rather than copying an old path blindly."

KNOWN_BACKEND_APP:
api/

KNOWN_DJANGO_APP_ROLE:
"Our custom API layer between Next.js and Django Oscar."

IMPORTANT:
"Do not recreate Django from scratch if the project already exists."

============================================================
5. PYTHON DEPENDENCIES / REQUIREMENTS HISTORY
============================================================

USER-SUPPLIED requirements.txt INCLUDED:

Django==5.2.17
django-oscar==4.2
djangorestframework
psycopg[binary]
Pillow
gunicorn
whitenoise
sorl-thumbnail
django-haystack
Whoosh

ROLE_BY_PACKAGE:

Django
  -> web framework

django-oscar
  -> ecommerce domain/business logic

djangorestframework
  -> JSON API layer

psycopg[binary]
  -> PostgreSQL driver

Pillow
  -> image processing

gunicorn
  -> production WSGI application server

whitenoise
  -> static files support

sorl-thumbnail
  -> image thumbnail support used by Oscar/UI ecosystem

django-haystack
  -> search abstraction

Whoosh
  -> local embedded search engine

PRODUCTION_SERVICE_POLICY:
"All listed services are self-hosted/local except payment processing."

============================================================
6. SETUP HISTORY / TROUBLESHOOTING CONTEXT
============================================================

EARLY_COMMAND:
django-admin startproject config .
RESULT:
"bash: django-admin: command not found"

FOLLOW-UP:
python -m django startproject config .
RESULT:
"CommandError because manage.py already existed; overlaying a project could not replace conflicting files."

INTERPRETATION:
"Project structure already existed. Do not recreate the Django project."

django_checks/migrations:
- manage.py / Django startup initially produced tracebacks.
- User later reported that manage.py was correct / setup was okay.
- python manage.py migrate had traceback during django.setup()/apps.populate at one stage.
- Current application later reached working API endpoint, so backend is operational enough for catalogue API work.

IMPORTANT:
"Do not assume historical setup errors are still active. Test the current repository first."

============================================================
7. CURRENT API ARCHITECTURE
============================================================

CUSTOM_APP:
api/

PRIMARY_BROWSER_API:
GET /api/products/

DIRECT_DJANGO_TEST:
http://127.0.0.1:8000/api/products/

CONFIRMED:
"Direct Django product API works."

FRONTEND-FACING PROXY:
The browser calls the Next.js same-origin /api/products/ endpoint. Next.js then server-side proxies to Django.

CONFIRMED:
"http://127.0.0.1:3000/api/products/ works and returns JSON."

BACKEND_FLOW:
Next.js server/API route
  -> Django /api/products/
  -> Oscar Product/query logic
  -> JSON

IMPORTANT:
"Django should not depend on the browser knowing its internal host/port."

============================================================
8. CURRENT API ROUTE INTENT
============================================================

EXPECTED API MODULES:

/api/health/
/api/auth/csrf/
/api/auth/login/
/api/auth/register/
/api/auth/logout/
/api/auth/me/

/api/products/
/api/products/<slug>/
/api/categories/

NOT_ALL_ENDPOINTS_ARE_CONFIRMED_AS_FINISHED:
"Health/auth/product/category routes were designed/implemented during the conversation, but future AI should inspect the actual repository rather than assuming every route is production-complete."

API_DESIGN_PRINCIPLE:
"Return a deliberately designed JSON representation. Do not expose Oscar's entire internal database model."

============================================================
9. HEALTH API
============================================================

TARGET:
GET /api/health/

EXPECTED_RESPONSE:
{
  "status": "ok",
  "service": "django"
}

PURPOSE:
"Simple operational health check for development/deployment diagnostics."

============================================================
10. CSRF / SESSION AUTHENTICATION
============================================================

TARGET:
GET /api/auth/csrf/

PURPOSE:
"Initialize Django's CSRF cookie so the frontend can submit unsafe requests safely."

LOGIN:
POST /api/auth/login/

BODY:
{
  "email": "customer@example.com",
  "password": "..."
}

REGISTER:
POST /api/auth/register/

BODY:
{
  "email": "...",
  "password": "...",
  "first_name": "...",
  "last_name": "..."
}

LOGOUT:
POST /api/auth/logout/

CURRENT_USER:
GET /api/auth/me/

TARGET_AUTH_STRATEGY:
"Django session authentication."

WHY:
- same-origin application architecture
- Django already handles session security
- avoids unnecessary JWT complexity
- appropriate for Next.js + Django under one domain
- CSRF protection remains explicit

IMPORTANT_SECURITY:
- do not disable CSRF
- do not create a frontend-only authentication state
- do not store passwords in frontend/localStorage
- do not invent JWT unless explicitly decided later
- Django backend remains authentication authority

EMAIL_LOGIN:
"Oscar EmailBackend is the intended authentication backend."

USER_CREATION_TARGET:
"Email is used as the username/login identity in the current design."

VALIDATION:
"Django password validation is used instead of custom password rules."

============================================================
11. PRODUCT API
============================================================

GET:
 /api/products/

CURRENT_QUERY_FEATURES_DESIGNED:
- public products only
- exclude child products from top-level catalogue list
- order by priority/date
- optional search
- optional category filter
- distinct results

QUERY_PARAMS:
search=<text>
category=<category-slug>

TOP_LEVEL_PRODUCT_RULE:
"Top-level list contains parent/standalone products. Child variants are exposed as part of product detail/variant data."

PAGINATION:
DRF page-number pagination target.

EXPECTED_RESPONSE_SHAPE:
{
  "count": number,
  "next": string | null,
  "previous": string | null,
  "results": [...]
}

PAGE_SIZE_TARGET:
24

============================================================
12. PRODUCT SERIALIZATION CONTRACT
============================================================

FILE_CONTEXT:
api/views.py currently contains explicit serialization logic.

MAIN_FUNCTION:
serialize_product(product, request)

TARGET_PURPOSE:
"Convert Oscar Product to intentionally limited storefront JSON."

CURRENT/INTENDED_SHAPE:

{
  "id": number,
  "title": string,
  "slug": string,
  "description": string,
  "rating": number,
  "images": [...],
  "attributes": {...},
  "categories": [...],
  "structure": string,
  "price": {...},
  "children": [...]
}

IMAGE:
{
  "url": string,
  "caption": string,
  "is_primary": boolean
}

PRICE:
{
  "available": boolean,
  "availability_message": string | null,
  "currency": string | null,
  "price": string | null,
  "price_excl_tax": string | null,
  "tax": string | null,
  "tax_included": boolean,
  "stock": number | null,
  "sku": string | null
}

CHILD:
{
  "id": number,
  "title": string,
  "attributes": {...},
  "price": {...}
}

IMPORTANT_MONEY_RULE:
"Backend exposes monetary values as strings to avoid JavaScript floating point precision problems at the API boundary."

AUTHORITATIVE_PRICE_RULE:
"Next.js is never authoritative for price."

============================================================
13. OSCAR PRICING / AVAILABILITY STRATEGY
============================================================

CURRENT_DESIGN:
Use Oscar's partner pricing/availability strategy, not custom arithmetic.

CONCEPT:
Selector().strategy(request=request, user=request.user)
  -> fetch_for_product(product)

RETURNED INFORMATION MAY INCLUDE:
- price
- availability
- stockrecord

EXPECTED_SOURCE_FOR:
- availability
- currency
- final price
- tax information
- SKU
- stock

IMPORTANT:
"Price calculation belongs in Oscar/backend."

FUTURE:
Expose original-vs-final price information when storefront discounts/offers are integrated.

DO_NOT:
- trust a price submitted by browser
- calculate order total only in Next.js
- calculate stock availability only in Next.js
- accept frontend payment amount as authoritative

============================================================
14. PRODUCT RATING BUG HISTORY
============================================================

PREVIOUS_ERROR:
TypeError:
float() argument must be a string or a real number, not 'NoneType'

LOCATION:
serialize_product()
product.rating

ORIGINAL_PATTERN:
float(product.rating)

FIX:
Use:
float(product.rating) if product.rating is not None else 0.0

LESSON:
"Oscar fields may be nullable; serializers must handle null values explicitly."

IMPORTANT:
"Never silently treat unrelated values as equivalent. Rating != review count."

============================================================
15. IMAGE / MEDIA ARCHITECTURE
============================================================

OSCAR_MEDIA_OUTPUT:
relative URL such as:
 /media/images/...

CURRENT_PRODUCTION-DEV TARGET:
Django stores uploaded product media locally.

CURRENT_FRONTEND PROXY:
Next.js /media/* -> Django /media/*

BACKEND_MEDIA_ROOT:
Expected Django media directory under backend project unless current settings say otherwise.

IMPORTANT:
- product images should not be hardcoded into backend JSON
- media URLs should be generated from actual Oscar images
- production can let Nginx serve media directly
- application API should continue returning stable media paths

============================================================
16. CATEGORIES API
============================================================

GET:
 /api/categories/

CURRENT/INTENDED_RESPONSE:
[
  {
    "id": number,
    "name": string,
    "slug": string
  }
]

CURRENT_TARGET:
Return root categories initially.

FUTURE:
- nested category representation
- product counts
- category filtering
- navigation data

IMPORTANT:
"Do not hardcode category counts in frontend. Backend should supply authoritative counts."

============================================================
17. API SERIALIZER DESIGN DECISION
============================================================

CURRENT_APPROACH:
"Explicit Python serializer functions in views.py."

REASON:
- easy to understand while project is small
- explicit backend/frontend contract
- no accidental exposure of Oscar model fields

POSSIBLE_FUTURE_REFACTOR:
"Move to DRF Serializer classes once the contract stabilizes."

DO_NOT:
"Refactor to serializers merely for style if current code is working and readable."

============================================================
18. DATABASE STRATEGY
============================================================

LOCAL_DEVELOPMENT:
SQLite is acceptable for convenience.

PRODUCTION:
PostgreSQL.

WHY:
- Oscar production use case
- transactional ecommerce data
- better production database choice than SQLite

POSTGRES_DRIVER:
psycopg[binary]

EXPECTED_PRODUCTION_DATABASE:
- database name via environment
- DB user via environment
- DB password via environment
- host/port via environment

SECURITY:
"Do not hardcode production DB password in settings.py or source control."

============================================================
19. ENVIRONMENT CONFIGURATION
============================================================

TARGET_PATTERN:
Use environment variables for secrets/environment-specific values.

IMPORTANT_VARIABLES_MAY_INCLUDE:
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_CSRF_TRUSTED_ORIGINS
DATABASE_ENGINE
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD
DATABASE_HOST
DATABASE_PORT
DJANGO_SECURE_SSL_REDIRECT
DJANGO_HSTS_SECONDS

NOTE:
"Exact current settings file must be inspected before changing variable names."

SECURITY:
- no secrets in git
- no secrets in frontend public env vars
- no payment secrets in Next.js client
- production DEBUG=False
- secure cookies under HTTPS
- real SECRET_KEY in environment

============================================================
20. STATIC AND MEDIA
============================================================

STATIC_URL:
"/static/"

STATIC_ROOT:
"staticfiles" under backend unless current settings differ.

MEDIA_URL:
"/media/"

MEDIA_ROOT:
"media" under backend unless current settings differ.

DEVELOPMENT:
Django may serve local media/static when DEBUG=True.

PRODUCTION:
Nginx should serve static/media where appropriate.

IMPORTANT:
"Do not assume application server should efficiently serve large media in production."

============================================================
21. SEARCH
============================================================

CURRENT_SEARCH_DECISION:
Haystack + Whoosh.

REQUIREMENT:
"Search must be self-hosted and have no external search provider."

TARGET:
Django/Oscar search queries run locally.

CURRENT_HAYSTACK_ENGINE_TARGET:
Whoosh.

SIGNAL_PROCESSOR_TARGET:
RealtimeSignalProcessor.

FUTURE:
"Search may be upgraded to another self-hosted engine later if scale requires it, but no hosted service should be introduced without explicit approval."

============================================================
22. OSCAR DASHBOARD / ADMIN
============================================================

TARGET:
http://127.0.0.1:8000/dashboard/

ROLE:
Store-owner administration.

NEEDS_TO_SUPPORT:
- catalogue
- products
- product classes
- product attributes
- stock/inventory
- partners
- orders
- customers/users
- offers
- vouchers
- shipping
- reviews
- reports

USER_REQUESTED_EVENTUAL_UI:
"A proper shoe-store dashboard with products, orders, users, inventory, sidebar icons, custom dashboard."

IMPORTANT:
"First use Oscar's dashboard for functionality. Customize visual appearance/workflow only after core ecommerce flow is stable."

============================================================
23. API URL STRUCTURE
============================================================

TARGET_CONFIG_CONCEPT:
Root Django URLs include:
- API under /api/
- Oscar under the main/root URL configuration where dashboard is reachable at /dashboard/
- Django admin may remain available under /admin/ if needed

IMPORTANT:
"Keep API and dashboard concerns separate."

============================================================
24. FRONTEND/BACKEND DATA OWNERSHIP
============================================================

PRODUCT:
Oscar authoritative.

CATEGORY:
Oscar authoritative.

ATTRIBUTE:
Oscar authoritative.

VARIANT:
Oscar child product authoritative.

SKU:
Oscar stock record authoritative.

STOCK:
Oscar stock record authoritative.

PRICE:
Oscar strategy/stock/offer system authoritative.

DISCOUNT:
Oscar offer system authoritative.

BASKET:
Oscar basket authoritative.

ORDER:
Oscar order authoritative.

CUSTOMER:
Django/Oscar user/customer system authoritative.

ADDRESS:
Oscar/Django backend authoritative.

PAYMENT_STATUS:
Backend/payment verification authoritative.

UI:
Next.js authoritative only for presentation state, not business truth.

============================================================
25. BASKET PLAN
============================================================

NOT_YET_COMPLETE:
"Basket integration is the next major backend ecommerce feature after catalogue/product page."

TARGET:
POST /api/basket/items/
PATCH/PUT quantity endpoints
DELETE item endpoints
GET /api/basket/

EXPECTED_FLOW:
Next.js product page
  -> choose child variant
  -> POST basket item
  -> Django/Oscar basket
  -> Oscar validates product/stock/pricing
  -> response contains basket state
  -> Next.js renders state

IMPORTANT:
- basket is server-side
- stock checked by backend
- price calculated by backend
- quantity validated by backend
- browser cannot set authoritative total
- anonymous baskets should be supported initially if desired by Oscar configuration

============================================================
26. CHECKOUT PLAN
============================================================

TARGET_ORDER:
1. basket
2. customer/auth if required by chosen flow
3. address
4. shipping method
5. order review
6. payment initiation
7. payment provider response
8. backend/payment verification
9. order placement/finalization
10. confirmation

IMPORTANT:
"The frontend must not be trusted to declare payment success."

============================================================
27. PAYMENT PLAN
============================================================

EXTERNAL_SERVICE_EXCEPTION:
"Payment provider is the only intentionally permitted external service."

PAYMENT_RULES:
- provider-specific integration lives in backend/payment layer
- secret credentials stay server-side
- browser receives public/client-safe information only
- payment result must be verified server-side
- order is not considered paid merely because frontend says so
- final order/payment state is backend truth

IMPORTANT:
"Do not select a provider based on current unsupported assumptions. Determine provider later based on the business's required market/country/payment method."

============================================================
28. SHIPPING PLAN
============================================================

INITIAL_REQUIREMENT:
All shoes/clothes require shipping.

FUTURE:
- shipping methods
- shipping charge calculation
- destination constraints
- delivery estimates
- integration with Oscar checkout/shipping abstractions

IMPORTANT:
"Do not create a custom shipping system until Oscar's shipping application is evaluated."

============================================================
29. CUSTOMER / USER API PLAN
============================================================

REQUIRED_CUSTOMER_FEATURES:
- register
- login
- logout
- current user
- profile
- addresses
- order history
- order details

ADMIN_USER_API:
"User list API was also requested earlier. The final endpoint/security design must distinguish customer-facing account APIs from staff/admin APIs."

SECURITY:
"Do not make user-list data public."

STAFF:
Use Django permissions/is_staff or appropriate authorization for admin-only operations.

============================================================
30. PRODUCT API ENDPOINT DETAIL PLAN
============================================================

CUSTOMER_URL_TARGET:
 /products/<slug>

BACKEND_API_TARGET:
 /api/products/<slug>/

REASON:
- semantic URL
- SEO
- cleaner storefront routing
- slug already exists on Oscar Product

EXPECTED_PRODUCT_DETAIL_CONTENT:
- id
- title
- slug
- description
- category data
- all product images
- attributes
- parent/child structure
- variant IDs
- variant attributes
- variant prices
- variant availability
- SKU
- stock as appropriate

============================================================
31. CUSTOM CODE VS OSCAR CODE
============================================================

CUSTOM_BACKEND_CODE:
api/
  views.py
  urls.py
  serializers.py
  future services/permissions/validators as justified

OSCAR_CORE_CODE:
"Do not modify installed package source code."

EXTENDING_OSCAR:
"Use Django configuration, subclassing, custom apps/models only where Oscar extension points require them."

IMPORTANT:
"Before adding a new model, ask whether Oscar already models the concept."

============================================================
32. SECURITY BASELINE
============================================================

DEVELOPMENT:
DEBUG=True may be used locally.

PRODUCTION:
DEBUG=False.

REQUIRED_PRODUCTION_SECURITY:
- strong DJANGO_SECRET_KEY
- ALLOWED_HOSTS
- HTTPS
- secure session cookie
- secure CSRF cookie
- CSRF protection
- same-site cookie settings
- HSTS after HTTPS is correctly established
- X-Content-Type-Options / nosniff
- clickjacking protection
- trusted origins
- proper reverse proxy headers
- staff access protection
- secret management
- database least privilege
- backups

DO_NOT:
- ALLOWED_HOSTS=["*"] as a lazy permanent production solution
- disable CSRF
- expose DEBUG tracebacks
- hardcode passwords
- accept frontend prices
- trust frontend stock
- trust frontend payment status
- expose internal model fields unnecessarily

============================================================
33. API AUTHORIZATION RULES
============================================================

PUBLIC:
- product listing
- public product detail
- public categories
- health endpoint

AUTHENTICATED:
- current-user
- customer basket when tied to account
- addresses
- order history
- checkout actions

STAFF/AUTHORIZED:
- user administration
- order management
- inventory management
- dashboard-specific operations

IMPORTANT:
"Use explicit DRF permissions. Do not rely on obscurity of URLs."

============================================================
34. ERROR HANDLING
============================================================

API SHOULD RETURN:
- appropriate HTTP status
- concise safe error detail
- no Python traceback to customer

EXPECTED_STATUS_CLASSES:
400 -> invalid input
401/403 -> authentication/authorization
404 -> resource not found
409 -> state conflict when appropriate
422 -> if deliberately used for semantic validation
500 -> unexpected server error

LOGGING:
"Server logs should contain diagnostic detail not exposed to browser."

============================================================
35. TEST STRATEGY
============================================================

MINIMUM_FUTURE_TESTS:
- health endpoint
- product list
- product detail
- category list
- login
- register
- logout
- current user
- CSRF protection
- basket add/remove/quantity
- stock limits
- price calculations
- checkout
- payment verification
- order creation
- unauthorized access
- staff-only endpoints

IMPORTANT_ECOMMERCE_TEST:
"Attempt to manipulate price/quantity/order totals from frontend and verify backend ignores/rejects invalid authoritative values."

============================================================
36. PERFORMANCE / QUERYING RULES
============================================================

CATALOGUE:
- paginate product lists
- use select_related/prefetch_related where justified
- avoid N+1 image/category/variant queries
- do not load entire product database into memory for storefront requests

CURRENT_SERIALIZER:
Uses prefetch_related for image/child/category in product detail context.

FUTURE:
"Profile actual slow queries before adding complexity."

============================================================
37. DATA INTEGRITY
============================================================

IMPORTANT:
Ecommerce operations require transactional integrity.

FUTURE_CRITICAL_AREAS:
- basket quantity changes
- stock allocation
- checkout
- order placement
- payment finalization
- order state transitions

TARGET:
Use Django/Oscar transactions and domain rules rather than manual multi-step unprotected writes.

============================================================
38. BACKUP / RECOVERY PLAN
============================================================

PRODUCTION:
- regular PostgreSQL backups
- media backup
- environment/secrets recovery plan
- migration discipline
- restore testing

IMPORTANT:
"Self-hosted does not mean no backup."

============================================================
39. DEPLOYMENT TARGET
============================================================

SERVER:
User-owned server.

TARGET_STACK:
Nginx
  -> Next.js
  -> Django/Gunicorn
  -> PostgreSQL

MEDIA:
Nginx/local filesystem.

STATIC:
Nginx/collected static or WhiteNoise where appropriate.

PROCESS_MANAGEMENT:
"Exact supervisor/systemd/Docker choice not yet finalized."

IMPORTANT:
"Do not introduce Docker unless it provides a concrete operational benefit for this project."

============================================================
40. CURRENT DEVELOPMENT COMMANDS
============================================================

BACKEND:
cd backend

VIRTUAL_ENV:
venv/

START_DJANGO:
python manage.py runserver

DIRECT_API:
http://127.0.0.1:8000/api/products/

DASHBOARD:
http://127.0.0.1:8000/dashboard/

ADMIN:
http://127.0.0.1:8000/admin/

NOTE:
"Exact manage.py/settings module in the current repository should be inspected before writing commands that assume a project package name."

============================================================
41. BACKEND DEVELOPMENT WORKFLOW FOR AI
============================================================

WHEN_ADDING_FEATURE:
1. Understand the ecommerce domain requirement.
2. Check whether Oscar already provides the concept.
3. Check actual installed Oscar version/API.
4. Inspect current project code.
5. Define/confirm API contract.
6. Add/update backend endpoint.
7. Add permissions.
8. Add validation.
9. Add tests.
10. Confirm response shape.
11. Tell frontend exactly what changed.
12. Avoid unrelated refactors.

WHEN_BUG:
1. Reproduce.
2. Identify exact traceback/file/line.
3. Confirm whether the problem is custom API code or Oscar behavior.
4. Prefer fixing custom integration code rather than modifying Oscar internals.
5. Add a regression test where appropriate.

============================================================
42. KNOWN FRONTEND CONTRACT
============================================================

FRONTEND_EXPECTS_STOREPRODUCT:
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

NEXTMERCE_LEGACY_PRODUCT:
{
  title,
  reviews,
  price,
  discountedPrice,
  id,
  imgs
}

FRONTEND_ADAPTER:
"Next.js currently converts StoreProduct into legacy NextMerce Product shape for existing UI components."

BACKEND_RULE:
"Do not distort Oscar business data merely to satisfy legacy UI shape. Use an adapter/view model on the frontend."

============================================================
43. CURRENT STATIC DATA MIGRATION
============================================================

NEXTMERCE_STATIC_DATA:
shopData.ts contains demo products.

KNOWN_DEMO_ITEMS:
- Havit HV-G69 USB Gamepad
- iPhone 14 Plus, 6/128GB
- Apple iMac M1 24-inch 2021
- MacBook Air M1 chip, 8/256GB
- Apple Watch Ultra
- Logitech MX Master 3 Mouse
- Apple iPad Air 5th Gen - 64GB
- Asus RT Dual Band Router

BACKEND_POLICY:
"These are not backend product data. The backend should never be adapted to keep fake template products alive."

============================================================
44. CURRENT PROJECT STATUS
============================================================

CONFIRMED_WORKING:
- Django backend project exists.
- Django Oscar installed.
- DRF installed.
- Product catalogue can be managed via Oscar/dashboard.
- Direct Django product API works.
- Next.js server proxy to /api/products/ works.
- Product JSON reaches frontend.
- Product image/media path works through Next.js media proxy.
- Product rating null crash has been identified and guarded in intended serializer code.
- Parent/child product strategy for variants is established.
- Shoes/Clothing product class concept established.

STILL_IN_PROGRESS:
- complete production-quality product serializer/API contract
- product detail by slug
- dynamic categories/filtering
- real product-card integration in NextMerce
- basket API
- authentication frontend integration
- customer/account APIs
- addresses
- shipping
- checkout
- payment provider integration
- order lifecycle
- admin/dashboard visual customization
- production deployment
- backup/monitoring
- exhaustive security hardening

============================================================
45. DEVELOPMENT ROADMAP FROM CURRENT POINT TO FINISH
============================================================

STAGE_1_CATALOGUE:
DONE/PARTIAL:
- product classes
- category concept
- attributes
- sample parent/child products
- stock
- product images
- product list API
- media proxy

NEXT:
- product detail API by slug
- product card integration
- product detail UI
- variant selection

STAGE_2_FILTERING:
- categories
- brand
- size
- color
- price
- availability
- pagination
- search

STAGE_3_BASKET:
- get basket
- add item
- update quantity
- remove item
- clear basket
- server-side stock/price validation

STAGE_4_CUSTOMER:
- CSRF
- register
- login
- logout
- current user
- profile
- addresses
- customer orders

STAGE_5_CHECKOUT:
- address selection
- shipping method
- checkout summary
- totals
- validation

STAGE_6_PAYMENT:
- provider configuration
- server-side payment initiation
- callback/webhook or provider verification
- idempotency
- paid/failed/pending states

STAGE_7_ORDERS:
- create/finalize order
- order status
- order detail
- customer order history
- staff order management

STAGE_8_ADMIN:
- custom shoe-store dashboard
- navigation
- inventory views
- product management UX
- order management UX
- customer management
- reports

STAGE_9_PRODUCTION:
- PostgreSQL
- Nginx
- Gunicorn
- static/media
- HTTPS
- environment secrets
- database backups
- logging
- monitoring/health checks
- deployment scripts
- server hardening

============================================================
46. IMPORTANT AI GUARDRAILS
============================================================

AN_AI_WORKING_ON_BACKEND_MUST:
1. Read this README first.
2. Inspect actual files before modifying them.
3. Preserve Django Oscar as commerce authority.
4. Do not create duplicate ecommerce systems.
5. Do not invent fields/endpoints not confirmed by code.
6. Do not assume every prior proposed snippet is currently present; distinguish planned vs confirmed.
7. Explain backend concepts to the owner in simple terms when responding.
8. Give exact commands and file paths.
9. Add meaningful comments to new complex backend functions.
10. Keep secrets out of source control.
11. Never expose payment secrets to frontend.
12. Never trust browser price/stock/payment state.
13. Use explicit DRF permissions.
14. Preserve CSRF/session security.
15. Prefer local/self-hosted solutions.
16. Don't add paid/external infrastructure without explicit approval.
17. Don't modify Oscar package source directly.
18. Test after each meaningful backend change.
19. Use Oscar extension points before inventing custom abstractions.
20. Avoid unnecessary dependencies.
21. Avoid generic Django rewrites that ignore the current project.
22. If a requirement depends on current Oscar behavior, inspect installed version/documentation before making claims.

============================================================
47. EXPLANATION STYLE FOR THE OWNER
============================================================

OWNER_IS_FRONTEND_DEVELOPER:
Use React/Next.js analogies when useful.

EXAMPLE:
"API endpoint ≈ backend function route"
"Serializer ≈ DTO mapper"
"Model ≈ persistent database entity"
"Queryset ≈ database query builder"
"Permission class ≈ route guard"
"Session cookie ≈ backend-managed login state"

BUT:
"Do not oversimplify security-critical concepts."

FOR_EACH_MAJOR_BACKEND_CHANGE:
- explain what the file does
- explain why it exists
- explain how frontend calls it
- explain what data it accepts/returns
- explain common errors
- state how to test it

============================================================
48. FINAL SYSTEM VISION
============================================================

FINAL_ARCHITECTURE:

                        CUSTOMER
                           |
                           v
                     Next.js / UI
                           |
                      same-origin
                        /api/*
                           |
                           v
                    Django REST API
                           |
                           v
                      Django Oscar
                           |
          +----------------+----------------+
          |                |                |
       Catalogue         Basket           Orders
          |                |                |
       Products         Checkout        Payments
       Categories        Shipping        Customer
       Variants          Offers          Addresses
       Stock             Vouchers        Order state
          |
          v
                      PostgreSQL

Files/media:
  Django local media filesystem
  -> Nginx in production

Search:
  Haystack + local Whoosh

Admin:
  Oscar Dashboard

Payment:
  external provider only

SECURITY_MODEL:
- backend is authoritative
- session + CSRF authentication
- server-side price/stock/order/payment verification
- secrets server-side only

COST_MODEL:
- self-hosted
- open-source software
- no paid SaaS dependencies
- payment provider is the only external paid/required service exception

END_OF_BACKEND_CONTEXT
