from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('ask/', views.question_create, name='question_create'),
    path('<int:pk>/', views.question_detail, name='question_detail'),
    path('answers/<int:pk>/accept/', views.accept_answer, name='accept_answer'),
    path('answers/<int:pk>/upvote/', views.upvote_answer, name='upvote_answer'),
]