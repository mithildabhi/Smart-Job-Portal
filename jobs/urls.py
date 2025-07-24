from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.main, name='main'),
    path('jobs/', views.job_list, name='job_list'),
    path('post-job/', views.post_job, name='post_job'),
    path('applications/', views.view_applications, name='view_applications'),
    path('contactus/', views.contactus, name='contactus'),
    path('aboutus/', views.aboutus, name='aboutus'),
]   

