# views.py - Updated Structure
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum, Case, When, F, FloatField
from django.db.models.functions import TruncDate
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json
import random
import string
import hashlib
import csv
from io import BytesIO

from .models import Client, AdvCampaign, ScanTracking
from .forms import ClientForm, AdvCampaignForm

# Try to import qrcode
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    print("Warning: qrcode module not found. Install with: pip install qrcode Pillow")

# ============== HELPER FUNCTIONS ==============
def generate_custom_uuid(client_name, campaign_name):
    """Generate custom UUID: ClientInitials_CampaignInitials_5RandomNumbers"""
    client_words = client_name.strip().split()
    client_initials = ''.join([word[0].upper() for word in client_words if word])[:3]
    
    campaign_words = campaign_name.strip().split()
    campaign_initials = ''.join([word[0].upper() for word in campaign_words if word])[:3]
    
    random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    custom_uuid = f"{client_initials}_{campaign_initials}_{random_numbers}"
    
    return custom_uuid

# ============== AUTHENTICATION ==============
def custom_login(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('sw:overview')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                    return redirect('sw:overview')
                else:
                    messages.error(request, 'Access denied. Admin privileges required.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'campaign/login.html', {'title': 'Login - Socialz Water'})

def custom_logout(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')
# ============== FIXED OVERVIEW ==============
@login_required
def overview(request):
    """Dashboard overview - Professional and optimized"""
    from django.db.models import Count, Q, Sum, Avg
    from datetime import datetime, timedelta
    
    # Basic counts using aggregation for efficiency
    total_clients = Client.objects.count()
    total_campaigns = AdvCampaign.objects.count()
    total_manufacturers = Manufacturer.objects.filter(is_active=True).count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    
    # Order statistics
    order_stats = Order.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        processing=Count('id', filter=Q(status='processing')),
        completed=Count('id', filter=Q(status='completed'))
    )
    total_orders = order_stats['total']
    
    # Supply statistics
    supply_stats = Supply.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        delivered=Count('id', filter=Q(status='delivered'))
    )
    total_supplies = supply_stats['total']
    
    # Campaign engagement statistics
    scan_stats = ScanTracking.objects.aggregate(
        total_scans=Count('id'),
        total_submissions=Count('id', filter=Q(form_submitted=True))
    )
    
    # Today's statistics
    today = timezone.now().date()
    today_stats = ScanTracking.objects.filter(scanned_at__date=today).aggregate(
        scans_today=Count('id'),
        submissions_today=Count('id', filter=Q(form_submitted=True))
    )
    
    # Calculate conversion rate
    conversion_rate = 0
    if scan_stats['total_scans'] > 0:
        conversion_rate = (scan_stats['total_submissions'] / scan_stats['total_scans']) * 100
    
    # ============== RECENT DATA (5 items each) ==============
    
    # Recent Clients with campaign count
    recent_clients = Client.objects.annotate(
        campaign_count=Count('campaigns')
    ).order_by('-created_at')[:5]
    
    # Recent Campaigns with scan metrics
    recent_campaigns = AdvCampaign.objects.select_related('client').annotate(
        scan_count=Count('scans'),
        submission_count=Count('scans', filter=Q(scans__form_submitted=True))
    ).order_by('-created_at')[:5]
    
    # Recent Manufacturers with order count
    recent_manufacturers = Manufacturer.objects.filter(is_active=True).annotate(
        order_count=Count('orders'),
        pending_orders=Count('orders', filter=Q(orders__status='pending'))
    ).order_by('-created_at')[:5]
    
    # Recent Orders with manufacturer info
    recent_orders = Order.objects.select_related('manufacturer').order_by('-order_date')[:5]
    
    # Reward statistics
    reward_stats = ScanTracking.objects.filter(form_submitted=True).aggregate(
        total_pending=Count('id', filter=Q(reward_status='pending')),
        total_granted=Count('id', filter=Q(reward_status='granted')),
        total_reward_amount=Sum('reward_amount', filter=Q(reward_status='granted'))
    )
    
    context = {
        # Page metadata
        'title': 'Dashboard Overview',
        'page': 'overview',
        'current_date': today.strftime('%B %d, %Y'),
        
        # Main statistics (6 cards)
        'total_clients': total_clients,
        'total_campaigns': total_campaigns,
        'total_manufacturers': total_manufacturers,
        'total_orders': total_orders,
        'total_suppliers': total_suppliers,
        'total_supplies': total_supplies,
        
        # Engagement metrics
        'total_scans': scan_stats['total_scans'],
        'total_submissions': scan_stats['total_submissions'],
        'scans_today': today_stats['scans_today'],
        'submissions_today': today_stats['submissions_today'],
        'conversion_rate': round(conversion_rate, 2),
        
        # Recent activity (4 tables)
        'recent_clients': recent_clients,
        'recent_campaigns': recent_campaigns,
        'recent_manufacturers': recent_manufacturers,
        'recent_orders': recent_orders,
        
        # Rewards
        'pending_rewards': reward_stats['total_pending'] or 0,
        'granted_rewards': reward_stats['total_granted'] or 0,
        'total_reward_amount': reward_stats['total_reward_amount'] or 0,
        
        # User info
        'user': request.user,
    }
    
    return render(request, 'campaign/overview.html', context)
# ============== 2. CLIENTS ==============
@login_required
def client_list(request):
    """Single view handling all client CRUD operations"""
    
    # Handle POST requests (Create/Update)
    if request.method == 'POST':
        action = request.POST.get('action')
        client_id = request.POST.get('client_id')
        
        if action == 'create':
            form = ClientForm(request.POST)
            if form.is_valid():
                client = form.save()
                messages.success(request, f'Client "{client.company_name}" created successfully!')
                return redirect('sw:client_list')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        
        elif action == 'update' and client_id:
            client = get_object_or_404(Client, pk=client_id)
            form = ClientForm(request.POST, instance=client)
            if form.is_valid():
                client = form.save()
                messages.success(request, f'Client "{client.company_name}" updated successfully!')
                return redirect('sw:client_list')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        
        elif action == 'delete' and client_id:
            client = get_object_or_404(Client, pk=client_id)
            client_name = client.company_name
            client.delete()
            messages.success(request, f'Client "{client_name}" deleted successfully!')
            return redirect('sw:client_list')
    
    # Handle GET requests (List/Search)
    clients = Client.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        clients = clients.filter(
            Q(company_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(contact_person_name__icontains=search_query) |
            Q(industry_type__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(clients, 12)  # 12 cards per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Client Management',
        'page': 'client',
        'clients': page_obj,
        'search_query': search_query,
        'create_form': ClientForm(),
    }
    
    return render(request, 'campaign/clients.html', context)

# ============== 3. CAMPAIGNS ==============
@login_required
def campaign_list(request):
    """Single view handling all campaign management"""
    
    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        campaign_id = request.POST.get('campaign_id')
        
        if action == 'create':
            form = AdvCampaignForm(request.POST, request.FILES)
            if form.is_valid():
                campaign = form.save(commit=False)
                
                # Generate custom UUID
                if not campaign.unique_id:
                    custom_uuid = generate_custom_uuid(
                        campaign.client.company_name,
                        campaign.camp_name
                    )
                    while AdvCampaign.objects.filter(unique_id=custom_uuid).exists():
                        custom_uuid = generate_custom_uuid(
                            campaign.client.company_name,
                            campaign.camp_name
                        )
                    campaign.unique_id = custom_uuid
                
                # Generate QR code with logo image in center
                if HAS_QRCODE:
                    from PIL import Image, ImageDraw
                    import os
                    from django.conf import settings
                    
                    domain = getattr(settings, 'SITE_DOMAIN', 'https://socialzwater.in')
                    qr_url = f"{domain}/sw/adv/{campaign.unique_id}/"
                    
                    # Create larger QR code for better quality
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_H,
                        box_size=20,  # Increased for higher resolution
                        border=4,
                    )
                    qr.add_data(qr_url)
                    qr.make(fit=True)
                    
                    # Create QR image
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_img = qr_img.convert("RGB")
                    
                    # Load and add logo image
                    logo_path = os.path.join(settings.BASE_DIR, 'campaign', 'static', 'images', 'SocialZWaterLogo.png')
                    
                    try:
                        logo = Image.open(logo_path)
                        
                        # Calculate logo size (1/4 of QR code for better visibility)
                        qr_width, qr_height = qr_img.size
                        logo_max_size = qr_width // 4
                        
                        # Calculate scaling to maintain aspect ratio
                        logo_width, logo_height = logo.size
                        aspect_ratio = logo_width / logo_height
                        
                        # Resize logo while maintaining aspect ratio
                        if logo_width > logo_height:
                            new_width = min(logo_width, logo_max_size)
                            new_height = int(new_width / aspect_ratio)
                        else:
                            new_height = min(logo_height, logo_max_size)
                            new_width = int(new_height * aspect_ratio)
                        
                        # Resize logo with high quality
                        if logo_width != new_width or logo_height != new_height:
                            logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Create a white background rectangle slightly larger than logo
                        padding = 10
                        bg_width = new_width + padding * 2
                        bg_height = new_height + padding * 2
                        
                        # Create white background
                        background = Image.new('RGB', (bg_width, bg_height), (255, 255, 255))
                        
                        # Paste logo on white background
                        logo_x = padding
                        logo_y = padding
                        
                        # Paste logo preserving transparency if it has alpha channel
                        if logo.mode == 'RGBA':
                            background.paste(logo, (logo_x, logo_y), logo)
                        else:
                            background.paste(logo, (logo_x, logo_y))
                        
                        # Calculate position to center on QR code
                        pos_x = (qr_width - bg_width) // 2
                        pos_y = (qr_height - bg_height) // 2
                        
                        # Paste onto QR code
                        qr_img.paste(background, (pos_x, pos_y))
                        
                        # Optionally: Apply sharpening filter for crisper image
                        from PIL import ImageEnhance
                        enhancer = ImageEnhance.Sharpness(qr_img)
                        qr_img = enhancer.enhance(1.2)  # Slight sharpening
                        
                    except Exception as e:
                        print(f"Could not add logo to QR code: {e}")
                        # QR code will still work without logo
                    
                    # Save QR code with high quality
                    buffer = BytesIO()
                    qr_img.save(buffer, format='PNG', optimize=True, quality=100)
                    
                    file_name = f'qr_{campaign.unique_id}.png'
                    campaign.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
                
                campaign.save()
                messages.success(request, f'Campaign "{campaign.camp_name}" created successfully!')
                return redirect('sw:campaign_list')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        
        elif action == 'update' and campaign_id:
            campaign = get_object_or_404(AdvCampaign, pk=campaign_id)
            form = AdvCampaignForm(request.POST, request.FILES, instance=campaign)
            if form.is_valid():
                campaign = form.save()
                messages.success(request, f'Campaign "{campaign.camp_name}" updated successfully!')
                return redirect('sw:campaign_list')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        
        elif action == 'delete' and campaign_id:
            campaign = get_object_or_404(AdvCampaign, pk=campaign_id)
            campaign_name = campaign.camp_name
            campaign.delete()
            messages.success(request, f'Campaign "{campaign_name}" deleted successfully!')
            return redirect('sw:campaign_list')
    
    # Handle GET requests
    campaigns = AdvCampaign.objects.all().select_related('client').order_by('-start_date')
    
    # Search and filter
    search_query = request.GET.get('search', '')
    client_id = request.GET.get('client')
    
    if search_query:
        campaigns = campaigns.filter(
            Q(camp_name__icontains=search_query) |
            Q(client__company_name__icontains=search_query) |
            Q(customized_message__icontains=search_query)
        )
    
    if client_id:
        campaigns = campaigns.filter(client_id=client_id)
    
    # Pagination
    paginator = Paginator(campaigns, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get clients for filter
    clients = Client.objects.all().order_by('company_name')
    
    context = {
        'title': 'Campaign Management',
        'page': 'campaign',
        'campaigns': page_obj,
        'search_query': search_query,
        'clients': clients,
        'selected_client': client_id,
        'create_form': AdvCampaignForm(),
    }
    
    return render(request, 'campaign/campaigns.html', context)
# ============== 4. REPORTS ==============
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

@login_required
def report_list(request):
    """Reports dashboard - All campaigns overview"""
    
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Get all campaigns with metrics
    campaigns = AdvCampaign.objects.all()
    
    # Apply search filter
    if search_query:
        campaigns = campaigns.filter(
            Q(camp_name__icontains=search_query) |
            Q(client__company_name__icontains=search_query) |
            Q(area_served__icontains=search_query)
        )
    
    # Annotate campaigns with metrics
    campaigns = campaigns.annotate(
        total_scans=Count('scans'),
        total_submissions=Count('scans', filter=Q(scans__form_submitted=True)),
        total_completions=Count('scans', filter=Q(scans__video_completed=True)),
        avg_watch_time=Avg('scans__video_watched'),
        unique_devices=Count('scans__device_fingerprint', distinct=True)
    ).select_related('client').order_by('-created_at')
    
    # Calculate conversion rates for each campaign
    campaign_list = []
    for campaign in campaigns:
        total_scans = campaign.total_scans or 0
        form_conversion = 0
        video_completion = 0
        
        if total_scans > 0:
            form_conversion = round((campaign.total_submissions / total_scans) * 100, 2)
            video_completion = round((campaign.total_completions / total_scans) * 100, 2)
        
        campaign_list.append({
            'campaign': campaign,
            'total_scans': total_scans,
            'form_submissions': campaign.total_submissions,
            'video_completions': campaign.total_completions,
            'form_conversion_rate': form_conversion,
            'video_completion_rate': video_completion,
            'avg_watch_time': round(campaign.avg_watch_time or 0, 1),
            'unique_devices': campaign.unique_devices
        })
    
    # Pagination
    paginator = Paginator(campaign_list, 10)
    page_number = request.GET.get('page')
    reports_page = paginator.get_page(page_number)
    
    context = {
        'reports': reports_page,
        'search_query': search_query,
        'total_campaigns': len(campaign_list),  # Just the count for display
    }
    
    return render(request, 'campaign/reports_list.html', context)

@login_required
def report_detail(request, unique_id):
    """
    Comprehensive individual campaign report with detailed analytics
    Merged functionality from campaign_analytics for complete reporting
    """
    
    try:
        campaign = get_object_or_404(AdvCampaign, unique_id=unique_id)
    except AdvCampaign.DoesNotExist:
        messages.error(request, 'Campaign not found')
        return redirect('sw:report_list')
    
    # Get all scans for this campaign
    all_scans = ScanTracking.objects.filter(campaign=campaign)
    
    # ============== BASIC METRICS ==============
    total_scans = all_scans.count()
    unique_devices = all_scans.values('device_fingerprint').distinct().count()
    form_submissions = all_scans.filter(form_submitted=True).count()
    video_completions = all_scans.filter(video_completed=True).count()
    
    # Conversion Rates
    form_conversion_rate = (form_submissions / total_scans * 100) if total_scans else 0
    video_completion_rate = (video_completions / total_scans * 100) if total_scans else 0
    
    # Average Metrics
    avg_watch_time = all_scans.exclude(
        video_watched=0
    ).aggregate(avg=Avg('video_watched'))['avg'] or 0
    
    avg_video_percentage = all_scans.exclude(
        video_percentage=0
    ).aggregate(avg=Avg('video_percentage'))['avg'] or 0
    
    # ============== DEVICE & PLATFORM STATISTICS ==============
    device_stats = list(
        all_scans.values('device_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    browser_stats = list(
        all_scans.values('browser')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]  # Top 5 browsers
    )
    
    os_stats = list(
        all_scans.values('os')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]  # Top 5 OS
    )
    
    # ============== RECENT ACTIVITY ==============
    recent_submissions = all_scans.filter(
        form_submitted=True
    ).order_by('-form_submitted_at')[:20]
    
    recent_scans = all_scans.order_by('-scanned_at')[:10]
    
    # ============== TIME-BASED ANALYTICS ==============
    # Hourly Distribution
    hourly_scans = {}
    for hour in range(24):
        hourly_scans[hour] = all_scans.filter(
            scanned_at__hour=hour
        ).count()
    
    # Daily Trend (Last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    daily_trend = []
    
    for i in range(30):
        date = start_date + timedelta(days=i)
        day_scans = all_scans.filter(
            scanned_at__date=date.date()
        )
        daily_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'scans': day_scans.count(),
            'submissions': day_scans.filter(form_submitted=True).count()
        })
    
    # Peak hours analysis
    peak_hours = sorted(hourly_scans.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # ============== VIDEO ENGAGEMENT ==============
    # Video Watch Distribution
    watch_distribution = {
        '0-25%': all_scans.filter(video_percentage__lte=25).count(),
        '26-50%': all_scans.filter(video_percentage__gt=25, video_percentage__lte=50).count(),
        '51-75%': all_scans.filter(video_percentage__gt=50, video_percentage__lte=75).count(),
        '76-99%': all_scans.filter(video_percentage__gt=75, video_percentage__lt=100).count(),
        '100%': all_scans.filter(video_percentage=100).count(),
    }
    
    # Engagement Funnel
    engagement_funnel = {
        'Total Scans': total_scans,
        'Video Started': all_scans.filter(video_watched__gt=0).count(),
        'Video 50%+': all_scans.filter(video_percentage__gte=50).count(),
        'Video Completed': video_completions,
        'Form Submitted': form_submissions
    }
    
    # ============== PERFORMANCE INDICATORS ==============
    # Calculate bounce rate (scanned but didn't watch video)
    bounce_rate = all_scans.filter(video_watched=0).count()
    bounce_percentage = (bounce_rate / total_scans * 100) if total_scans else 0
    
    # Performance classification
    performance = {
        'excellent': form_conversion_rate >= 30 and video_completion_rate >= 80,
        'good': form_conversion_rate >= 20 and video_completion_rate >= 60,
        'average': form_conversion_rate >= 10 and video_completion_rate >= 40,
        'needs_improvement': form_conversion_rate < 10 or video_completion_rate < 40
    }
    
    # Get performance level
    if performance['excellent']:
        performance_level = 'excellent'
        performance_color = 'success'
    elif performance['good']:
        performance_level = 'good'
        performance_color = 'primary'
    elif performance['average']:
        performance_level = 'average'
        performance_color = 'warning'
    else:
        performance_level = 'needs_improvement'
        performance_color = 'danger'
    
    # ============== EXPORT DATA PREPARATION ==============
    export_data = {
        'campaign_name': campaign.camp_name,
        'client': campaign.client.company_name,
        'report_date': timezone.now().strftime('%Y-%m-%d %H:%M'),
        'total_scans': total_scans,
        'form_submissions': form_submissions,
        'conversion_rate': round(form_conversion_rate, 2),
    }
    
    # ============== CONTEXT ASSEMBLY ==============
    context = {
        'title': f'Campaign Report - {campaign.camp_name}',
        'page': 'reports',
        'campaign': campaign,
        'metrics': {
            'total_scans': total_scans,
            'unique_devices': unique_devices,
            'form_submissions': form_submissions,
            'video_completions': video_completions,
            'form_conversion_rate': round(form_conversion_rate, 2),
            'video_completion_rate': round(video_completion_rate, 2),
            'avg_watch_time': round(avg_watch_time, 1),
            'avg_video_percentage': round(avg_video_percentage, 2),
            'bounce_percentage': round(bounce_percentage, 2),
        },
        'device_stats': device_stats,
        'browser_stats': browser_stats,
        'os_stats': os_stats,
        'recent_submissions': recent_submissions,
        'recent_scans': recent_scans,
        'hourly_scans': hourly_scans,
        'daily_trend': daily_trend,
        'watch_distribution': watch_distribution,
        'engagement_funnel': engagement_funnel,
        'peak_hours': peak_hours,
        'performance': performance,
        'performance_level': performance_level,
        'performance_color': performance_color,
        'export_data': export_data,
    }
    
    return render(request, 'campaign/campaign_report.html', context)

# Add these imports to your existing views.py
from decimal import Decimal
from .models import Manufacturer, Order, Supplier, Supply  # Add these to existing imports

# === ADD THESE NEW VIEWS TO YOUR EXISTING VIEWS.PY ===



# ============== EXPORT FUNCTIONS ==============
@login_required
def export_manufacturers(request):
    """Export manufacturers to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="manufacturers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Contact Person', 'Contact Number', 'Email', 'City', 'State', 'GST Number', 'Total Orders', 'Created Date'])
    
    manufacturers = Manufacturer.objects.all()
    for manufacturer in manufacturers:
        writer.writerow([
            manufacturer.name,
            manufacturer.contact_person,
            manufacturer.contact_number,
            manufacturer.email,
            manufacturer.city,
            manufacturer.state,
            manufacturer.gst_number,
            manufacturer.total_orders,
            manufacturer.created_at.strftime('%Y-%m-%d'),
        ])
    
    return response

@login_required
def export_orders(request):
    """Export orders to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order Number', 'Manufacturer', 'Product', 'Quantity', 'Unit Price', 'Total Amount', 'Status', 'Order Date', 'Expected Delivery'])
    
    orders = Order.objects.select_related('manufacturer')
    for order in orders:
        writer.writerow([
            order.order_number,
            order.manufacturer.name,
            order.product_name,
            order.quantity,
            order.unit_price,
            order.total_amount,
            order.status,
            order.order_date.strftime('%Y-%m-%d'),
            order.expected_delivery.strftime('%Y-%m-%d'),
        ])
    
    return response

@login_required
def export_suppliers(request):
    """Export suppliers to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="suppliers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Type', 'Contact Person', 'Contact Number', 'Email', 'City', 'State', 'Rating', 'Total Supplies'])
    
    suppliers = Supplier.objects.all()
    for supplier in suppliers:
        writer.writerow([
            supplier.name,
            supplier.get_supplier_type_display(),
            supplier.contact_person,
            supplier.contact_number,
            supplier.email,
            supplier.city,
            supplier.state,
            supplier.rating,
            supplier.total_supplies,
        ])
    
    return response

@login_required
def export_supplies(request):
    """Export supplies to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="supplies.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Supply Number', 'Supplier', 'Product', 'Quantity', 'Unit Price', 'Total Amount', 'Status', 'Supply Date', 'Expected Delivery', 'Quality Rating'])
    
    supplies = Supply.objects.select_related('supplier')
    for supply in supplies:
        writer.writerow([
            supply.supply_number,
            supply.supplier.name,
            supply.product_name,
            supply.quantity_supplied,
            supply.unit_price,
            supply.total_amount,
            supply.status,
            supply.supply_date.strftime('%Y-%m-%d'),
            supply.expected_delivery.strftime('%Y-%m-%d'),
            supply.quality_rating,
        ])
    
    return response


# ============== PUBLIC QR LANDING PAGE ==============
import hashlib
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.db import transaction
import uuid

def adv_landing(request, unique_id):
    """
    QR code landing page with proper handling:
    - New scan = New entry (even from same device)
    - Refresh = No new entry (continue with existing scan)
    """
    try:
        campaign = AdvCampaign.objects.get(unique_id=unique_id)
        
        # Check if campaign is active
        if not campaign.is_active:
            return render(request, 'campaign/invalid_qr.html', {
                'error': 'This campaign has ended or is not yet active'
            })

        # Session key for this campaign
        session_scan_key = f'scan_{unique_id}'
        
        # Device info extraction
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        device_type, browser, os = 'unknown', 'Unknown', 'Unknown'
        
        if user_agent_string:
            ua = user_agent_string.lower()
            # Device type - prioritize mobile detection
            if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
                device_type = 'mobile'
            elif 'ipad' in ua or 'tablet' in ua:
                device_type = 'tablet'
            elif 'windows' in ua or 'mac' in ua or 'linux' in ua:
                device_type = 'desktop'
            
            # Browser detection
            if 'chrome' in ua and 'edge' not in ua:
                browser = 'Chrome'
            elif 'safari' in ua and 'chrome' not in ua:
                browser = 'Safari'
            elif 'firefox' in ua:
                browser = 'Firefox'
            elif 'edge' in ua:
                browser = 'Edge'
            elif 'opera' in ua:
                browser = 'Opera'
            
            # OS detection
            if 'android' in ua:
                os = 'Android'
            elif 'iphone' in ua or 'ipad' in ua or 'ipod' in ua:
                os = 'iOS'
            elif 'windows' in ua:
                os = 'Windows'
            elif 'mac' in ua:
                os = 'macOS'
            elif 'linux' in ua:
                os = 'Linux'

        # Get IP address
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or \
                     request.META.get('REMOTE_ADDR', '0.0.0.0')
        
        # Create device fingerprint
        fingerprint_data = f"{user_agent_string}_{ip_address}_{request.META.get('HTTP_ACCEPT_LANGUAGE', '')}"
        device_fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()
        
        # Handle POST (form submission)
        if request.method == 'POST':
            # Get current scan from session
            scan_id = request.session.get(session_scan_key)
            scan = None
            
            if scan_id:
                try:
                    scan = ScanTracking.objects.get(id=scan_id, campaign=campaign)
                except ScanTracking.DoesNotExist:
                    messages.error(request, 'Session expired. Please scan the QR code again.')
                    return redirect('sw:adv_landing', unique_id=unique_id)
            else:
                messages.error(request, 'Session expired. Please scan the QR code again.')
                return redirect('sw:adv_landing', unique_id=unique_id)
            
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            
            # Validation
            if not phone or len(phone) != 10 or not phone.isdigit():
                messages.error(request, 'Please enter a valid 10-digit phone number')
                return redirect('sw:adv_landing', unique_id=unique_id)
            
            if not name or len(name) < 3:
                messages.error(request, 'Please enter your full name (minimum 3 characters)')
                return redirect('sw:adv_landing', unique_id=unique_id)
            
            # Check for duplicate phone submission
            with transaction.atomic():
                existing_submission = ScanTracking.objects.filter(
                    campaign=campaign,
                    user_phone=phone,
                    form_submitted=True
                ).exclude(id=scan.id).exists()
                
                if existing_submission:
                    messages.error(request, 'This phone number has already been registered for this campaign')
                    return redirect('sw:adv_landing', unique_id=unique_id)
                
                # Save form data
                scan.user_name = name
                scan.user_phone = phone
                scan.form_submitted = True
                scan.form_submitted_at = timezone.now()
                scan.save()
                
                # Mark this scan as submitted
                request.session[f'submitted_{scan_id}'] = True
                
                messages.success(request, 'Registration successful! You will receive your reward within 24 hours.')
            
            return redirect('sw:adv_landing', unique_id=unique_id)
        
        # GET request
        # Check for 'new' parameter to force new scan
        force_new = request.GET.get('new', '').lower() == 'true'
        
        # Get existing scan from session
        scan_id = request.session.get(session_scan_key)
        scan = None
        
        if scan_id and not force_new:
            try:
                scan = ScanTracking.objects.get(id=scan_id, campaign=campaign)
                
                # Check if already submitted
                if scan.form_submitted or request.session.get(f'submitted_{scan_id}'):
                    context = {
                        'campaign': campaign,
                        'client': campaign.client,
                        'already_submitted': True,
                        'scan_id': 0,
                        'show_form': False,
                        'resume_position': 0
                    }
                    return render(request, 'campaign/adv_landing.html', context)
            except ScanTracking.DoesNotExist:
                scan = None
        
        # Create new scan if needed
        if not scan:
            # Always create new scan for:
            # 1. First visit (no session)
            # 2. Forced new scan
            # 3. Invalid scan in session
            scan = create_new_scan(
                campaign=campaign,
                ip_address=ip_address,
                user_agent_string=user_agent_string,
                device_fingerprint=device_fingerprint,
                device_type=device_type,
                browser=browser,
                os=os
            )
            request.session[session_scan_key] = scan.id
            # Clear any previous submission flag
            if scan_id:
                request.session.pop(f'submitted_{scan_id}', None)
        
        # Determine if should show form directly (video already watched)
        show_form = scan.video_completed or scan.video_percentage >= 95
        resume_position = scan.video_watched if not show_form else 0
        
        context = {
            'campaign': campaign,
            'client': campaign.client,
            'scan_id': scan.id,
            'already_submitted': False,
            'show_form': show_form,
            'resume_position': resume_position,
            'scan_time': scan.scanned_at,
            'device_type': device_type,
            'browser': browser,
            'os': os,
            'messages': messages.get_messages(request),
            'debug': False  # Set to True for testing
        }
        
        return render(request, 'campaign/adv_landing.html', context)
    
    except AdvCampaign.DoesNotExist:
        return render(request, 'campaign/invalid_qr.html', {
            'error': 'Invalid or expired QR code'
        })
    except Exception as e:
        import traceback
        print(f"Error in adv_landing: {str(e)}")
        print(traceback.format_exc())
        return render(request, 'campaign/invalid_qr.html', {
            'error': 'An error occurred. Please try again.'
        })


def create_new_scan(campaign, ip_address, user_agent_string, device_fingerprint, 
                   device_type, browser, os):
    """Helper function to create new scan record"""
    # Generate unique session ID
    session_id = hashlib.md5(
        f"{ip_address}_{timezone.now().isoformat()}_{user_agent_string}_{os}_{uuid.uuid4()}".encode()
    ).hexdigest()
    
    scan = ScanTracking.objects.create(
        campaign=campaign,
        ip_address=ip_address,
        user_agent=user_agent_string[:500] if user_agent_string else '',
        device_fingerprint=device_fingerprint,
        device_type=device_type,
        browser=browser[:50],
        os=os[:50],
        session_id=session_id,
        video_duration=0,
        video_watched=0,
        video_completed=False,
        video_percentage=0
    )
    return scan


@csrf_exempt
def track_video_progress(request):
    """AJAX endpoint for video progress tracking"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            scan_id = data.get('scan_id')
            
            # Skip tracking if no valid scan_id
            if not scan_id or scan_id == 0:
                return JsonResponse({'status': 'skipped'})
            
            try:
                scan = ScanTracking.objects.get(id=scan_id)
            except ScanTracking.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Scan not found'
                }, status=404)
            
            video_duration = data.get('video_duration', 0)
            watched_seconds = data.get('watched_seconds', 0)
            completed = data.get('completed', False)
            
            # Update video duration if not set
            if video_duration > 0 and scan.video_duration == 0:
                scan.video_duration = video_duration
            
            # Update watched time (keep maximum)
            scan.video_watched = max(scan.video_watched, watched_seconds)
            
            # Mark as completed
            if completed:
                scan.video_completed = True
                scan.video_watched = scan.video_duration
            
            # Calculate percentage
            if scan.video_duration > 0:
                scan.video_percentage = round(
                    min((scan.video_watched / scan.video_duration) * 100, 100), 
                    2
                )
            
            scan.save()
            
            return JsonResponse({
                'status': 'success',
                'tracked': {
                    'duration': scan.video_duration,
                    'watched': scan.video_watched,
                    'percentage': float(scan.video_percentage),
                    'completed': scan.video_completed
                }
            })
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)


# ============== EXPORT FUNCTIONALITY ==============
@login_required
def export_campaign_data(request, unique_id=None):
    """Export campaign data to CSV"""
    campaign_id = unique_id
    if campaign_id:
        try:
            if campaign_id.isdigit():
                campaign = AdvCampaign.objects.get(pk=campaign_id)
            else:
                campaign = AdvCampaign.objects.get(unique_id=campaign_id)
            scans = ScanTracking.objects.filter(campaign=campaign)
            filename = f'campaign_{campaign.unique_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        except AdvCampaign.DoesNotExist:
            messages.error(request, f'Campaign "{campaign_id}" not found.')
            return redirect('sw:report_list')
    else:
        scans = ScanTracking.objects.all()
        filename = f'all_campaigns_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Write UTF-8 BOM for Excel compatibility
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    # Write headers
    writer.writerow([
        'Campaign Name',
        'Campaign ID',
        'Scan Date & Time',
        'Device Type',
        'Browser',
        'Operating System',
        'IP Address',
        'Video Watch Percentage',
        'User Name',
        'User Phone',
        'Form Submitted'
    ])
    
    # Write data rows
    for scan in scans.select_related('campaign'):
        writer.writerow([
            scan.campaign.camp_name if scan.campaign else 'N/A',
            scan.campaign.unique_id if scan.campaign else 'N/A',
            scan.scanned_at.strftime('%Y-%m-%d %H:%M:%S') if scan.scanned_at else '',
            scan.device_type or 'Unknown',
            scan.browser or 'Unknown',
            scan.os or 'Unknown',
            scan.ip_address or '',
            f"{scan.video_percentage:.1f}%" if scan.video_percentage else '0%',
            scan.user_name or '',
            scan.user_phone or '',
            'Yes' if scan.form_submitted else 'No'
        ])
    
    return response



# ============== 9. REWARDS MANAGEMENT ==============
# Add these views to your existing views.py file
# ============== 9. REWARDS MANAGEMENT ==============
# Add these views to your existing views.py file

@login_required
def rewards_list(request):
    """List all campaigns with reward management"""
    campaigns = AdvCampaign.objects.annotate(
        total_scans=Count('scans'),
        total_submissions=Count('scans', filter=Q(scans__form_submitted=True)),
        pending_rewards=Count('scans', filter=Q(
            scans__form_submitted=True,
            scans__reward_status='pending'
        )),
        granted_rewards=Count('scans', filter=Q(
            scans__form_submitted=True,
            scans__reward_status='granted'
        )),
        invalid_rewards=Count('scans', filter=Q(
            scans__form_submitted=True,
            scans__reward_status='invalid'
        ))
    ).select_related('client').order_by('-created_at')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        campaigns = campaigns.filter(
            Q(camp_name__icontains=search_query) |
            Q(client__company_name__icontains=search_query)
        )
    
    context = {
        'title': 'Reward Management',
        'page': 'rewards',
        'campaigns': campaigns,
        'search_query': search_query,
    }
    return render(request, 'campaign/rewards_list.html', context)

@login_required
def rewards_detail(request, campaign_id):
    """Detailed reward management for a specific campaign"""
    campaign = get_object_or_404(AdvCampaign, id=campaign_id)
    
    # Handle POST requests for status updates
    if request.method == 'POST':
        action = request.POST.get('action')
        scan_id = request.POST.get('scan_id')
        
        if action == 'update_status' and scan_id:
            try:
                scan = ScanTracking.objects.get(id=scan_id, campaign=campaign)
                new_status = request.POST.get('reward_status')
                
                if new_status in ['pending', 'granted', 'invalid']:
                    scan.reward_status = new_status
                    
                    # Update reward amount if granted
                    if new_status == 'granted':
                        amount = request.POST.get('reward_amount')
                        if amount:
                            scan.reward_amount = Decimal(amount)
                            scan.reward_granted_at = timezone.now()
                    elif new_status == 'invalid':
                        scan.reward_notes = request.POST.get('notes', 'Invalid details')
                    
                    scan.save()
                    messages.success(request, f'Status updated for {scan.user_name}')
                    
            except ScanTracking.DoesNotExist:
                messages.error(request, 'Scan record not found')
            except Exception as e:
                messages.error(request, f'Error updating status: {str(e)}')
                
        elif action == 'bulk_update':
            scan_ids = request.POST.getlist('scan_ids')
            new_status = request.POST.get('bulk_status')
            bulk_amount = request.POST.get('bulk_amount')
            
            if scan_ids and new_status:
                updated = 0
                for sid in scan_ids:
                    try:
                        scan = ScanTracking.objects.get(id=sid, campaign=campaign)
                        scan.reward_status = new_status
                        
                        if new_status == 'granted' and bulk_amount:
                            scan.reward_amount = Decimal(bulk_amount)
                            scan.reward_granted_at = timezone.now()
                        
                        scan.save()
                        updated += 1
                    except:
                        continue
                
                messages.success(request, f'Updated {updated} records')
        
        return redirect('sw:rewards_detail', campaign_id=campaign_id)
    
    # Get submissions with filters
    submissions = ScanTracking.objects.filter(
        campaign=campaign,
        form_submitted=True
    ).order_by('-form_submitted_at')
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        submissions = submissions.filter(reward_status=status_filter)
    
    if search_query:
        submissions = submissions.filter(
            Q(user_name__icontains=search_query) |
            Q(user_phone__icontains=search_query)
        )
    
    # Calculate statistics
    total_submissions = submissions.count()
    total_budget = campaign.budget_of_rewards or 0
    
    # Calculate amounts
    granted_amount = submissions.filter(
        reward_status='granted'
    ).aggregate(
        total=Sum('reward_amount')
    )['total'] or Decimal('0')
    
    remaining_budget = total_budget - granted_amount
    
    # Calculate budget percentage used
    budget_percentage = 0
    if total_budget > 0:
        budget_percentage = min((float(granted_amount) / float(total_budget)) * 100, 100)
    
    stats = {
        'total_scans': campaign.scans.count(),
        'total_submissions': total_submissions,
        'pending': submissions.filter(reward_status='pending').count(),
        'granted': submissions.filter(reward_status='granted').count(),
        'invalid': submissions.filter(reward_status='invalid').count(),
        'total_budget': total_budget,
        'granted_amount': granted_amount,
        'remaining_budget': remaining_budget,
        'avg_reward': granted_amount / submissions.filter(reward_status='granted').count() if submissions.filter(reward_status='granted').count() > 0 else 0,
        'budget_percentage': round(budget_percentage, 1),
    }
    
    # Pagination
    paginator = Paginator(submissions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': f'Rewards - {campaign.camp_name}',
        'page': 'rewards',
        'campaign': campaign,
        'submissions': page_obj,
        'stats': stats,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'campaign/rewards_detail.html', context)

@login_required
def export_rewards(request, campaign_id):
    """Export reward data to CSV"""
    campaign = get_object_or_404(AdvCampaign, id=campaign_id)
    
    response = HttpResponse(content_type='text/csv')
    filename = f'rewards_{campaign.unique_id}_{timezone.now().strftime("%Y%m%d")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Write UTF-8 BOM
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow([
        'Date Submitted',
        'Name',
        'Phone',
        'Video Watched %',
        'Reward Status',
        'Reward Amount',
        'Granted Date',
        'Notes'
    ])
    
    submissions = ScanTracking.objects.filter(
        campaign=campaign,
        form_submitted=True
    ).order_by('-form_submitted_at')
    
    for sub in submissions:
        writer.writerow([
            sub.form_submitted_at.strftime('%Y-%m-%d %H:%M') if sub.form_submitted_at else '',
            sub.user_name,
            sub.user_phone,
            f"{sub.video_percentage:.1f}%",
            sub.get_reward_status_display() if hasattr(sub, 'get_reward_status_display') else sub.reward_status,
            sub.reward_amount if sub.reward_amount else '',
            sub.reward_granted_at.strftime('%Y-%m-%d %H:%M') if sub.reward_granted_at else '',
            sub.reward_notes if sub.reward_notes else ''
        ])
    
    return response



# ============== IMPROVED MANAGEMENT VIEWS ==============
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from datetime import datetime

# ============== 5. MANUFACTURERS (TABLE VIEW) ==============
# ============== IMPROVED MANAGEMENT VIEWS ==============
# ============== IMPROVED MANAGEMENT VIEWS ==============
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from datetime import datetime

# ============== 5. MANUFACTURERS (TABLE VIEW) ==============
@login_required
def manufacturer_list(request):
    """Manufacturer management with table view"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'quick_update':
            # Handle inline updates via AJAX
            manufacturer_id = request.POST.get('id')
            field = request.POST.get('field')
            value = request.POST.get('value')
            
            try:
                manufacturer = Manufacturer.objects.get(pk=manufacturer_id)
                setattr(manufacturer, field, value)
                manufacturer.save()
                return JsonResponse({'status': 'success'})
            except Manufacturer.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Manufacturer not found'})
        
        else:
            # Handle regular form submissions
            return handle_manufacturer_crud(request)
    
    # GET request - Table view
    manufacturers = Manufacturer.objects.annotate(
        order_count=Count('orders'),
        pending_order_count=Count('orders', filter=Q(orders__status='pending')),
        order_total_value=Sum('orders__total_amount')
    ).order_by('-created_at')
    
    # Search and filter
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        manufacturers = manufacturers.filter(
            Q(name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(city__icontains=search_query)
        )
    
    if status_filter == 'active':
        manufacturers = manufacturers.filter(is_active=True)
    elif status_filter == 'inactive':
        manufacturers = manufacturers.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(manufacturers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Manufacturer Management',
        'page': 'manufacturers',
        'manufacturers': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_count': manufacturers.count(),
    }
    
    return render(request, 'campaign/manufacturers_table.html', context)

def handle_manufacturer_crud(request):
    """Handle manufacturer CRUD operations"""
    action = request.POST.get('action')
    manufacturer_id = request.POST.get('manufacturer_id')
    
    if action == 'create':
        manufacturer = Manufacturer.objects.create(
            name=request.POST.get('name'),
            contact_person=request.POST.get('contact_person'),
            contact_number=request.POST.get('contact_number'),
            address=request.POST.get('address'),
            city=request.POST.get('city', ''),
            state=request.POST.get('state', ''),
            email=request.POST.get('email', ''),
            gst_number=request.POST.get('gst_number', ''),
            registration_number=request.POST.get('registration_number', ''),
            postal_code=request.POST.get('postal_code', ''),
        )
        messages.success(request, f'Manufacturer "{manufacturer.name}" created!')
    
    elif action == 'update' and manufacturer_id:
        manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)
        manufacturer.name = request.POST.get('name')
        manufacturer.contact_person = request.POST.get('contact_person')
        manufacturer.contact_number = request.POST.get('contact_number')
        manufacturer.address = request.POST.get('address')
        manufacturer.city = request.POST.get('city', '')
        manufacturer.state = request.POST.get('state', '')
        manufacturer.email = request.POST.get('email', '')
        manufacturer.gst_number = request.POST.get('gst_number', '')
        manufacturer.save()
        messages.success(request, f'Manufacturer "{manufacturer.name}" updated!')
    
    elif action == 'toggle_status' and manufacturer_id:
        manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)
        manufacturer.is_active = not manufacturer.is_active
        manufacturer.save()
        status = 'activated' if manufacturer.is_active else 'deactivated'
        messages.success(request, f'Manufacturer "{manufacturer.name}" {status}!')
    
    elif action == 'delete' and manufacturer_id:
        manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)
        name = manufacturer.name
        manufacturer.delete()
        messages.success(request, f'Manufacturer "{name}" deleted!')
    
    return redirect('sw:manufacturer_list')

