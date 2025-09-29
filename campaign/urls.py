# urls.py - Fixed URL ordering
from django.urls import path
from . import views

app_name = 'sw'

urlpatterns = [
    # Authentication
    path('login/', views.custom_login, name='custom_login'),
    path('logout/', views.custom_logout, name='custom_logout'),
    
    # 1. Overview
    path('', views.overview, name='overview'),
    path('overview/', views.overview, name='overview'),
    
    # 2. Clients
    path('clients/', views.client_list, name='client_list'),
    
    # 3. Campaigns
    path('campaigns/', views.campaign_list, name='campaign_list'),
    
    # 4. Reports
    path('reports/', views.report_list, name='report_list'),
    path('reports/<str:unique_id>/', views.report_detail, name='report_detail'),
    
    # 5. Manufacturers
    path('manufacturers/', views.manufacturer_list, name='manufacturer_list'),
    
    # 6. Orders
    path('orders/', views.order_list, name='order_list'),
    
    # 7. Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    
    # 8. Supplies
    path('supplies/', views.supply_list, name='supply_list'),
    
    # Export functionality - SPECIFIC PATHS FIRST
    path('export/manufacturers/', views.export_manufacturers, name='export_manufacturers'),
    path('export/orders/', views.export_orders, name='export_orders'),
    path('export/suppliers/', views.export_suppliers, name='export_suppliers'),
    path('export/supplies/', views.export_supplies, name='export_supplies'),
    # GENERIC PATHS LAST
    path('export/', views.export_campaign_data, name='export_all_data'),
    path('export/<str:unique_id>/', views.export_campaign_data, name='export_campaign_data'),
    
    # PUBLIC URLs
    path('adv/<str:unique_id>/', views.adv_landing, name='adv_landing'),
    
    # AJAX Endpoints
    path('track-video/', views.track_video_progress, name='track_video_progress'),
    path('rewards/', views.rewards_list, name='rewards_list'),
    path('rewards/<int:campaign_id>/', views.rewards_detail, name='rewards_detail'),
    path('rewards/<int:campaign_id>/export/', views.export_rewards, name='export_rewards'),
]