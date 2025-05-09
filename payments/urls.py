# payments/urls.py
from django.urls import path
from . import views
from .views import pesapal_get_token

urlpatterns = [
    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
    path('ipn_listener/', views.ipn_listener, name='ipn_listener'),
    path('pay_order/<int:order_id>/', views.pay_order, name='pay_order'),
    path('get-token/', pesapal_get_token, name='pesapal_get_token'),
    path('get-token/', views.pesapal_get_token, name='pesapal_get_token'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
    path('ipn_listener/', views.ipn_listener, name='ipn_listener'),
]
