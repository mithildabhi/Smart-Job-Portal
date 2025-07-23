from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Job, Application
from .forms import JobForm, StatusUpdateForm
from jobs.models import Job  # Import your models as needed
from companies.models import Company
from django.shortcuts import render

from .models import Job
def main(request):
    # Efficient querying: fetch limited data for featured sections
    latest_jobs = Job.objects.all().order_by('-posted_on')[:5]
    top_companies = Company.objects.all()[:5]
    context = {
   }
    return render(request, 'main.html', context)

def contact(request):
    return render(request, 'jobs/contact.html')

def login_view(request):
    """Login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'Jobs/login.html')

def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('main')

def contact(request):
    """Contact page view"""
    return render(request, 'Jobs/contact.html')

def post_job(request):
    """Post job view"""
    return render(request, 'Jobs/post_job.html')


def view_applications(request):
    """View applications"""
    return render(request, 'view_applications.html')


@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            return redirect('recruiter_dashboard')
    else:
        form = JobForm()
    return render(request, 'jobs/post_job.html', {'form': form})


def job_list(request):
    """Contact page view"""
    return render(request, 'Jobs/job_list.html')