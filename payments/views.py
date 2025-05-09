import uuid  # Imported uuid for generating unique IDs
import requests
import hmac, hashlib, base64
from urllib.parse import urlencode
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .forms import PaymentForm
from .models import Payment

# Import Order model from your orders app for integration in pay_order view.
from orders.models import Order


def generate_order_reference():
    """Generate a unique order reference."""
    return str(uuid.uuid4())


def sign_request(data_string, consumer_secret):
    """Sign the data string using HMAC-SHA1 and return the signature."""
    hashed = hmac.new(consumer_secret.encode(), data_string.encode(), hashlib.sha1)
    return base64.b64encode(hashed.digest()).decode()


def initiate_payment(request):
    """Initiate a Pesapal payment from a stand-alone payment form."""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            order_ref = generate_order_reference()

            # Create a Payment record in the database
            payment = Payment.objects.create(
                order_reference=order_ref,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone_number=data['phone_number'],
                amount=data['amount'],
                currency=data['currency'],
            )

            # Package the payload for Pesapal according to their requirements.
            payload = {
                'pesapal_merchant_reference': order_ref,
                'pesapal_description': 'Food Order Payment',
                'amount': str(data['amount']),
                'currency': data['currency'],
                'callback_url': settings.PESAPAL_CALLBACK_URL,
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
                'phone_number': data['phone_number'],
            }

            # Create a query string of the payload and sign it.
            query_string = urlencode(payload)
            signature = sign_request(query_string, settings.PESAPAL_CONSUMER_SECRET)
            payload['signature'] = signature

            # Prepare headers with a realistic User-Agent.
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }

            # Post the request to Pesapal's sandbox endpoint (for API 3.0)
            pesapal_url = settings.PESAPAL_API_URL + '/create_payment'
            try:
                response = requests.post(pesapal_url, json=payload, headers=headers)
                if response.status_code == 200:
                    resp_data = response.json()  # Expected to include a redirect_url.
                    redirect_url = resp_data.get('redirect_url')
                    if redirect_url:
                        # Optionally, store the transaction ID from Pesapal.
                        payment.pesapal_transaction_id = resp_data.get('pesapal_transaction_id', '')
                        payment.save()
                        return redirect(redirect_url)
                    else:
                        return HttpResponse("Error: Payment URL not received from Pesapal.", status=400)
                else:
                    return HttpResponse(f"Error initiating payment: HTTP {response.status_code}", status=400)
            except Exception as e:
                return HttpResponse("Exception occurred: " + str(e), status=500)
    else:
        form = PaymentForm()
    return render(request, 'initiate_payment.html', {'form': form})


def get_access_token():
    """
    Get an access token using Pesapal API 3.0.
    This uses the endpoint and headers as shown in your cURL example.
    """
    url = f"{settings.PESAPAL_API_URL}/Auth/RequestToken"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        # Including a realistic User-Agent helps avoid Cloudflare blocking.
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    data = {
        "consumer_key": settings.PESAPAL_CONSUMER_KEY,
        "consumer_secret": settings.PESAPAL_CONSUMER_SECRET
    }
    try:
        response = requests.post(url, json=data, headers=headers)
    except Exception as e:
        raise Exception(f"Request failed: {str(e)}")

    # Debug output
    print("Access Token Response Status:", response.status_code)
    print("Access Token Response Text:", response.text)

    if 'application/json' not in response.headers.get('Content-Type', ''):
        raise Exception("Unexpected Content-Type: " + response.headers.get('Content-Type', ''))

    try:
        resp_json = response.json()
    except Exception as e:
        raise Exception("Error parsing JSON response: " + str(e))

    token = resp_json.get('token')
    if not token:
        raise Exception("Failed to retrieve access token from Pesapal. Response: " + response.text)
    return token


@csrf_exempt
def pesapal_get_token(request):
    """
    Returns a JSON response with an access token obtained from Pesapal.
    """
    url = f"{settings.PESAPAL_API_URL}/Auth/RequestToken"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "consumer_key": settings.PESAPAL_CONSUMER_KEY,
        "consumer_secret": settings.PESAPAL_CONSUMER_SECRET
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return JsonResponse(response.json(), status=200)
        else:
            return JsonResponse({"error": response.text}, status=response.status_code)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def pay_order(request, order_id):
    """
    Initiate payment for a specific order.
    Ensures the order exists and belongs to the current user.
    """
    # Ensure the order exists and belongs to the current user.
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Instead of filtering on a non-existent 'order' field, we filter by the order_reference.
    existing_payment = Payment.objects.filter(order_reference__startswith=f"{order.id}-").first()
    if existing_payment:
        return redirect(existing_payment.redirect_url or settings.PESAPAL_CALLBACK_URL)

    try:
        token = get_access_token()

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

        # Generate a unique order reference that includes the order id.
        order_reference = f"{order.id}-{uuid.uuid4()}"

        # Build the payload ensuring proper formatting.
        payload = {
            "id": order_reference,
            "currency": "KES",
            "amount": f"{order.total_price:.2f}",
            "description": "Food Order Payment",
            "callback_url": request.build_absolute_uri('/payments/payment_callback/'),
            "notification_id": settings.PESAPAL_NOTIFICATION_ID,
            "billing_address": {
                "email_address": request.user.email,
                "phone_number": getattr(order, 'phone_number', "0712345678"),
                "first_name": request.user.first_name or "FirstName",
                "last_name": request.user.last_name or "LastName",
                "line_1": "Nairobi",
                "city": "Nairobi",
                "country_code": "KE"
            }
        }

        url = f"{settings.PESAPAL_API_URL}/api/transactions/submitorderrequest"
        res = requests.post(url, json=payload, headers=headers)

        if res.status_code == 200:
            data = res.json()
            redirect_url = data.get('redirect_url')
            tracking_id = data.get('order_tracking_id')

            Payment.objects.create(
                order_reference=order_reference,
                pesapal_transaction_id=tracking_id,
                amount=order.total_price,
                currency="KES",
            )

            return redirect(redirect_url)
        else:
            print("Pesapal Error:", res.status_code, res.text)
            return HttpResponse("Failed to create Pesapal order", status=400)

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


def payment_callback(request):
    """
    Called by Pesapal after the user completes a payment.
    Updates the Payment record with transaction details.
    """
    order_ref = request.GET.get('pesapal_merchant_reference')
    tracking_id = request.GET.get('pesapal_transaction_tracking_id')
    transaction_status = request.GET.get('transaction_status')
    try:
        payment = Payment.objects.get(order_reference=order_ref)
        payment.pesapal_transaction_id = tracking_id
        payment.transaction_status = transaction_status
        payment.save()
    except Payment.DoesNotExist:
        return HttpResponse("Invalid payment reference.", status=404)
    return render(request, 'payment_callback.html', {'payment': payment})


@csrf_exempt
def ipn_listener(request):
    """
    Listens for Pesapal Instant Payment Notifications (IPN) and updates the Payment.
    """
    if request.method == 'POST':
        order_ref = request.POST.get('pesapal_merchant_reference', '').strip()
        print("Received Order Ref:", repr(order_ref))
        tracking_id = request.POST.get('pesapal_transaction_tracking_id')
        transaction_status = request.POST.get('transaction_status')
        try:
            payment = Payment.objects.get(order_reference=order_ref)
            payment.pesapal_transaction_id = tracking_id
            payment.transaction_status = transaction_status
            payment.save()
        except Payment.DoesNotExist:
            return HttpResponse("Payment not found.", status=404)
        return HttpResponse("IPN Received")
    return HttpResponse("Only POST method allowed.", status=405)
