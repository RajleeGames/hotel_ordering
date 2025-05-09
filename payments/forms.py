# payments/forms.py
from django import forms

class PaymentForm(forms.Form):
    first_name = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    phone_number = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number'})
    )
    amount = forms.DecimalField(decimal_places=2)
    currency = forms.CharField(max_length=10, initial='TZS', widget=forms.HiddenInput())
