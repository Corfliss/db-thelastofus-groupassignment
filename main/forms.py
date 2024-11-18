from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import CustomUser

class TopUpForm(forms.Form):
    top_up_amount = forms.DecimalField(
        label="Top-Up Amount", 
        min_value=0.01, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter top-up amount'})
    )

class ServicePaymentForm(forms.Form):
    service_session = forms.ChoiceField(
        label="Service Session",
        choices=[],  # To be dynamically populated in the view
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    service_price = forms.DecimalField(
        label="Service Price",
        disabled=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

class TransferForm(forms.Form):
    recipient_phone = forms.CharField(
        label="Recipient's Phone Number",
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter recipient's phone number"})
    )
    transfer_amount = forms.DecimalField(
        label="Transfer Amount",
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter transfer amount'})
    )

class WithdrawalForm(forms.Form):
    bank_name = forms.ChoiceField(
        label="Bank Name",
        choices=[
            ('gopay', 'GoPay'),
            ('ovo', 'OVO'),
            ('virtual_account_bca', 'Virtual Account BCA'),
            ('bni', 'BNI'),
            ('mandiri', 'Mandiri'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    bank_account_number = forms.CharField(
        label="Bank Account Number",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter bank account number'})
    )
    withdrawal_amount = forms.DecimalField(
        label="Withdrawal Amount",
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter withdrawal amount'})
    )

# Define choices for user types
USER_TYPE_CHOICES = [
    ('customer', 'Customer'),
    ('worker', 'Worker'),
]

# Define choices for worker bank names
BANK_NAME_CHOICES = [
    ('GoPay', 'GoPay'),
    ('OVO', 'OVO'),
    ('Virtual Account BCA', 'Virtual Account BCA'),
    ('Virtual Account BNI', 'Virtual Account BNI'),
    ('Virtual Account Mandiri', 'Virtual Account Mandiri'),
]

class CustomerRegistrationForm(UserCreationForm):
    sex = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')], label="Sex")
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Birth Date")

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'sex', 'phone_number', 'birthdate', 'address']
        labels = {
            'username': 'Name',
            'phone_number': 'Phone Number',
            'address': 'Address',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'customer'
        if commit:
            user.save()
        return user

class WorkerRegistrationForm(UserCreationForm):
    sex = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')], label="Sex")
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Birth Date")
    bank_name = forms.ChoiceField(choices=BANK_NAME_CHOICES, label="Bank Name")
    accountnumber = forms.CharField(label="Account Number")
    npwp = forms.CharField(label="NPWP")  # Worker ID
    image_url = forms.URLField(label="Image URL", required=False)  # Optional profile picture

    class Meta:
        model = CustomUser
        fields = [
            'username', 'password1', 'password2', 'sex', 'phone_number', 
            'birthdate', 'address', 'bank_name', 'accountnumber', 'npwp', 'image_url',
        ]
        labels = {
            'username': 'Name',
            'phone_number': 'Phone Number',
            'address': 'Address',
            'accountnumber' : 'Account Number',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'worker'
        if commit:
            user.save()
        return user 