"""
File: apps/products/views.py
Description: The logic for listing all products and fetching a single product's details.
Related Files: apps/products/serializers.py, apps/products/urls.py
"""

from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class ProductListAPIView(generics.ListAPIView):
	"""
	API Endpoint: GET /api/products/
	Purpose: Returns a list of all active products in the store.
	"""

	# We only want to show products that are marked as active
	queryset = Product.objects.filter(is_active=True).order_by('-created_at')
	serializer_class = ProductSerializer
	permission_classes = [AllowAny]  # Anyone can view products


class ProductDetailAPIView(generics.RetrieveAPIView):
	"""
	API Endpoint: GET /api/products/<slug>/
	Purpose: Fetches the details of a single product using its SEO-friendly slug.
	"""

	queryset = Product.objects.filter(is_active=True)
	serializer_class = ProductSerializer
	permission_classes = [AllowAny]
	lookup_field = (
		'slug'  # This tells Django to search by slug instead of the default ID
	)
