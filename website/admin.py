# website/admin.py
from django.contrib import admin
from .models import (
    PartnerInquiry,
    QRLandingInquiry,
)

@admin.register(QRLandingInquiry)
class QRLandingInquiryAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email_address', 'phone_number', 'how_found_us', 'created_at']
    list_filter = ['how_found_us', 'created_at']
    search_fields = ['full_name', 'email_address', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email_address', 'phone_number')
        }),
        ('Additional Information', {
            'fields': ('how_found_us',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PartnerInquiry)
class PartnerInquiryAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'partner_type', 'created_at']
    list_filter = ['partner_type', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    ordering = ['-created_at']