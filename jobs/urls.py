from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('contact/', views.contact, name='contact'),
    path('recruiter/dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('recruiter/job_post/', views.post_job, name='post_job'),
    path('recruiter/job/<int:job_id>/applicants/', views.view_applicants, name='view_applicants'),
    path('recruiter/applicant/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
]
