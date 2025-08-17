# website/forms.py
from django import forms
from .models import (
    QRLandingInquiry,
    BusinessHotelInquiry,
    SmartBrandInquiry,
    EarnWithUsInquiry,
    ContactInquiry
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


class BusinessHotelForm(forms.ModelForm):
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the Terms & Conditions and Privacy Policy'
    )
    
    class Meta:
        model = BusinessHotelInquiry
        fields = [
            'business_name', 'contact_person', 'business_type', 'phone_number',
            'business_email', 'targeted_area', 'business_address', 'monthly_requirement'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'business_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel',
                'required': True
            }),
            'business_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'targeted_area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mumbai, Delhi, Bangalore',
                'required': True
            }),
            'business_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Complete business address'
            }),
            'monthly_requirement': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'business_name': 'Business Name *',
            'contact_person': 'Contact Person *',
            'business_type': 'Business Type *',
            'phone_number': 'Phone Number *',
            'business_email': 'Business Email *',
            'targeted_area': 'Service Area/Region *',
            'business_address': 'Business Address',
            'monthly_requirement': 'Monthly Water Bottle Requirement',
        }


class SmartBrandForm(forms.ModelForm):
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the Terms & Conditions and Privacy Policy'
    )
    
    class Meta:
        model = SmartBrandInquiry
        fields = [
            'company_name', 'contact_person', 'business_email', 'phone_number',
            'industry_type', 'targeted_area', 'website_url', 'company_description',
            'budget_range', 'target_audience', 'social_instagram', 'video_duration'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'business_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel',
                'required': True
            }),
            'industry_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'targeted_area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mumbai, Delhi, Bangalore',
                'required': True
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'company_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of your company and products/services'
            }),
            'budget_range': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'target_audience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your ideal customer (age, interests, location, etc.)'
            }),
            'social_instagram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@yourhandle'
            }),
            'video_duration': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'company_name': 'Company Name *',
            'contact_person': 'Contact Person *',
            'business_email': 'Business Email *',
            'phone_number': 'Phone Number *',
            'industry_type': 'Industry/Business Type *',
            'targeted_area': 'Targeted Area/Market *',
            'website_url': 'Website URL',
            'company_description': 'Company Description',
            'budget_range': 'Advertising Budget Range *',
            'target_audience': 'Target Audience Demographics',
            'social_instagram': 'Instagram Handle',
            'video_duration': 'Preferred Video Ad Duration',
        }


class EarnWithUsForm(forms.ModelForm):
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the Terms & Conditions and Privacy Policy'
    )
    agree_contact = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I would like to receive updates and promotional materials about partnership opportunities via email and SMS.'
    )
    
    class Meta:
        model = EarnWithUsInquiry
        fields = [
            'full_name', 'phone_number', 'email_address', 'partnership_type',
            'company_name', 'service_areas', 'referral_source'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel',
                'required': True
            }),
            'email_address': forms.EmailInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'partnership_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'service_areas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your current service areas, distribution network, or coverage regions'
            }),
            'referral_source': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'full_name': 'Full Name *',
            'phone_number': 'Phone Number *',
            'email_address': 'Email Address *',
            'partnership_type': 'Partnership Interest *',
            'company_name': 'Company Name',
            'service_areas': 'Service Areas/Distribution Network',
            'referral_source': 'How did you hear about us?',
        }


class ContactForm(forms.ModelForm):
    verification = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I'm not a robot and agree to the terms of service"
    )
    
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'city', 'interest', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control rounded-3',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'type': 'tel'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control rounded-3'
            }),
            'interest': forms.Select(attrs={
                'class': 'form-select rounded-3',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control rounded-3',
                'rows': 5,
                'placeholder': 'Tell us more about your inquiry...',
                'required': True
            }),
        }
        labels = {
            'name': 'Full Name *',
            'email': 'Email Address *',
            'phone': 'Phone Number',
            'city': 'City',
            'interest': "I'm interested in *",
            'message': 'Message *',
        }