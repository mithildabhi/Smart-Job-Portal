from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_home, name='company-home'),
]
