"""
URL configuration for AnumatiSetu project.
SIH26130 — Smart India Hackathon 2026
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public Institutional Pages
    path('', views.home_view, name='home'),
    path('how-it-works/', views.how_it_works_view, name='how_it_works'),
    path('about/', views.about_view, name='about'),
    path('location-intelligence/', views.location_intelligence_view, name='location_intelligence'),
    path('health/', views.health_check_view, name='health_check'),
    
    # Dashboard Role Redirection & Dashboards
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('entrepreneur/dashboard/', views.entrepreneur_dashboard_view, name='entrepreneur_dashboard'),
    path('officer/dashboard/', views.officer_dashboard_view, name='officer_dashboard'),

    # Domain Apps
    path('accounts/', include('accounts.urls')),
    path('business/', include('business.urls')),
    path('approvals/', include('approvals.urls')),
    path('documents/', include('documents.urls')),
    path('applications/', include('applications.urls')),
    path('inspections/', include('inspections.urls')),
    path('compliance/', include('compliance.urls')),
    path('schemes/', include('schemes.urls')),
    path('assistant/', include('assistant.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
