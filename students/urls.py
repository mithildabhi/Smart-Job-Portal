# students/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # example route
    path('', views.home, name='student-home'),
]
