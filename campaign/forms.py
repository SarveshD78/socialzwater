from django import forms
from .models import Client, AdvCampaign

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'company_name', 'email', 'address', 'industry_type',
            'contact_person_name', 'contact_phone_number'
        ]
        
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'industry_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Technology, Healthcare'}),
            'contact_person_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact person name'}),
            'contact_phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
        }

class AdvCampaignForm(forms.ModelForm):
    class Meta:
        model = AdvCampaign
        fields = [
            'camp_name', 'video', 'client', 'start_date', 'end_date',
            'number_of_bottles', 'budget_of_rewards', 'customized_message',
            'area_served', 'facebook_link', 'website_link', 'instagram_link', 'other_links'
        ]
        
        widgets = {
            'camp_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campaign name'}),
            'video': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'number_of_bottles': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'budget_of_rewards': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'customized_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter campaign message'}),
            'area_served': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Areas served'}),
            'facebook_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://facebook.com/...'}),
            'website_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/...'}),
            'other_links': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Other social media links'}),
        }
        
        labels = {
            'camp_name': 'Campaign Name',
            'budget_of_rewards': 'Rewards Budget (₹)',
            'number_of_bottles': 'Number of Bottles',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError('End date must be after start date.')
        
        return cleaned_data