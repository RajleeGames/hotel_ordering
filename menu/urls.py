# menu/urls.py
from django.urls import path
from .views import menu_view, toggle_favorite, customer_support_view

urlpatterns = [
    path('', menu_view, name='menu'),
    path('customer-support/', customer_support_view, name='customer_support'),
    path('toggle-favorite/<int:item_id>/', toggle_favorite, name='toggle_favorite'),
]
