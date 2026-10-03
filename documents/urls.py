from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.precheck_view, name='precheck'),
    path('upload/', views.upload_document_view, name='upload'),
    path('api/recheck/<int:doc_id>/', views.trigger_precheck_api, name='trigger_recheck'),
]
