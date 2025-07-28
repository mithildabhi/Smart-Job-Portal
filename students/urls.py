from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # path('register/', views.student_register, name='student_register'),
    path('login/', views.student_login, name='student_login'),
    path('logout/', views.student_logout, name='student_logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', views.student_profile, name='student_profile'),
    path('register/', views.student_register, name='student_register'),
    path('saved_jobs/', views.saved_jobs, name='saved_jobs'),
    path('applications/', views.student_applications, name='student_applications'),
    path('withdraw-application/<int:application_id>/', views.withdraw_application, name='withdraw_application'),

    path('profile/upload-picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('profile/delete-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    path('profile/', views.student_profile, name='student_profile'),
    path('delete-account/', views.delete_student_account, name='delete_account'),

]
