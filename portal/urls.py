from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    # Root — redirects to the correct dashboard based on role
    path('',                         views.role_redirect,          name='home'),
    path('dashboard/',               views.role_redirect,          name='dashboard'),

    # Role-specific dashboards
    path('user-dashboard/',          views.user_dashboard,         name='user_dashboard'),
    path('admin-dashboard/',         views.admin_dashboard,        name='admin_dashboard'),

    # Bulk upload endpoints (admin/trainer only)
    path('bulk/csv/',                views.bulk_csv_upload,        name='bulk_csv_upload'),
    path('bulk/documents/',          views.bulk_document_upload,   name='bulk_document_upload'),
    path('bulk/csv/template/',       views.download_csv_template,  name='csv_template'),
]