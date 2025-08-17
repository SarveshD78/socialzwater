# website/models.py
from django.db import models
from django.utils import timezone

class QRLandingInquiry(models.Model):
    # Required fields
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email_address = models.EmailField()
    
    # Optional fields
    how_found_us = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('qr_scan', 'QR Code Scan'),
        ('social_media', 'Social Media'),
        ('friend', 'Friend Referral'),
        ('other', 'Other'),
    ])
    
    # Meta fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'qr_landing_inquiries'
        verbose_name = 'QR Landing Inquiry'
        verbose_name_plural = 'QR Landing Inquiries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.email_address}"


class BusinessHotelInquiry(models.Model):
    # Required fields
    business_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    business_email = models.EmailField()
    targeted_area = models.CharField(max_length=200)
    business_type = models.CharField(max_length=50, choices=[
        ('hotel', 'Hotel'),
        ('restaurant', 'Restaurant'),
        ('event_venue', 'Event Venue'),
        ('cafe', 'Cafe/Coffee Shop'),
        ('resort', 'Resort'),
        ('conference_center', 'Conference Center'),
        ('other', 'Other'),
    ])
    
    # Optional fields
    business_address = models.TextField(blank=True, null=True)
    monthly_requirement = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('1000-5000', '1,000 - 5,000 bottles'),
        ('5000-10000', '5,000 - 10,000 bottles'),
        ('10000-25000', '10,000 - 25,000 bottles'),
        ('25000+', '25,000+ bottles'),
    ])
    
    # Meta fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'business_hotel_inquiries'
        verbose_name = 'Business Hotel Inquiry'
        verbose_name_plural = 'Business Hotel Inquiries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business_name} - {self.contact_person}"


class SmartBrandInquiry(models.Model):
    # Required fields
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    business_email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    industry_type = models.CharField(max_length=50, choices=[
        ('technology', 'Technology'),
        ('food_beverage', 'Food & Beverage'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('retail', 'Retail'),
        ('automotive', 'Automotive'),
        ('finance', 'Finance'),
        ('fashion', 'Fashion & Lifestyle'),
        ('travel', 'Travel & Tourism'),
        ('other', 'Other'),
    ])
    targeted_area = models.CharField(max_length=200)
    budget_range = models.CharField(max_length=50, choices=[
        ('50000-100000', '₹50,000 - ₹1,00,000'),
        ('100000-250000', '₹1,00,000 - ₹2,50,000'),
        ('250000-500000', '₹2,50,000 - ₹5,00,000'),
        ('500000-1000000', '₹5,00,000 - ₹10,00,000'),
        ('1000000+', '₹10,00,000+'),
    ])
    
    # Optional fields
    website_url = models.URLField(blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)
    target_audience = models.TextField(blank=True, null=True)
    social_instagram = models.CharField(max_length=100, blank=True, null=True)
    video_duration = models.CharField(max_length=10, blank=True, null=True, choices=[
        ('20', '20 seconds'),
        ('30', '30 seconds'),
    ])
    
    # Meta fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'smart_brand_inquiries'
        verbose_name = 'Smart Brand Inquiry'
        verbose_name_plural = 'Smart Brand Inquiries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company_name} - {self.contact_person}"


class EarnWithUsInquiry(models.Model):
    # Required fields
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email_address = models.EmailField()
    partnership_type = models.CharField(max_length=50, choices=[
        ('manufacturer', 'Manufacturer'),
        ('dealer', 'Dealer/Distributor'),
        ('retailer', 'Retailer'),
        ('wholesale', 'Wholesale Partner'),
        ('regional', 'Regional Partner'),
        ('other', 'Other'),
    ])
    
    # Optional fields
    company_name = models.CharField(max_length=200, blank=True, null=True)
    service_areas = models.TextField(blank=True, null=True)
    referral_source = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('website', 'Website'),
        ('social_media', 'Social Media'),
        ('referral', 'Friend/Business Referral'),
        ('advertisement', 'Advertisement'),
        ('event', 'Event/Exhibition'),
        ('other', 'Other'),
    ])
    
    # Meta fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'earn_with_us_inquiries'
        verbose_name = 'Earn With Us Inquiry'
        verbose_name_plural = 'Earn With Us Inquiries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.partnership_type}"


class ContactInquiry(models.Model):
    # Required fields
    name = models.CharField(max_length=100)
    email = models.EmailField()
    interest = models.CharField(max_length=50, choices=[
        ('water-lover', 'For Water Lovers - Earning Rewards'),
        ('smart-brand', 'For Smart Brands - Advertising'),
        ('growth-partner', 'For Growth Partners - Partnership'),
        ('general', 'General Inquiry'),
        ('support', 'Technical Support'),
    ])
    message = models.TextField()
    
    # Optional fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    # Meta fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contact_inquiries'
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_interest_display()}"