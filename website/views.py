# website/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from .models import (
    QRLandingInquiry, 
    BusinessHotelInquiry, 
    SmartBrandInquiry, 
    EarnWithUsInquiry, 
    ContactInquiry
)
from .forms import (
    QRLandingForm,
    BusinessHotelForm,
    SmartBrandForm,
    EarnWithUsForm,
    ContactForm
)
INQUIRY_MODELS = {
    'qr_landing': QRLandingInquiry,
    'business_hotel': BusinessHotelInquiry,
    'smart_brand': SmartBrandInquiry,
    'earn_with_us': EarnWithUsInquiry,
    'contact': ContactInquiry,
}

def home(request):
    """Home page view"""
    context = {
        'title': 'Home - Socialz Water',
    }
    return render(request, 'website/home.html', context)

def about(request):
    """About page view"""
    context = {
        'title': 'About Us - Socialz Water',
    }
    return render(request, 'website/about.html', context)

def qr_landing(request):
    """QR Code Landing page view with form submission"""
    if request.method == 'POST':
        form = QRLandingForm(request.POST)
        if form.is_valid():
            try:
                # Save inquiry
                inquiry = form.save()
                
                # Send notification email (optional)
                try:
                    send_mail(
                        subject='New QR Landing Registration',
                        message=f'New registration from {inquiry.full_name} ({inquiry.email_address})',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=['info@socialzwater.com'],
                        fail_silently=True,
                    )
                except:
                    pass  # Email sending is optional
                
                messages.success(request, 'Thank you! We will notify you as soon as we launch.')
                return redirect('website:qr_landing')
                
            except Exception as e:
                messages.error(request, 'Something went wrong. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields correctly.')
    else:
        form = QRLandingForm()
    
    context = {
        'title': 'Welcome to Socialz Water - Coming Soon',
        'form': form,
    }
    return render(request, 'website/qr_landing.html', context)

def business_hotels(request):
    """For Business Hotels & Events page view"""
    if request.method == 'POST':
        form = BusinessHotelForm(request.POST)
        if form.is_valid():
            try:
                # Save inquiry (excluding agree_terms as it's not in model)
                inquiry_data = form.cleaned_data.copy()
                inquiry_data.pop('agree_terms', None)  # Remove agree_terms as it's not in model
                inquiry = BusinessHotelInquiry.objects.create(**inquiry_data)
                
                # Send notification email
                try:
                    send_mail(
                        subject='New Business Partnership Inquiry',
                        message=f'New business inquiry from {inquiry.business_name}\nContact: {inquiry.contact_person}\nEmail: {inquiry.business_email}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=['partners@socialzwater.com'],
                        fail_silently=True,
                    )
                except:
                    pass
                
                messages.success(request, 'Thank you! We will contact you within 24 hours with your custom quote.')
                return redirect('website:business_hotels')
                
            except Exception as e:
                messages.error(request, 'Something went wrong. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields correctly.')
    else:
        form = BusinessHotelForm()
    
    context = {
        'title': 'For Business Hotels & Events - Socialz Water',
        'form': form,
    }
    return render(request, 'website/business_hotels.html', context)

def smart_brands(request):
    """For Smart Brands page view"""
    if request.method == 'POST':
        form = SmartBrandForm(request.POST)
        if form.is_valid():
            try:
                # Save inquiry (excluding agree_terms as it's not in model)
                inquiry_data = form.cleaned_data.copy()
                inquiry_data.pop('agree_terms', None)  # Remove agree_terms as it's not in model
                inquiry = SmartBrandInquiry.objects.create(**inquiry_data)
                
                # Send notification email
                try:
                    send_mail(
                        subject='New Brand Advertising Inquiry',
                        message=f'New advertising inquiry from {inquiry.company_name}\nContact: {inquiry.contact_person}\nBudget: {inquiry.budget_range}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=['partners@socialzwater.com'],
                        fail_silently=True,
                    )
                except:
                    pass
                
                messages.success(request, 'Thank you! We will create a custom campaign proposal for you within 24 hours.')
                return redirect('website:smart_brands')
                
            except Exception as e:
                messages.error(request, 'Something went wrong. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields correctly.')
    else:
        form = SmartBrandForm()
    
    context = {
        'title': 'For Smart Brands - Socialz Water',
        'form': form,
    }
    return render(request, 'website/smart_brands.html', context)

