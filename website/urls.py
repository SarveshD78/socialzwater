# Add to website/urls.py

from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('coming-soon/', views.qr_landing, name='qr_landing'),
    path('business/', views.business_hotels, name='business_hotels'),
    path('brands/', views.smart_brands, name='smart_brands'),
    path('earn/', views.earn_with_us, name='earn_with_us'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('admin-login/', views.custom_login, name='custom_login'),
    path('admin-logout/', views.custom_logout, name='custom_logout'),
    
    # Dashboard
    path('admin-dashboard/', views.dashboard, name='dashboard'),
]