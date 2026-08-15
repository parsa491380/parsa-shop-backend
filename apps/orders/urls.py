"""
File: apps/orders/urls.py
Description: Maps the order API endpoints.
"""

from django.urls import path
from .views import CheckoutAPIView

urlpatterns = [
    path('checkout/', CheckoutAPIView.as_view(), name='api-checkout'),
]