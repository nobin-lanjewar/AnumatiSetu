from django.urls import path
from . import views

app_name = 'schemes'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('api/check-eligibility/<int:scheme_id>/', views.check_eligibility_api, name='check_eligibility'),
]
