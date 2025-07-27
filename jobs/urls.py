from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.main, name='main'),
    path('jobs_joblist/', views.job_list, name='job_list'),
    path('post-job/', views.post_job, name='post_job'),
    path('applications/', views.view_applications, name='view_applications'),
    path('contactus/', views.contactus, name='contactus'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('detail/<int:job_id>/', views.job_detail, name='job_detail'),  # /jobs/detail/123/
    path('apply/', views.apply_job, name='apply_job'),  # /jobs/apply/
    path('edit/<int:job_id>/', views.edit_job, name='edit_job'),  # /jobs/edit/123/
    path('delete/<int:job_id>/', views.delete_job, name='delete_job'),  # /jobs/delete/123/
    path('bookmark/', views.bookmark_job, name='bookmark_job'),  # /jobs/bookmark/
    path('search/', views.job_search, name='job_search'),  # /jobs/search/

]   

