# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required


from .forms import UserUpdateForm, ProfileUpdateForm

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

    return render(request, 'accounts/signup.html', {'form': form})


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
    return redirect('login')



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
            return redirect('profile')  # Refresh the page
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile.html', context)

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
