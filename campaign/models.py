# models.py
from django.db import models

class Client(models.Model):
    company_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)
    address = models.TextField()
    industry_type = models.CharField(max_length=100)
    contact_person_name = models.CharField(max_length=100)
    contact_phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

class AdvCampaign(models.Model):
    unique_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    camp_name = models.CharField(max_length=255)
    video = models.FileField(upload_to='campaign_videos/', blank=True, null=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='campaigns')
    start_date = models.DateField()
    end_date = models.DateField()
    number_of_bottles = models.PositiveIntegerField()
    budget_of_rewards = models.DecimalField(max_digits=12, decimal_places=2)
    customized_message = models.TextField()
    # New fields moved from Client
    area_served = models.TextField()
    facebook_link = models.URLField(blank=True, null=True)
    website_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    other_links = models.TextField(blank=True, null=True)
    
    qr_code = models.ImageField(upload_to='campaign_qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.camp_name
    
    class Meta:
        ordering = ['-start_date', '-created_at']
        verbose_name = 'Advertisement Campaign'
        verbose_name_plural = 'Advertisement Campaigns'
    
    @property
    def is_active(self):
        from datetime import date
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1
# Add this to your models.py

from django.db import models
from django.utils import timezone

from django.db import models
from django.utils import timezone
from decimal import Decimal

class ScanTracking(models.Model):
    """Track each QR code scan and engagement with session persistence"""
    campaign = models.ForeignKey(
        'AdvCampaign', 
        on_delete=models.CASCADE, 
        related_name='scans'
    )
    
    # Device & Location Info
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_fingerprint = models.CharField(max_length=64)  # Hash of device info
    device_type = models.CharField(
        max_length=20, 
        choices=[
            ('mobile', 'Mobile'),
            ('tablet', 'Tablet'),
            ('desktop', 'Desktop'),
            ('unknown', 'Unknown'),
        ], 
        default='mobile'  # Default to mobile as 99% users
    )
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    
    # Video Engagement - Track actual duration and progress
    video_duration = models.IntegerField(
        default=0, 
        help_text="Total video duration in seconds"
    )
    video_watched = models.IntegerField(
        default=0, 
        help_text="Seconds watched"
    )
    video_completed = models.BooleanField(default=False)
    video_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00
    )
    
    # User Data (if submitted)
    user_name = models.CharField(max_length=100, blank=True)
    user_phone = models.CharField(max_length=20, blank=True)
    form_submitted = models.BooleanField(default=False)
    
    # Timestamps
    scanned_at = models.DateTimeField(auto_now_add=True)
    form_submitted_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Session tracking
    session_id = models.CharField(
        max_length=64, 
        help_text="Unique session identifier"
    )
    
    # ========== REWARD MANAGEMENT FIELDS ==========
    REWARD_STATUS_CHOICES = [
        ('pending', 'Video Watched - Pending'),
        ('granted', 'Reward Granted'),
        ('invalid', 'Invalid Details'),
        ('duplicate', 'Duplicate Number'),
    ]
    
    reward_status = models.CharField(
        max_length=20,
        choices=REWARD_STATUS_CHOICES,
        default='pending',
        help_text="Current status of reward for this submission"
    )
    
    reward_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount of reward granted"
    )
    
    reward_granted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the reward was granted"
    )
    
    reward_notes = models.TextField(
        blank=True,
        help_text="Notes about reward status or issues"
    )
    
    class Meta:
        ordering = ['-scanned_at']
        indexes = [
            models.Index(fields=['campaign', 'scanned_at']),
            models.Index(fields=['device_fingerprint']),
            models.Index(fields=['session_id']),
            models.Index(fields=['campaign', 'user_phone']),
            models.Index(fields=['campaign', 'form_submitted']),
            models.Index(fields=['campaign', 'reward_status']),  # New index for reward queries
        ]
        # Unique constraint for phone number per campaign
        constraints = [
            models.UniqueConstraint(
                fields=['campaign', 'user_phone'],
                condition=models.Q(form_submitted=True) & ~models.Q(user_phone=''),
                name='unique_phone_per_campaign'
            )
        ]
    
    def __str__(self):
        return f"{self.campaign.camp_name} - {self.scanned_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_unique_device(self):
        """Check if this is first scan from this device"""
        return not ScanTracking.objects.filter(
            campaign=self.campaign,
            device_fingerprint=self.device_fingerprint,
            scanned_at__lt=self.scanned_at
        ).exists()
    
    @property
    def is_returning_user(self):
        """Check if user returned to complete the flow"""
        return self.video_watched > 0 and not self.form_submitted
    
    @property
    def watch_duration_formatted(self):
        """Return formatted watch duration"""
        if self.video_watched == 0:
            return "Not watched"
        minutes = self.video_watched // 60
        seconds = self.video_watched % 60
        return f"{minutes}:{seconds:02d}"
    
    @property
    def total_duration_formatted(self):
        """Return formatted total duration"""
        if self.video_duration == 0:
            return "Unknown"
        minutes = self.video_duration // 60
        seconds = self.video_duration % 60
        return f"{minutes}:{seconds:02d}"
    
    @property
    def engagement_score(self):
        """Calculate engagement score based on actions"""
        score = 0
        if self.video_percentage > 0:
            score += min(self.video_percentage, 100) * 0.5
        if self.video_completed:
            score += 25
        if self.form_submitted:
            score += 25
        return round(score, 2)
    
    @property
    def can_grant_reward(self):
        """Check if reward can be granted"""
        return self.form_submitted and self.reward_status == 'pending'
    
    @property
    def reward_status_color(self):
        """Get Bootstrap color class for status"""
        status_colors = {
            'pending': 'warning',
            'granted': 'success',
            'invalid': 'danger',
            'duplicate': 'secondary'
        }
        return status_colors.get(self.reward_status, 'secondary')
    
    def save(self, *args, **kwargs):
        # Ensure form_submitted_at is set when form is submitted
        if self.form_submitted and not self.form_submitted_at:
            self.form_submitted_at = timezone.now()
            # Set initial reward status
            if not self.reward_status:
                self.reward_status = 'pending'
        
        # Update last activity timestamp
        self.last_activity = timezone.now()
        
        # Calculate percentage if duration is known
        if self.video_duration > 0:
            self.video_percentage = round(
                min((self.video_watched / self.video_duration) * 100, 100), 
                2
            )
        
        super().save(*args, **kwargs)

