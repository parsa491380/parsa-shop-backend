"""
File: apps/users/models.py
Description: Defines the database schema for Users in the e-commerce platform.
Related Files: apps/users/serializers.py (for API formatting), apps/users/views.py (for API logic).
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
	"""
	Extends the default Django user to include e-commerce specific data.
	Using email as the primary contact and login identifier is standard for modern web apps.
	"""

	email = models.EmailField(
		unique=True, help_text="User's email address, used for login and notifications."
	)
	phone_number = models.CharField(
		max_length=20,
		blank=True,
		null=True,
		help_text='Contact number for shipping updates.',
	)
	default_shipping_address = models.TextField(
		blank=True, null=True, help_text='Saved shipping address for faster checkout.'
	)

	# We tell Django to use 'email' for logging in instead of a 'username'
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	def __str__(self):
		"""Returns the string representation of the user (their email)."""
		return self.email
