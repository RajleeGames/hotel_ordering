from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.process_payment, name='process_payment'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # New Cart Update URLs
    path('increment/<int:item_id>/', views.increment_cart_item, name='increment_cart_item'),
    path('decrement/<int:item_id>/', views.decrement_cart_item, name='decrement_cart_item'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Staff management
    path('manage/', views.manage_orders, name='manage_orders'),
    path('update_status/<int:order_id>/<str:new_status>/', views.update_order_status, name='update_order_status'),
]
