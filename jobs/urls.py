from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:id>/', views.job_detail, name='job_detail'),

    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:id>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:id>/delete/', views.job_delete, name='job_delete'),

    path('jobs/<int:id>/apply/', views.apply_job, name='apply_job'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', views.register, name='register'),

    path('jobs/<int:id>/applications/', views.job_applications, name='job_applications'),
    path('applications/<int:id>/hire/', views.hire_freelancer, name='hire_freelancer'),

    # Both URLs point to the same view — role is handled inside it
    path('dashboard/', views.client_dashboard, name='client_dashboard'),
    path('dashboard/', views.client_dashboard, name='freelancer_dashboard'),

    path('jobs/<int:job_id>/chat/', views.job_chat, name='job_chat'),
    path('jobs/<int:job_id>/send/', views.send_message, name='send_message'),

    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),

    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('notifications/<int:id>/read/', views.notification_read, name='notification_read'),
    path('notifications/<int:id>/delete/', views.delete_notification, name='delete_notification'),

    path('profile/<str:username>/review/', views.leave_review, name='leave_review'),

    path('jobs/<int:id>/complete/', views.mark_complete, name='mark_complete'),
]






