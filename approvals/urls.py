from django.urls import path
from . import views

app_name = 'approvals'

urlpatterns = [
    path('', views.discovery_view, name='discovery'),
    path('api/filter/', views.api_filter_approvals, name='api_filter'),
    path('<slug:code>/', views.detail_view, name='detail'),
]
