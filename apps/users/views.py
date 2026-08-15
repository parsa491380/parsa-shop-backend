from django.shortcuts import render

"""
File: apps/users/views.py
Description: Contains the logic for the User API endpoints (Registering and viewing profiles).
Related Files: apps/users/serializers.py, apps/users/urls.py
"""

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserProfileSerializer

User = get_user_model()

class RegisterUserAPIView(generics.CreateAPIView):
    """
    API Endpoint: POST /api/users/register/
    Purpose: Accepts user details in JSON format and creates a new account.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    # AllowAny means anyone can access this endpoint without a token (since they don't have an account yet!)
    permission_classes = [AllowAny] 

class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    API Endpoint: GET or PUT /api/users/profile/
    Purpose: Retrieves or updates the logged-in user's profile information.
    """
    serializer_class = UserProfileSerializer
    # IsAuthenticated means a valid JWT token must be in the HTTP headers to access this
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Instead of looking up a user by an ID in the URL, this automatically 
        returns the user associated with the provided JWT token.
        """
        return self.request.user