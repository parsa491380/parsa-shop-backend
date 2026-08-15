# NextMerce Django Backend

A fully self-hosted, RESTful Django backend designed to power the NextMerce Next.js frontend.

## Features

- **JWT Authentication:** Secure stateless authentication for frontend communication.
- **Modular Architecture:** Cleanly separated apps for Users, Products, Cart, and Orders.
- **SEO Optimized:** Product models include metadata fields (slugs, alt-texts, meta descriptions) to feed the Next.js server-side rendering for optimal search engine rankings.
- **Customizable Admin:** Built-in Django admin panel for easy store management.

## Prerequisites

- Python 3.10+
- Virtual Environment

## Local Setup (Windows)

1. **Clone the repository and navigate into it**
2. **Create a virtual environment:**
   `python -m venv venv`
3. **Activate the virtual environment:**
   `venv\Scripts\activate`
4. **Install dependencies:**
   `pip install -r requirements.txt`
5. **Run database migrations:**
   `python manage.py migrate`
6. **Create a superuser for the Admin Panel:**
   `python manage.py createsuperuser`
7. **Start the development server:**
   `python manage.py runserver`

The API will be available at `http://127.0.0.1:8000/api/`.
