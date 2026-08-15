"""
File: apps/products/urls.py
Description: Maps the product API endpoints.
"""

from django.urls import path
from .views import ProductListAPIView, ProductDetailAPIView

urlpatterns = [
    path('', ProductListAPIView.as_view(), name='api-product-list'),
    path('<slug:slug>/', ProductDetailAPIView.as_view(), name='api-product-detail'),
]