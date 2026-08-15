"""
File: apps/products/admin.py
Description: Configures the store catalog in the Admin dashboard. 
Includes automatic slug generation for perfect SEO.
"""

from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    # This is magic: As you type the category name, it automatically types out the SEO slug!
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    # Makes it easy to quickly edit prices and stock directly from the list view
    list_editable = ('price', 'stock_quantity', 'is_active')