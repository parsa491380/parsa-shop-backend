"""
File: apps/orders/serializers.py
Description: Handles the complex logic of safely receiving cart items from the frontend, verifying prices in the database, and generating a final Order receipt.
Related Files: apps/orders/models.py, apps/orders/views.py
"""

from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.models import Product

class CartItemInputSerializer(serializers.Serializer):
    """
    Validates the data coming from the Next.js frontend cart.
    We only ask for the product ID and quantity. We calculate the price ourselves.
    """
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class CheckoutSerializer(serializers.Serializer):
    """
    The master serializer for processing a checkout session.
    """
    shipping_address = serializers.CharField()
    items = CartItemInputSerializer(many=True)

    def create(self, validated_data):
        """
        This function executes when the frontend sends a valid checkout request.
        It creates the Order, locks in the prices, and calculates the grand total securely.
        """
        # 1. Extract data
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        shipping_address = validated_data['shipping_address']
        
        # 2. Create the empty receipt (Order)
        order = Order.objects.create(
            user=user, 
            shipping_address=shipping_address, 
            total_amount=0.00
        )
        
        grand_total = 0
        
        # 3. Process each item in the cart
        for item_data in items_data:
            # Fetch the actual product from the database to get the real price
            product = Product.objects.get(id=item_data['product_id'])
            quantity = item_data['quantity']
            
            # Create the line-item on the receipt
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=product.price
            )
            
            # Add to the grand total
            grand_total += (product.price * quantity)
            
            # (Optional Future Step): Deduct quantity from product.stock_quantity here
            
        # 4. Save the final calculated total to the order
        order.total_amount = grand_total
        order.save()
        
        return order