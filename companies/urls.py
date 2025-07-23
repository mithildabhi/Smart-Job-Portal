from django.urls import path
from . import views

app_name = 'companies'



urlpatterns = [
    path('dashboard/', views.company_home, name='company_home'),

    # Company registration & authentication
    # path('register/', views.company_register, name='company_register'),
    # path('login/', views.company_login, name='company_login'),
    # path('logout/', views.company_logout, name='company_logout'),
    
    # Company dashboard & profile
    # path('dashboard/', views.company_dashboard, name='company_dashboard'),
    # path('profile/', views.company_profile, name='company_profile'),
    # path('profile/edit/', views.edit_company_profile, name='edit_company_profile'),
    
    # Company job management
    # path('jobs/', views.company_jobs, name='company_jobs'),
    # path('jobs/<int:job_id>/applicants/', views.view_job_applicants, name='view_job_applicants'),
    
    # Company listing
    # path('', views.company_list, name='company_list'),
    # path('<int:company_id>/', views.company_detail, name='company_detail'),
]
