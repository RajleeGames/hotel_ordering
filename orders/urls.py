from django.urls import path
from . import views  # This imports orders/views.py

urlpatterns = [
    path('add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),  # This should match the function name
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.process_payment, name='process_payment'),
]