def earn_with_us(request):
    """Earn with Us page view"""
    if request.method == 'POST':
        form = EarnWithUsForm(request.POST)
        if form.is_valid():
            try:
                # Save inquiry (excluding agree_terms and agree_contact as they're not in model)
                inquiry_data = form.cleaned_data.copy()
                inquiry_data.pop('agree_terms', None)
                inquiry_data.pop('agree_contact', None)
                inquiry = EarnWithUsInquiry.objects.create(**inquiry_data)
                
                # Send notification email
                try:
                    send_mail(
                        subject='New Partnership Application',
                        message=f'New partnership application from {inquiry.full_name}\nType: {inquiry.partnership_type}\nEmail: {inquiry.email_address}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=['partners@socialzwater.com'],
                        fail_silently=True,
                    )
                except:
                    pass
                
                messages.success(request, 'Thank you! We will review your partnership application within 24-48 hours.')
                return redirect('website:earn_with_us')
                
            except Exception as e:
                messages.error(request, 'Something went wrong. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields correctly.')
    else:
        form = EarnWithUsForm()
    
    context = {
        'title': 'Earn with Us - Socialz Water',
        'form': form,
    }
    return render(request, 'website/earn_with_us.html', context)

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Save inquiry (excluding verification as it's not in model)
                inquiry_data = form.cleaned_data.copy()
                inquiry_data.pop('verification', None)  # Remove verification as it's not in model
                inquiry = ContactInquiry.objects.create(**inquiry_data)
                
                # Send notification email
                try:
                    send_mail(
                        subject='New Contact Form Submission',
                        message=f'New contact from {inquiry.name}\nInterest: {inquiry.get_interest_display()}\nMessage: {inquiry.message}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=['info@socialzwater.com'],
                        fail_silently=True,
                    )
                except:
                    pass
                
                messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
                return redirect('website:contact')
                
            except Exception as e:
                messages.error(request, 'Something went wrong. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields correctly.')
    else:
        form = ContactForm()
    
    context = {
        'title': 'Contact Us - Socialz Water',
        'form': form,
    }
    return render(request, 'website/contact.html', context)


# website/dashboard_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (
    QRLandingInquiry,
    BusinessHotelInquiry,
    SmartBrandInquiry,
    EarnWithUsInquiry,
    ContactInquiry
)

INQUIRY_MODELS = {
    'qr_landing': QRLandingInquiry,
    'business_hotel': BusinessHotelInquiry,
    'smart_brand': SmartBrandInquiry,
    'earn_with_us': EarnWithUsInquiry,
    'contact': ContactInquiry,
}

@login_required
@staff_member_required
def dashboard(request):
    """Simple dashboard with inquiry selection and table"""
    
    # Get selected inquiry type from dropdown
    selected_type = request.GET.get('type', 'qr_landing')
    
    if selected_type not in INQUIRY_MODELS:
        selected_type = 'qr_landing'
    
    model = INQUIRY_MODELS[selected_type]
    inquiries = model.objects.all().order_by('-created_at')
    
    # Handle delete action
    if request.method == 'POST':
        inquiry_id = request.POST.get('inquiry_id')
        if inquiry_id:
            try:
                inquiry = model.objects.get(id=inquiry_id)
                inquiry.delete()
                messages.success(request, 'Inquiry deleted successfully.')
            except:
                messages.error(request, 'Error deleting inquiry.')
        return redirect('website:dashboard')
    
    context = {
        'inquiries': inquiries,
        'selected_type': selected_type,
        'inquiry_types': {
            'qr_landing': 'QR Landing',
            'business_hotel': 'Business Hotels',
            'smart_brand': 'Smart Brands',
            'earn_with_us': 'Earn With Us',
            'contact': 'Contact',
        }
    }
    return render(request, 'website/dashboard.html', context)


# Add to website/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def custom_login(request):
    """Custom login view"""
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('website:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff:  # Only allow staff users
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                    return redirect('website:dashboard')
                else:
                    messages.error(request, 'Access denied. Admin privileges required.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    context = {
        'title': 'Admin Login - Socialz Water'
    }
    return render(request, 'website/login.html', context)

def custom_logout(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('website:custom_login')