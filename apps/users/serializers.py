"""
File: apps/users/serializers.py
Description: Translates CustomUser database models into JSON data for the frontend, and validates incoming JSON data to safely create new users.
Related Files: apps/users/models.py, apps/users/views.py
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

# Fetch our CustomUser model
User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
	"""
	Handles the validation and secure creation of a new user.
	Ensures passwords are securely hashed before saving to the database.
	"""

	# Write_only ensures the password is never sent back to the frontend in the API response
	password = serializers.CharField(
		write_only=True, min_length=8, style={'input_type': 'password'}
	)

	class Meta:
		model = User
		fields = ('id', 'email', 'password', 'first_name', 'last_name')

	def create(self, validated_data):
		"""
		Overrides the default save method to use Django's secure create_user method,
		which automatically hashes the password.
		"""
		user = User.objects.create_user(
			email=validated_data['email'],
			username=validated_data['email'],  # We use email as the username
			password=validated_data['password'],
			first_name=validated_data.get('first_name', ''),
			last_name=validated_data.get('last_name', ''),
		)
		return user


class UserProfileSerializer(serializers.ModelSerializer):
	"""
	Formats the user's public and private profile data to be sent to the frontend.
	Used for the "My Account" page in Next.js.
	"""

	class Meta:
		model = User
		fields = (
			'id',
			'email',
			'first_name',
			'last_name',
			'phone_number',
			'default_shipping_address',
		)
		read_only_fields = (
			'email',
		)  # Prevent users from changing their email via profile update
