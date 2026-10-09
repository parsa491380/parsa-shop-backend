# Shoes & Clothing Store - Django/Oscar Backend

This backend uses Django + Django Oscar + Django REST Framework.

## Run locally

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\\venv\\Scripts\\Activate.ps1
```

Install:

```bash
python -m pip install -r requirements.txt
```

Migrate:

```bash
python manage.py migrate
```

Populate Oscar shipping countries:

```bash
python manage.py bootstrap_store
```

Create dashboard administrator:

```bash
python manage.py createsuperuser
```

Run:

```bash
python manage.py runserver
```

Dashboard:
http://127.0.0.1:8000/dashboard/

## API

The frontend uses same-origin Next.js API routes that proxy to:

- `/api/products/`
- `/api/products/<slug>/`
- `/api/categories/`
- `/api/countries/`
- `/api/basket/`
- `/api/auth/*`
- `/api/addresses/`
- `/api/orders/`
- `/api/shipping/methods/`
- `/api/checkout/orders/`

## Production

Use PostgreSQL, not the development SQLite database.

Set `CHECKOUT_ALLOW_PENDING_ORDERS=False` until a real payment provider is integrated and verified server-side.

## AI context

Read `BACKEND_AI_README.md` and `../PROJECT_STATUS_CURRENT.md` before changing architecture.
