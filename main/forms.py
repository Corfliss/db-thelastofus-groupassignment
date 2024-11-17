from django import forms

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
