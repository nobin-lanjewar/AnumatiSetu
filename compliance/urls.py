from django.urls import path
from . import views

app_name = 'compliance'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('renew/<int:compliance_id>/', views.submit_renewal, name='submit_renewal'),
]
