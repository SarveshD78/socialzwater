# website/admin.py
from django.contrib import admin
from .models import (
    QRLandingInquiry,
    BusinessHotelInquiry,
    SmartBrandInquiry,
    EarnWithUsInquiry,
    ContactInquiry
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

@admin.register(BusinessHotelInquiry)
class BusinessHotelInquiryAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'contact_person', 'business_email', 'business_type', 'targeted_area', 'created_at']
    list_filter = ['business_type', 'monthly_requirement', 'created_at']
    search_fields = ['business_name', 'contact_person', 'business_email', 'targeted_area']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Business Information', {
            'fields': ('business_name', 'contact_person', 'business_type', 'business_email', 'phone_number')
        }),
        ('Location & Requirements', {
            'fields': ('targeted_area', 'business_address', 'monthly_requirement')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SmartBrandInquiry)
class SmartBrandInquiryAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'contact_person', 'business_email', 'industry_type', 'budget_range', 'created_at']
    list_filter = ['industry_type', 'budget_range', 'video_duration', 'created_at']
    search_fields = ['company_name', 'contact_person', 'business_email', 'targeted_area']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'contact_person', 'business_email', 'phone_number', 'industry_type')
        }),
        ('Campaign Details', {
            'fields': ('targeted_area', 'budget_range', 'video_duration')
        }),
        ('Additional Information', {
            'fields': ('website_url', 'company_description', 'target_audience', 'social_instagram'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EarnWithUsInquiry)
class EarnWithUsInquiryAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email_address', 'partnership_type', 'company_name', 'created_at']
    list_filter = ['partnership_type', 'referral_source', 'created_at']
    search_fields = ['full_name', 'email_address', 'company_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'email_address', 'phone_number')
        }),
        ('Partnership Details', {
            'fields': ('partnership_type', 'company_name', 'service_areas')
        }),
        ('Additional Information', {
            'fields': ('referral_source',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'interest', 'city', 'created_at']
    list_filter = ['interest', 'created_at']
    search_fields = ['name', 'email', 'city']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'city')
        }),
        ('Inquiry Details', {
            'fields': ('interest', 'message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Customize admin site header and title
admin.site.site_header = "Socialz Water Admin"
admin.site.site_title = "Socialz Water Admin Portal"
admin.site.index_title = "Welcome to Socialz Water Administration"