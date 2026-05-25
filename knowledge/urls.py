from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    # Modules
    path('modules/', views.module_list, name='module_list'),
    path('modules/<slug:slug>/', views.module_detail, name='module_detail'),

    # Processes
    path('processes/', views.process_explorer, name='process_explorer'),
    path('processes/create/', views.process_create, name='process_create'),
    path('processes/<slug:slug>/', views.process_detail, name='process_detail'),
    path('processes/<slug:slug>/edit/', views.process_edit, name='process_edit'),

    # T-Codes
    path('tcodes/', views.tcode_directory, name='tcode_directory'),
    path('tcodes/search/', views.tcode_search_ajax, name='tcode_search_ajax'),

    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/upload/', views.document_upload, name='document_upload'),
    path('documents/<int:pk>/download/', views.document_download, name='document_download'),

    # FAQs
    path('faqs/', views.faq_list, name='faq_list'),
    path('faqs/create/', views.faq_create, name='faq_create'),

    # Announcements
    path('announcements/create/', views.announcement_create, name='announcement_create'),

    # Global Search
    path('search/', views.global_search, name='search'),
]