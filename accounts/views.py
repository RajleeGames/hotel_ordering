# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
import random
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import PasswordResetEmailForm, PasswordResetCodeForm, SetNewPasswordForm
from .models import PasswordResetCode
from django.contrib.auth import get_user_model


def signup(request):
    """
    Handles user registration with phone number + optional profile picture.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the User (and triggers the post_save signal to create Profile).
            user = form.save()

            # Update the new Profile with phone_number & profile_picture
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            user.profile.profile_picture = form.cleaned_data.get('profile_picture')
            user.profile.save()

            # Optionally log the user in immediately
            login(request, user)
            messages.success(request, "Your account has been created successfully!")
            return redirect('menu')  # or wherever you want
    else:
        form = SignUpForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('menu')  # or wherever you want
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('intro')


@login_required
def profile_view(request):
    """View and edit profile details."""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('profiles')  # Redirect to the "profiles" URL
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profiles.html', context)


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Creates the User and triggers Profile creation
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            user.profile.save()
            login(request, user)
            return redirect('menu')
    else:
        form = SignUpForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_site_view(request):
    return render(request, 'profile_site.html')



User = get_user_model()

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "No user with that email exists.")
                return redirect('password_reset_request')
            # Generate a random 6-digit code.
            code = f"{random.randint(100000, 999999)}"
            PasswordResetCode.objects.create(user=user, code=code)
            # Send email (adjust email subject and message as needed)
            send_mail(
                subject="Your Password Reset Code",
                message=f"Your password reset code is: {code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            messages.success(request, "A verification code has been sent to your email.")
            return redirect('password_reset_verify')
    else:
        form = PasswordResetEmailForm()
    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_verify(request):
    if request.method == "POST":
        form = PasswordResetCodeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            code_input = form.cleaned_data['code']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Invalid email.")
                return redirect('password_reset_verify')
            # Get the latest code for the user
            try:
                reset_code = PasswordResetCode.objects.filter(user=user).latest('created_at')
            except PasswordResetCode.DoesNotExist:
                messages.error(request, "No reset code found, please request a new one.")
                return redirect('password_reset_request')
            if reset_code.is_expired():
                messages.error(request, "Your code has expired. Please request a new one.")
                return redirect('password_reset_request')
            if reset_code.code != code_input:
                messages.error(request, "Invalid verification code.")
                return redirect('password_reset_verify')
            # Code is valid; redirect to set new password view.
            return redirect('password_reset_set', email=email)
    else:
        form = PasswordResetCodeForm()
    return render(request, 'accounts/password_reset_verify.html', {'form': form})


from django.contrib.auth.hashers import make_password

def password_reset_set(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "Invalid email.")
        return redirect('password_reset_request')
        
    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect('login')
    else:
        form = SetNewPasswordForm(initial={'email': email})
    return render(request, 'accounts/password_reset_set.html', {'form': form})

