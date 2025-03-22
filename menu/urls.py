# menu/urls.py
from django.urls import path
from .views import menu_view
from .views import customer_support_view

urlpatterns = [
    path('', menu_view, name='menu'),
    path('customer-support/', customer_support_view, name='customer_support'),
]
