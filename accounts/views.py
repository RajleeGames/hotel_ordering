# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import SignUpForm


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # This creates the User and triggers the signal to create a Profile.
            # Update the Profile with phone and address data:
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            
            user.profile.save()
            login(request, user)  # Optionally log in the user after registration.
            return redirect('menu')  # Redirect to your home or menu page.
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
            return redirect('menu')  # Redirect to your menu page
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # This creates the User
            # Update the Profile with phone & address
            user.profile.phone_number = form.cleaned_data.get('phone_number')
        
            user.profile.save()

            # Optionally log the user in immediately
            login(request, user)
            return redirect('menu')  # Or wherever you want to send them
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})
