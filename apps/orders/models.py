"""
File: apps/orders/models.py
Description: Defines the database schema for customer Orders and individual Order Items.
Related Files: apps/orders/serializers.py, apps/orders/views.py.
"""

from django.db import models
from django.conf import settings
from apps.products.models import Product


class Order(models.Model):
	"""
	Represents a customer's checkout session and overall receipt.
	"""

	# Order Status Choices
	PENDING = 'Pending'
	PAID = 'Paid'
	SHIPPED = 'Shipped'
	DELIVERED = 'Delivered'
	CANCELLED = 'Cancelled'

	STATUS_CHOICES = [
		(PENDING, 'Pending'),
		(PAID, 'Paid'),
		(SHIPPED, 'Shipped'),
		(DELIVERED, 'Delivered'),
		(CANCELLED, 'Cancelled'),
	]

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE
	)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
	total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
	shipping_address = models.TextField(
		help_text='The address where this specific order will be delivered.'
	)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f'Order #{self.id} by {self.user.email}'


class OrderItem(models.Model):
	"""
	Represents a specific product and its quantity within a larger Order.
	"""

	order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(
		Product, related_name='order_items', on_delete=models.SET_NULL, null=True
	)
	quantity = models.PositiveIntegerField(default=1)

	# We save the price here in case the product price changes in the future,
	# ensuring historical receipts remain accurate.
	price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f'{self.quantity}x {self.product.name} (Order #{self.order.id})'
