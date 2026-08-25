"""
File: apps/orders/admin.py
Description: Configures the order management system. Uses "Inlines" to show the
individual items purchased directly inside the main order receipt.
"""

from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
	"""
	Allows you to see the individual items (shirts, shoes, etc.)
	on the exact same page as the main Order receipt.
	"""

	model = OrderItem
	extra = 0  # Don't show empty extra rows by default
	readonly_fields = ('product', 'quantity', 'price_at_purchase')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
	list_filter = ('status', 'created_at')
	search_fields = ('user__email', 'id')
	readonly_fields = ('total_amount',)

	# Attach the inline items defined above
	inlines = [OrderItemInline]
