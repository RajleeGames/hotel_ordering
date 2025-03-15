# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from menu.models import FoodItem
from orders.models import Order, OrderItem
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def process_payment(request):
    if request.method == 'POST':
        token = request.POST.get('stripeToken')
        amount = int(float(request.POST.get('amount')) * 100)  # Convert dollars to cents
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency='usd',
                description='Hotel Order Payment',
                source=token,
            )
            messages.success(request, "Payment successful!")
            return redirect('order_confirmation')
        except stripe.error.CardError as e:
            messages.error(request, "Payment error: " + str(e))
            return redirect('checkout')
    return render(request, 'orders/payment.html')

def add_to_cart(request, item_id):
    cart = request.session.get('cart', {})
    food_item = get_object_or_404(FoodItem, id=item_id)
    if str(item_id) in cart:
        cart[str(item_id)]['quantity'] += 1
    else:
        cart[str(item_id)] = {
            'name': food_item.name,
            'price': str(food_item.price),
            'quantity': 1,
        }
    request.session['cart'] = cart
    messages.success(request, f"Added {food_item.name} to your cart.")
    return redirect('menu')

def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    context = {
        'cart': cart,
        'total': total,
    }
    return render(request, 'orders/cart.html', context)

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('menu')
    
    if request.method == 'POST':
        order = Order.objects.create(user=request.user)
        for item_id, item_data in cart.items():
            OrderItem.objects.create(
                order=order,
                food_item_id=item_id,
                quantity=item_data['quantity'],
                price=item_data['price']
            )
        request.session['cart'] = {}
        messages.success(request, "Your order has been placed!")
        return redirect('order_confirmation', order_id=order.id)
    
    total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    context = {
        'cart': cart,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)
