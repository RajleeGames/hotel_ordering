from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from datetime import date, timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import stripe

from .models import Order, OrderItem, Coupon, Driver
from menu.models import FoodItem

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
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('menu')

    discount_amount = 0
    delivery_fee = 1000  # Fixed delivery fee

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

        net_total = subtotal - float(discount_amount)
        gross_total = net_total + delivery_fee

        order.total_price = gross_total if gross_total > 0 else 0
        order.save()

        # Clear the cart.
        request.session['cart'] = {}
        messages.success(request, "Your order has been placed!")
        
        # Redirect to the Pesapal payment view, passing the order ID.
        return redirect('pay_order', order_id=order.id)
    
    # GET: show checkout page with summary details.
    subtotal = sum(float(item['price']) * item['quantity'] for item in cart.values())
    net_total = subtotal
    gross_total = net_total + delivery_fee
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'gross_total': gross_total,
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
    # Grab the 'date_filter' from GET parameters
    date_filter = request.GET.get('date_filter', '')
    orders = Order.objects.all()

    # Apply filter logic based on selected option
    if date_filter == 'today':
        orders = orders.filter(created_at__date=date.today())
    elif date_filter == 'yesterday':
        orders = orders.filter(created_at__date=date.today() - timedelta(days=1))
    elif date_filter == 'last_7_days':
        start_date = date.today() - timedelta(days=7)
        orders = orders.filter(created_at__date__gte=start_date)

    context = {
        'orders': orders,
    }
    return render(request, 'orders/manage_orders.html', context)


@staff_member_required
def update_order_status(request, order_id, new_status):
    """
    Staff-only view to update an order's status.
    """
    order = get_object_or_404(Order, pk=order_id)
    order.status = new_status
    order.save()
    return redirect('manage_orders')


@login_required
def order_status_api(request, order_id):
    """
    Returns JSON with the order status and driver location.
    Only accessible to the user who placed the order (or staff).
    """
    # Restrict to the user’s own order (or staff/superuser).
    if request.user.is_staff:
        order = get_object_or_404(Order, pk=order_id)
    else:
        order = get_object_or_404(Order, pk=order_id, user=request.user)

    data = {
        'status': order.status,
        'driver_lat': float(order.driver_lat) if order.driver_lat else None,
        'driver_lng': float(order.driver_lng) if order.driver_lng else None,
        'total_price': float(order.total_price) if order.total_price else 0.0
    }
    return JsonResponse(data)


@login_required
def track_order(request, order_id):
    """
    Track a specific order. Also fetch all drivers to display as default deliverers.
    """
    # Restrict to user’s own order or staff
    if request.user.is_staff:
        order = get_object_or_404(Order, pk=order_id)
    else:
        order = get_object_or_404(Order, pk=order_id, user=request.user)

    # Get the first available driver (if any)
    driver = Driver.objects.first()

    return render(request, 'orders/track_order.html', {
        'order': order,
        'driver': driver,
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Get filters from GET request
    order_id_filter = request.GET.get('order_id', '').strip()
    status_filter = request.GET.get('status', '').strip()

    # Apply filters
    if order_id_filter:
        orders = orders.filter(id=order_id_filter)

    if status_filter:
        orders = orders.filter(status__iexact=status_filter)  # Case-insensitive match

    # Return JSON response if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        orders_data = [
            {
                'id': order.id,
                'date': order.created_at.strftime('%b %d, %Y'),
                'total_price': str(order.total_price),
                'status': order.status,
                'detail_url': f"/orders/order/{order.id}/"
            }
            for order in orders
        ]
        return JsonResponse({'orders': orders_data})

    return render(request, 'orders/my_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Use the assigned driver if available, otherwise default to the first available driver.
    driver = order.driver if hasattr(order, 'driver') and order.driver else Driver.objects.first()
    items_total = sum(item.quantity * item.price for item in order.items.all())
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items_total': items_total,
        'driver': driver,
    })
