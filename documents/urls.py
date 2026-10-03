from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.precheck_view, name='precheck'),
    path('precheck/', views.precheck_view, name='precheck_alias'),
    path('upload/', views.upload_document_view, name='upload'),
    path('view/<int:doc_id>/', views.view_document_file, name='view_file'),
    path('delete/<int:doc_id>/', views.delete_document_view, name='delete'),
    path('api/recheck/<int:doc_id>/', views.trigger_precheck_api, name='trigger_recheck'),
]
