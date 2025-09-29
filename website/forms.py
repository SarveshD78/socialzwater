# website/forms.py
from django import forms
from .models import (
    QRLandingInquiry,
)

class QRLandingForm(forms.ModelForm):
    class Meta:
        model = QRLandingInquiry
        fields = ['full_name', 'phone_number', 'email_address', 'how_found_us']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'type': 'tel',
                'required': True
            }),
            'email_address': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'required': True
            }),
            'how_found_us': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'full_name': '',
            'phone_number': '',
            'email_address': '',
            'how_found_us': '',
        }

