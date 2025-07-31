from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    # Authentication URLs
    path('register/', views.company_register, name='company_register'),
    path('login/', views.company_login, name='company_login'),
    path('logout/', views.company_logout, name='company_logout'),
    
    # Company Dashboard & Profile
    path('dashboard/', views.company_dashboard, name='company_dashboard'),
    path('profile/', views.company_profile, name='company_profile'),
    path('delete-account/', views.delete_company_account, name='delete_account'),
    
    # Job Management
    path('post-job/', views.post_job, name='post_job'),
    path('manage-jobs/', views.manage_jobs, name='manage_jobs'),
    path('toggle-job/<int:job_id>/', views.toggle_job_status, name='toggle_job_status'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
    
    # Application Management
    path('applications/', views.view_applications, name='view_applications'),
    path('application/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('application/<int:application_id>/detail/', views.application_detail, name='application_detail'),
    path('application/<int:application_id>/save-notes/', views.save_application_notes, name='save_application_notes'),
    
    # Company Logo Management
    path('upload-logo/', views.upload_company_logo, name='upload_company_logo'),
    path('delete-logo/', views.delete_company_logo, name='delete_company_logo'),
    
    # Advanced Features
    path('applications/bulk-update/', views.bulk_update_applications, name='bulk_update_applications'),
    path('statistics/', views.get_application_statistics, name='get_application_statistics'),
]
