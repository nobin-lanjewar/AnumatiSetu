from django.urls import path
from . import views

app_name = 'inspections'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('schedule/', views.schedule_inspection_view, name='schedule'),
    path('update/<int:inspection_id>/', views.update_inspection_status, name='update_status'),
]
