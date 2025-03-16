from rest_framework import serializers
from .models import Order, OrderItem
from menu.models import FoodItem

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'price', 'image', 'description', 'category']

class OrderItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'total_price', 'delivery_address', 'items']
        read_only_fields = ['user', 'status', 'created_at', 'total_price']