# models.py

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class Manufacturer(models.Model):
    """Model to store manufacturer details"""
    name = models.CharField(max_length=255, verbose_name="Manufacturer Name")
    contact_person = models.CharField(max_length=150, verbose_name="Contact Person")
    
    # Phone number with validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits allowed."
    )
    contact_number = models.CharField(validators=[phone_regex], max_length=17, verbose_name="Contact Number")
    
    # Address fields
    address = models.TextField(verbose_name="Address")
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default="India")
    
    # Additional fields
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address")
    registration_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Registration No.")
    gst_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="GST Number")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Manufacturer'
        verbose_name_plural = 'Manufacturers'

    def __str__(self):
        return f"{self.name} - {self.contact_person}"

    @property
    def total_orders(self):
        return self.orders.count()

    @property
    def active_orders(self):
        return self.orders.filter(status__in=['pending', 'processing']).count()

    @property
    def completed_orders(self):
        return self.orders.filter(status='completed').count()

    @property
    def total_order_value(self):
        return sum(order.total_amount for order in self.orders.all())


class Order(models.Model):
    """Model to store order details - One-to-Many with Manufacturer"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('delivered', 'Delivered'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Foreign key to manufacturer
    manufacturer = models.ForeignKey(
        Manufacturer, 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name="Manufacturer"
    )
    
    # Order details
    order_number = models.CharField(max_length=50, unique=True, verbose_name="Order Number")
    order_date = models.DateField(default=timezone.now, verbose_name="Order Date")
    expected_delivery = models.DateField(verbose_name="Expected Delivery Date")
    actual_delivery = models.DateField(blank=True, null=True, verbose_name="Actual Delivery Date")
    
    # Order specifications
    product_name = models.CharField(max_length=255, verbose_name="Product Name")
    product_description = models.TextField(blank=True, null=True, verbose_name="Product Description")
    quantity = models.PositiveIntegerField(verbose_name="Quantity")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Unit Price")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total Amount")
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Additional details
    notes = models.TextField(blank=True, null=True, verbose_name="Order Notes")
    terms_conditions = models.TextField(blank=True, null=True, verbose_name="Terms & Conditions")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date', '-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.order_number} - {self.manufacturer.name}"

    def save(self, *args, **kwargs):
        # Auto-calculate total amount
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        from datetime import date
        return self.expected_delivery < date.today() and self.status not in ['completed', 'delivered', 'cancelled']

    @property
    def days_until_delivery(self):
        from datetime import date
        return (self.expected_delivery - date.today()).days

    @property
    def status_display(self):
        return self.get_status_display()

    @property
    def priority_display(self):
        return self.get_priority_display()


class Supplier(models.Model):
    """Model to store supplier details - Hotels, Events, Distributors"""
    
    SUPPLIER_TYPES = [
        ('hotel', 'Hotel'),
        ('event', 'Event Company'),
        ('distributor', 'Distributor'),
        ('restaurant', 'Restaurant'),
        ('catering', 'Catering Service'),
        ('retailer', 'Retailer'),
        ('other', 'Other'),
    ]

    # Basic details
    name = models.CharField(max_length=255, verbose_name="Supplier Name")
    supplier_type = models.CharField(max_length=20, choices=SUPPLIER_TYPES, verbose_name="Supplier Type")
    contact_person = models.CharField(max_length=150, verbose_name="Contact Person")
    
    # Contact details
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits allowed."
    )
    contact_number = models.CharField(validators=[phone_regex], max_length=17, verbose_name="Contact Number")
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address")
    
    # Address
    address = models.TextField(verbose_name="Address")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="India")
    
    # Business details
    business_license = models.CharField(max_length=100, blank=True, null=True, verbose_name="Business License")
    gst_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="GST Number")
    
    # Rating and status
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name="Rating (out of 5)")
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['supplier_type', 'name']
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return f"{self.name} ({self.get_supplier_type_display()})"

    @property
    def total_supplies(self):
        return self.supplies.count()

    @property
    def active_supplies(self):
        return self.supplies.filter(status__in=['pending', 'processing']).count()

    @property
    def completed_supplies(self):
        return self.supplies.filter(status='delivered').count()

    @property
    def total_supply_value(self):
        return sum(supply.total_amount for supply in self.supplies.all())


class Supply(models.Model):
    """Model to track supply deliveries - Many-to-Many with Orders through this model"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    # Relationships
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.CASCADE, 
        related_name='supplies',
        verbose_name="Supplier"
    )
    orders = models.ManyToManyField(
        Order, 
        related_name='supplies',
        verbose_name="Related Orders",
        blank=True
    )
    
    # Supply details
    supply_number = models.CharField(max_length=50, unique=True, verbose_name="Supply Number")
    supply_date = models.DateField(default=timezone.now, verbose_name="Supply Date")
    expected_delivery = models.DateField(verbose_name="Expected Delivery Date")
    actual_delivery = models.DateField(blank=True, null=True, verbose_name="Actual Delivery Date")
    
    # Product details
    product_name = models.CharField(max_length=255, verbose_name="Product Name")
    quantity_supplied = models.PositiveIntegerField(verbose_name="Quantity Supplied")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Unit Price")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total Amount")
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tracking Number")
    delivery_notes = models.TextField(blank=True, null=True, verbose_name="Delivery Notes")
    
    # Quality and feedback
    quality_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Quality Rating (out of 5)"
    )
    feedback = models.TextField(blank=True, null=True, verbose_name="Feedback")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-supply_date', '-created_at']
        verbose_name = 'Supply'
        verbose_name_plural = 'Supplies'

    def __str__(self):
        return f"Supply #{self.supply_number} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        # Auto-calculate total amount
        self.total_amount = self.quantity_supplied * self.unit_price
        super().save(*args, **kwargs)

    @property
    def is_delivered(self):
        return self.status == 'delivered'

    @property
    def is_overdue(self):
        from datetime import date
        return (
            self.expected_delivery < date.today() and 
            self.status not in ['delivered', 'cancelled']
        )

    @property
    def delivery_delay_days(self):
        if self.actual_delivery and self.expected_delivery:
            return (self.actual_delivery - self.expected_delivery).days
        return None

    @property
    def status_display(self):
        return self.get_status_display()

    @property
    def related_orders_count(self):
        return self.orders.count()
