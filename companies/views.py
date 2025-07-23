from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.


def company_home(request):
    return HttpResponse("Welcome to the Company section!")

def company_login(request):
    return render(request, 'companies/company_login.html')

@login_required
def post_job(request):
    return render(request, 'companies/post_job.html')

@login_required
def view_applications(request):
    return render(request, 'companies/view_applications.html')