# companies/urls.py
from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('login/', views.company_login, name='company_login'),
    path('register/', views.company_register, name='company_register'),
    path('dashboard/', views.company_dashboard, name='company_dashboard'),
    path('profile/', views.company_profile, name='company_profile'),
    path('post-job/', views.post_job, name='post_job'),
    path('jobs/', views.job_list, name='job_list'),
    path('manage-jobs/', views.manage_jobs, name='manage_jobs'),
    path('view-applications/', views.view_applications, name='view_applications'),
    path('update-application-status/', views.update_application_status, name='update_application_status'),
    path('logout/', views.company_logout, name='company_logout'),
]
