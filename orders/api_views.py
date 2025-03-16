from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action

from django.shortcuts import get_object_or_404

from .models import Order, OrderItem
from .serializers import FoodItemSerializer, OrderSerializer, OrderItemSerializer
from menu.models import FoodItem

class FoodItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows food items to be viewed.
    """
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orders to be created, viewed, and updated.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        user = request.user
        item_list = request.data.get('items', [])
        delivery_address = request.data.get('delivery_address', '')
        order = Order.objects.create(user=user, delivery_address=delivery_address)
        subtotal = 0.0

        for item_data in item_list:
            food_id = item_data.get('food_item_id')
            quantity = item_data.get('quantity', 1)
            food_item = get_object_or_404(FoodItem, pk=food_id)
            line_price = float(food_item.price) * quantity
            subtotal += line_price
            OrderItem.objects.create(
                order=order,
                food_item=food_item,
                quantity=quantity,
                price=food_item.price
            )

        order.total_price = subtotal
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        order.status = new_status
        order.save()
        return Response(self.get_serializer(order).data)
