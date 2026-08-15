"""
File: apps/products/serializers.py
Description: Packages Category and Product database models into JSON. Includes SEO metadata so Next.js can render perfect HTML <head> tags.
Related Files: apps/products/models.py, apps/products/views.py
"""

from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    """Formats category data, useful for sidebar navigations and dropdown menus."""
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'meta_title', 'meta_description')

class ProductSerializer(serializers.ModelSerializer):
    """
    Formats the complete product profile. 
    We nest the CategorySerializer so the frontend knows exactly which category this product belongs to without a second API call.
    """
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'category', 'name', 'slug', 'description', 
            'price', 'stock_quantity', 'image', 'image_alt_text', 
            'meta_title', 'meta_description', 'is_active'
        )