"""
File: apps/orders/views.py
Description: Contains the logic for customers to place new orders and view their past order history.
Related Files: apps/orders/serializers.py, apps/orders/urls.py
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import CheckoutSerializer

class CheckoutAPIView(generics.CreateAPIView):
    """
    API Endpoint: POST /api/orders/checkout/
    Purpose: Accepts a shipping address and a list of cart items to create a new order.
    """
    serializer_class = CheckoutSerializer
    permission_classes = [IsAuthenticated] # Must be logged in to buy

    def create(self, request, *args, **kwargs):
        """
        Overrides the default response to send a clean success message back to Next.js.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        return Response({
            "message": "Order placed successfully!",
            "order_id": order.id,
            "total_amount": order.total_amount
        }, status=status.HTTP_201_CREATED)