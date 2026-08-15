"""
File: apps/users/admin.py
Description: Configures how user accounts are displayed and managed in the Admin dashboard.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """
    Extends the default UserAdmin to display our custom e-commerce fields.
    """
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'is_staff']
    
    # We must reorganize the detail view to include our custom fields
    fieldsets = UserAdmin.fieldsets + (
        ('E-Commerce Details', {'fields': ('phone_number', 'default_shipping_address')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)