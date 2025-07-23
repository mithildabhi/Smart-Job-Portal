from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # path('register/', views.student_register, name='student_register'),
    path('login/', views.student_login, name='student_login'),
    path('logout/', views.student_logout, name='student_logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', views.student_profile, name='student_profile'),
]

# urlpatterns = [
    # Remove this line that's causing the error:
    # path('', views.main, name='main'),
    
    # Student registration & authentication
    # path('register/', views.student_register, name='student_register'),
    # path('login/', views.student_login, name='student_login'),
    # path('logout/', views.student_logout, name='student_logout'),
    
    # Student dashboard & profile
    # path('dashboard/', views.student_dashboard, name='student_dashboard'),
    # path('profile/', views.student_profile, name='student_profile'),
    # path('profile/edit/', views.edit_student_profile, name='edit_student_profile'),
    
    # # Student applications
    # path('applications/', views.student_applications, name='student_applications'),
    # path('apply/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    # path('applications/<int:application_id>/withdraw/', views.withdraw_application, name='withdraw_application'),
    
    # # Student resources
    # path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
    # path('save-job/<int:job_id>/', views.save_job, name='save_job'),
    
# ]
