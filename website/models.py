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


from django.db import models
from django.utils import timezone

class PartnerInquiry(models.Model):
    PARTNER_TYPE_CHOICES = [
        ('brand', 'Partner as Brand'),
        ('manufacturer', 'Manufacturer'),
        ('distributor', 'Distributor'),
        ('event', 'Event Organizer'),
    ]
    
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    partner_type = models.CharField(max_length=50, choices=PARTNER_TYPE_CHOICES)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Partner Inquiry"
        verbose_name_plural = "Partner Inquiries"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.get_partner_type_display()} ({self.created_at.strftime('%Y-%m-%d')})"