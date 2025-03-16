# orders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

import stripe

from menu.models import FoodItem
from .models import Order, OrderItem, Coupon

stripe.api_key = settings.STRIPE_SECRET_KEY


def process_payment(request):
    """
    Process Stripe payment.
    """
    if request.method == 'POST':
        token = request.POST.get('stripeToken')
        amount = int(float(request.POST.get('amount')) * 100)  # Convert to cents
        try:
            stripe.Charge.create(
                amount=amount,
                currency='usd',
                description='Hotel Order Payment',
                source=token,
            )
            messages.success(request, "Payment successful!")
            # Adjust if you need to pass a specific order_id here.
            return redirect('order_confirmation')
        except stripe.error.CardError as e:
            messages.error(request, f"Payment error: {e}")
            return redirect('checkout')
    return render(request, 'orders/payment.html')


def add_to_cart(request, item_id):
    """
    Add a FoodItem to the session-based cart with optional quantity from POST data.
    """
    cart = request.session.get('cart', {})
    food_item = get_object_or_404(FoodItem, id=item_id)

    # If a POST form has 'quantity', use it; otherwise default to 1
    quantity = 1
    if request.method == 'POST':
        qty_str = request.POST.get('quantity', '1')
        quantity = max(int(qty_str), 1)  # ensure quantity >= 1

    item_key = str(item_id)
    if item_key in cart:
        cart[item_key]['quantity'] += quantity
    else:
        cart[item_key] = {
            'name': food_item.name,
            'price': str(food_item.price),  # store as string; convert later
            'quantity': quantity,
        }

    request.session['cart'] = cart
    messages.success(request, f"Added {food_item.name} x{quantity} to your cart.")
    return redirect('menu')


def increment_cart_item(request, item_id):
    """
    Increase the quantity of a cart item by 1.
    """
    cart = request.session.get('cart', {})
    item_key = str(item_id)
    if item_key in cart:
        cart[item_key]['quantity'] += 1
    request.session['cart'] = cart
    return redirect('view_cart')


def decrement_cart_item(request, item_id):
    """
    Decrease the quantity of a cart item by 1. Remove if quantity hits zero.
    """
    cart = request.session.get('cart', {})
    item_key = str(item_id)
    if item_key in cart:
        cart[item_key]['quantity'] -= 1
        if cart[item_key]['quantity'] <= 0:
            del cart[item_key]
    request.session['cart'] = cart
    return redirect('view_cart')


def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    item_key = str(item_id)
    if item_key in cart:
        # Grab the item name before removing it
        removed_item_name = cart[item_key]['name']
        del cart[item_key]
        messages.info(request, f"Removed {removed_item_name} from cart.")
    else:
        messages.warning(request, "Item not found in cart.")
    
    request.session['cart'] = cart
    return redirect('view_cart')



def view_cart(request):
    """
    Display the current cart with a total calculation.
    """
    cart = request.session.get('cart', {})
    total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    context = {
        'cart': cart,
        'total': total,
    }
    return render(request, 'orders/cart.html', context)


def checkout(request):
    """
    Checkout view that handles coupon code processing,
    creates an Order and corresponding OrderItems, applies discount,
    and then clears the cart.
    """
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('menu')

    discount_amount = 0

    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                discount_amount = coupon.discount_amount
            except Coupon.DoesNotExist:
                messages.warning(request, "Invalid or inactive coupon code.")

        # Create the Order for the logged-in user.
        order = Order.objects.create(user=request.user)
        subtotal = 0

        # Create OrderItem for each item in the cart.
        for item_id, item_data in cart.items():
            food_item = get_object_or_404(FoodItem, pk=int(item_id))
            line_price = float(item_data['price']) * item_data['quantity']
            subtotal += line_price

            OrderItem.objects.create(
                order=order,
                food_item=food_item,
                quantity=item_data['quantity'],
                price=float(item_data['price'])
            )

        # Apply discount if any.
        total = subtotal - float(discount_amount)
        order.total_price = total if total > 0 else 0
        order.save()

        # Clear the cart.
        request.session['cart'] = {}
        messages.success(request, "Your order has been placed!")
        return redirect('order_confirmation', order_id=order.id)

    total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    context = {
        'cart': cart,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)


def order_confirmation(request, order_id):
    """
    Display the order confirmation page with order details.
    """
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    return render(request, 'orders/order_confirmation.html', context)


@staff_member_required
def manage_orders(request):
    """
    Staff-only view to manage orders.
    """
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders/manage_orders.html', {'orders': orders})


@staff_member_required
def update_order_status(request, order_id, new_status):
    """
    Staff-only view to update an order's status.
    """
    order = get_object_or_404(Order, pk=order_id)
    order.status = new_status
    order.save()
    return redirect('manage_orders')
