# website/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from .models import (
    PartnerInquiry,
    QRLandingInquiry, 
)
from .forms import (
    QRLandingForm,
)
INQUIRY_MODELS = {
    'qr_landing': QRLandingInquiry,

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



def contact(request):
    """Contact page view"""
    context = {
        'title': 'Contact Us - Socialz Water',
    }
    return render(request, 'website/contact.html', context)


# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PartnerInquiry

def partner(request):
    """Partner page view with form handling"""
    print("=" * 50)
    print(f"Request Method: {request.method}")
    print("=" * 50)
    
    if request.method == 'POST':
        print("POST request received!")
        print(f"POST data: {request.POST}")
        
        # Get form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        partner_type = request.POST.get('partner_type')
        message = request.POST.get('message', '')
        
        # Debug print all form values
        print("-" * 50)
        print(f"Full Name: {full_name}")
        print(f"Email: {email}")
        print(f"Phone: {phone}")
        print(f"Partner Type: {partner_type}")
        print(f"Message: {message}")
        print("-" * 50)
        
        # Check if required fields are present
        if not full_name:
            print("ERROR: full_name is missing!")
        if not email:
            print("ERROR: email is missing!")
        if not phone:
            print("ERROR: phone is missing!")
        if not partner_type:
            print("ERROR: partner_type is missing!")
        
        # Save to database
        try:
            print("Attempting to save to database...")
            partner_inquiry = PartnerInquiry.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                partner_type=partner_type,
                message=message
            )
            print(f"SUCCESS! Saved inquiry with ID: {partner_inquiry.id}")
            print(f"Saved object: {partner_inquiry}")
            
            # Success message
            messages.success(request, 'Thank you for your interest! We will contact you within 24 hours.')
            print("Success message added")
            
            print("Redirecting to partner page...")
            return redirect('website:partner')  # Redirect to same page to clear form
            
        except Exception as e:
            print(f"ERROR while saving: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            import traceback
            print(f"Full traceback:\n{traceback.format_exc()}")
            
            messages.error(request, 'An error occurred. Please try again.')
    else:
        print("GET request - displaying form")
    
    # GET request or after POST processing
    context = {
        'title': 'Partner With Us - Socialz Water',
    }
    print("Rendering template...")
    return render(request, 'website/partner.html', context)

def faqs(request):
    """Home page view"""
    context = {
        'title': 'Home - Socialz Water',
    }
    return render(request, 'website/faqs.html', context)