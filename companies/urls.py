from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('login/', views.company_login, name='company_login'),
    path('register/', views.company_register, name='company_register'),
    path('dashboard/', views.company_dashboard, name='company_dashboard'),
    path('profile/', views.company_profile, name='company_profile'),
    # path('jobs/', views.job_list, name='job_list'),  # From first version
    path('manage-jobs/', views.manage_jobs, name='manage_jobs'),
    
    # Additional job controls
    path('toggle-job/<int:job_id>/', views.toggle_job_status, name='toggle_job_status'),  # From second version
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),  # From second version

    # path('view-applications/', views.view_applications, name='view_applications'),
    path("application/<int:pk>/update-status/", views.update_application_status,name="update_application_status"),

    path('delete-account/', views.delete_company_account, name='delete_account'),
    path('logout/', views.company_logout, name='company_logout'),
    
    path('applications/', views.view_applications, name='view_applications'),
    path('application/<int:application_id>/detail/', views.application_detail, name='application_detail'),
    path('application/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('application/<int:application_id>/save-notes/', views.save_application_notes, name='save_application_notes'),
    path('upload-logo/', views.upload_company_logo, name='upload_company_logo'),    # ← ADD THIS
    path('delete-logo/', views.delete_company_logo, name='delete_company_logo'),    # ← ADD THIS
    
    
]
