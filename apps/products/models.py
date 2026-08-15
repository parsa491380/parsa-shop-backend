"""
File: apps/products/models.py
Description: Defines the database schema for Categories and Products. Includes SEO metadata fields.
Related Files: apps/products/serializers.py, apps/products/views.py.
"""

from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    """
    Groups products together. Includes SEO fields for category landing pages.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="URL friendly name (e.g., 'summer-shirts'). Auto-generated if left blank.")
    description = models.TextField(blank=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=60, blank=True, help_text="Ideal length: 50-60 characters for search engines.")
    meta_description = models.CharField(max_length=160, blank=True, help_text="Ideal length: 150-160 characters for search engines.")

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        """Automatically generate a URL-friendly slug from the category name if one isn't provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Represents an individual item for sale. Contains pricing, inventory, and SEO data.
    """
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Auto-generated URL string.")
    description = models.TextField()
    
    # Pricing & Inventory
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Product price in your local currency.")
    stock_quantity = models.PositiveIntegerField(default=0, help_text="Current number of items available for sale.")
    
    # Media & SEO
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image_alt_text = models.CharField(max_length=255, blank=True, help_text="Crucial for screen readers and image SEO.")
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this product from the storefront.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Automatically generate a slug from the product name for clean URLs."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name