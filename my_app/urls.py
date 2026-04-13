from django.urls import path
from . import views

urlpatterns = [
    path('article/<int:id>/', views.article_detail, name='article_detail'),
    path('jobs/<int:job_id>/messages/', views.job_messages, name='job_messages'),
]
