from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('create/<slug:approval_code>/', views.create_view, name='create'),
    path('<str:app_id>/', views.track_view, name='track'),
    path('officer/review/<str:app_id>/', views.officer_review_view, name='officer_review'),
    path('officer/status/<str:app_id>/', views.officer_update_status, name='officer_update_status'),
    path('officer/query/<str:app_id>/', views.officer_raise_query, name='officer_raise_query'),
    path('query/respond/<int:query_id>/', views.respond_query, name='respond_query'),
]
