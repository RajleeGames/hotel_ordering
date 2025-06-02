from django.urls import path
from . import views
from .views import order_status_api, track_order  # Import both order_status_api and track_order
from .views import my_orders, order_detail

urlpatterns = [
    path('add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('pay_order/<int:order_id>/', views.pay_order, name='pay_order'),  # ✅ Add this
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('status/<int:order_id>/', order_status_api, name='order_status_api'),
    path('track/<int:order_id>/', track_order, name='track_order'),
     path('my-orders/', my_orders, name='my_orders'),
      path('<int:order_id>/', order_detail, name='order_detail'),
    
    # New Cart Update URLs
    path('increment/<int:item_id>/', views.increment_cart_item, name='increment_cart_item'),
    path('decrement/<int:item_id>/', views.decrement_cart_item, name='decrement_cart_item'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Staff management
    path('manage/', views.manage_orders, name='manage_orders'),
    path('update_status/<int:order_id>/<str:new_status>/', views.update_order_status, name='update_order_status'),
]
