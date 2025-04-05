# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'profile_picture', 'password1']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password1'}),
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # Remove help texts for all fields
        for field in self.fields.values():
            field.help_text = ""
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
          
          
          
           
        # Remove the password2 field if it exists
        if 'password2' in self.fields:
            self.fields.pop('password2')

    def clean_password2(self):
        """
        Since password2 is removed, just return password1.
        This method overrides the parent validation.
        """
        return self.cleaned_data.get('password1')




class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']  # or 'username', etc.

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'profile_picture']


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

class PasswordResetCodeForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)
    code = forms.CharField(label="Verification Code", max_length=6)

class SetNewPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())  # hidden email field
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password")
        p2 = cleaned_data.get("confirm_password")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
