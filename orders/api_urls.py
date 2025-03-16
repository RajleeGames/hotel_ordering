# orders/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import FoodItemViewSet, OrderViewSet

router = DefaultRouter()
router.register('food-items', FoodItemViewSet, basename='food-items')
router.register('orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
]