# ============== 6. ORDERS (TABLE VIEW) ==============
@login_required
def order_list(request):
    """Order management with table view and inline status updates"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            # Quick status update
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')
            
            try:
                order = Order.objects.get(pk=order_id)
                order.status = new_status
                
                # Update actual delivery if marking as delivered
                if new_status == 'delivered':
                    order.actual_delivery = timezone.now().date()
                
                order.save()
                messages.success(request, f'Order #{order.order_number} status updated!')
            except Order.DoesNotExist:
                messages.error(request, 'Order not found')
            
            return redirect('sw:order_list')
        
        elif action == 'update_priority':
            # Quick priority update
            order_id = request.POST.get('order_id')
            new_priority = request.POST.get('priority')
            
            try:
                order = Order.objects.get(pk=order_id)
                order.priority = new_priority
                order.save()
                messages.success(request, f'Order #{order.order_number} priority updated!')
            except Order.DoesNotExist:
                messages.error(request, 'Order not found')
            
            return redirect('sw:order_list')
        
        else:
            # Handle regular CRUD
            return handle_order_crud(request)
    
    # GET request - Table view
    orders = Order.objects.select_related('manufacturer').order_by('-order_date')
    
    # Filters
    search_query = request.GET.get('search', '')
    manufacturer_id = request.GET.get('manufacturer', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(product_name__icontains=search_query) |
            Q(manufacturer__name__icontains=search_query)
        )
    
    if manufacturer_id:
        orders = orders.filter(manufacturer_id=manufacturer_id)
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if priority_filter:
        orders = orders.filter(priority=priority_filter)
    
    # Get manufacturers for dropdown
    manufacturers = Manufacturer.objects.filter(is_active=True).order_by('name')
    
    # Statistics
    stats = {
        'total': orders.count(),
        'pending': orders.filter(status='pending').count(),
        'processing': orders.filter(status='processing').count(),
        'completed': orders.filter(status='completed').count(),
        'total_value': orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
    }
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Order Management',
        'page': 'orders',
        'orders': page_obj,
        'manufacturers': manufacturers,
        'search_query': search_query,
        'selected_manufacturer': manufacturer_id,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': Order.STATUS_CHOICES,
        'priority_choices': Order.PRIORITY_CHOICES,
        'stats': stats,
    }
    
    return render(request, 'campaign/orders_table.html', context)

def handle_order_crud(request):
    """Handle order CRUD operations"""
    action = request.POST.get('action')
    
    if action == 'create':
        try:
            manufacturer = Manufacturer.objects.get(pk=request.POST.get('manufacturer'))
            order = Order.objects.create(
                manufacturer=manufacturer,
                order_number=request.POST.get('order_number'),
                product_name=request.POST.get('product_name'),
                quantity=int(request.POST.get('quantity')),
                unit_price=Decimal(request.POST.get('unit_price')),
                expected_delivery=datetime.strptime(
                    request.POST.get('expected_delivery'), '%Y-%m-%d'
                ).date(),
                product_description=request.POST.get('product_description', ''),
                priority=request.POST.get('priority', 'medium'),
                notes=request.POST.get('notes', ''),
            )
            messages.success(request, f'Order #{order.order_number} created!')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    elif action == 'delete':
        order = get_object_or_404(Order, pk=request.POST.get('order_id'))
        order_num = order.order_number
        order.delete()
        messages.success(request, f'Order #{order_num} deleted!')
    
    return redirect('sw:order_list')

# ============== 7. SUPPLIERS (TABLE VIEW) ==============
@login_required
def supplier_list(request):
    """Supplier management with table view"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_rating':
            # Quick rating update
            supplier_id = request.POST.get('supplier_id')
            rating = request.POST.get('rating')
            
            try:
                supplier = Supplier.objects.get(pk=supplier_id)
                supplier.rating = Decimal(rating)
                supplier.save()
                return JsonResponse({'status': 'success'})
            except Supplier.DoesNotExist:
                return JsonResponse({'status': 'error'})
        
        else:
            return handle_supplier_crud(request)
    
    # GET request
    suppliers = Supplier.objects.annotate(
        supply_count=Count('supplies'),
        active_supply_count=Count('supplies', filter=Q(supplies__status__in=['pending', 'processing']))
    ).order_by('supplier_type', 'name')
    
    # Filters
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(city__icontains=search_query)
        )
    
    if type_filter:
        suppliers = suppliers.filter(supplier_type=type_filter)
    
    # Statistics by type
    type_stats = {}
    for stype, label in Supplier.SUPPLIER_TYPES:
        type_stats[label] = suppliers.filter(supplier_type=stype).count()
    
    # Pagination
    paginator = Paginator(suppliers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Supplier Management',
        'page': 'suppliers',
        'suppliers': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'supplier_types': Supplier.SUPPLIER_TYPES,
        'type_stats': type_stats,
        'total_count': suppliers.count(),
    }
    
    return render(request, 'campaign/suppliers_table.html', context)

