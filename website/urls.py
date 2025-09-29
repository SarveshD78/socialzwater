# Add to website/urls.py

from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('s_waters', views.qr_landing, name='qr_landing'),
    path('contact/', views.contact, name='contact'),
    path('partner/', views.partner, name='partner'),
    path('get-started', views.contact, name='get-started'),
    path('faq/', views.faqs, name='faqs'),
]