def handle_supplier_crud(request):
    """Handle supplier CRUD operations"""
    action = request.POST.get('action')
    supplier_id = request.POST.get('supplier_id')
    
    if action == 'create':
        try:
            supplier = Supplier.objects.create(
                name=request.POST.get('name'),
                supplier_type=request.POST.get('supplier_type'),
                contact_person=request.POST.get('contact_person'),
                contact_number=request.POST.get('contact_number'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                postal_code=request.POST.get('postal_code', ''),
                email=request.POST.get('email', ''),
                business_license=request.POST.get('business_license', ''),
                gst_number=request.POST.get('gst_number', ''),
            )
            messages.success(request, f'Supplier "{supplier.name}" created!')
        except Exception as e:
            messages.error(request, f'Error creating supplier: {str(e)}')
    
    elif action == 'toggle_status' and supplier_id:
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        supplier.is_active = not supplier.is_active
        supplier.save()
        status = 'activated' if supplier.is_active else 'deactivated'
        messages.success(request, f'Supplier "{supplier.name}" {status}!')
    
    elif action == 'delete' and supplier_id:
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        name = supplier.name
        supplier.delete()
        messages.success(request, f'Supplier "{name}" deleted!')
    
    return redirect('sw:supplier_list')

# ============== 8. SUPPLIES (TABLE VIEW) ==============
@login_required
def supply_list(request):
    """Supply management with table view and inline updates"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            supply_id = request.POST.get('supply_id')
            new_status = request.POST.get('status')
            
            try:
                supply = Supply.objects.get(pk=supply_id)
                supply.status = new_status
                
                if new_status == 'delivered':
                    supply.actual_delivery = timezone.now().date()
                
                supply.save()
                messages.success(request, f'Supply #{supply.supply_number} updated!')
            except Supply.DoesNotExist:
                messages.error(request, 'Supply not found')
            
            return redirect('sw:supply_list')
        
        else:
            return handle_supply_crud(request)
    
    # GET request
    supplies = Supply.objects.select_related('supplier').prefetch_related('orders').order_by('-supply_date')
    
    # Filters
    search_query = request.GET.get('search', '')
    supplier_id = request.GET.get('supplier', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        supplies = supplies.filter(
            Q(supply_number__icontains=search_query) |
            Q(product_name__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )
    
    if supplier_id:
        supplies = supplies.filter(supplier_id=supplier_id)
    
    if status_filter:
        supplies = supplies.filter(status=status_filter)
    
    # Get suppliers for dropdown
    suppliers = Supplier.objects.filter(is_active=True).order_by('name')
    
    # Statistics
    stats = {
        'total': supplies.count(),
        'pending': supplies.filter(status='pending').count(),
        'delivered': supplies.filter(status='delivered').count(),
        'total_value': supplies.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
    }
    
    # Pagination
    paginator = Paginator(supplies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Supply Management',
        'page': 'supplies',
        'supplies': page_obj,
        'suppliers': suppliers,
        'search_query': search_query,
        'selected_supplier': supplier_id,
        'status_filter': status_filter,
        'status_choices': Supply.STATUS_CHOICES,
        'stats': stats,
    }
    
    return render(request, 'campaign/supplies_table.html', context)

def handle_supply_crud(request):
    """Handle supply CRUD operations"""
    action = request.POST.get('action')
    
    if action == 'create':
        try:
            supplier = Supplier.objects.get(pk=request.POST.get('supplier'))
            supply = Supply.objects.create(
                supplier=supplier,
                supply_number=request.POST.get('supply_number'),
                product_name=request.POST.get('product_name'),
                quantity_supplied=int(request.POST.get('quantity_supplied')),
                unit_price=Decimal(request.POST.get('unit_price')),
                expected_delivery=datetime.strptime(
                    request.POST.get('expected_delivery'), '%Y-%m-%d'
                ).date(),
                tracking_number=request.POST.get('tracking_number', ''),
                delivery_notes=request.POST.get('delivery_notes', ''),
            )
            
            # Handle orders relationship
            order_ids = request.POST.getlist('orders')
            if order_ids:
                supply.orders.set(order_ids)
            
            messages.success(request, f'Supply #{supply.supply_number} created!')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    elif action == 'delete':
        supply = get_object_or_404(Supply, pk=request.POST.get('supply_id'))
        supply_num = supply.supply_number
        supply.delete()
        messages.success(request, f'Supply #{supply_num} deleted!')
    
    return redirect('sw:supply_list')