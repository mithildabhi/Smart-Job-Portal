from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
import json

# ✅ FIXED: Correct imports
from .models import Job, JobApplication, JobBookmark
from .forms import JobApplicationForm, JobForm
from companies.models import Company

def main(request):
    """Main page with featured jobs and companies"""
    # ✅ FIXED: Use created_at instead of posted_on
    latest_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:5]
    top_companies = Company.objects.all()[:5]
    
    context = {
        'latest_jobs': latest_jobs,
        'top_companies': top_companies,
    }
    return render(request, 'main.html', context)

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


@login_required
def post_job(request):
    """Post a new job and redirect to manage jobs"""
    try:
        company = Company.objects.get(user=request.user)
        
        if request.method == 'POST':
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description')
            location = request.POST.get('location')
            job_type = request.POST.get('job_type', 'full_time')
            salary = request.POST.get('salary')
            requirements = request.POST.get('requirements')
            deadline = request.POST.get('deadline')
            
            # Validate required fields
            if not all([title, description, location, deadline]):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'jobs/post_job.html', {'company': company})
            
            # Create new job
            job = Job.objects.create(
                company=company,
                title=title,
                description=description,
                location=location,
                job_type=job_type,
                salary=salary,
                requirements=requirements,
                deadline=deadline,
                is_active=True
            )
            
            messages.success(request, f'Job "{title}" posted successfully!')
            return redirect('companies:manage_jobs')  # Redirect to manage jobs
            
        context = {'company': company}
        return render(request, 'jobs/post_job.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_dashboard')
    
def job_list(request):
    """Public job listings for students"""
    jobs = Job.objects.filter(is_active=True).select_related('company').annotate(
        applications_count=Count('applications')  # ✅ FIXED: Use 'applications' related name
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(company__company_name__icontains=search_query) |
            Q(required_skills__icontains=search_query)
        )
    
    # Filter by location
    location = request.GET.get('location')
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    # Filter by job type
    job_type = request.GET.get('job_type')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    # Pagination
    paginator = Paginator(jobs, 12)  # 12 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get applied jobs for current user
    applied_jobs = []
    if request.user.is_authenticated:
        applied_jobs = JobApplication.objects.filter(
            student=request.user
        ).values_list('job_id', flat=True)
    
    context = {
        'jobs': page_obj,
        'applied_jobs': applied_jobs,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'jobs/job_list.html', context)

@login_required
def apply_job(request):
    """Handle job application submission"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        job_id = request.POST.get('job_id')
        job = get_object_or_404(Job, id=job_id, is_active=True)
        
        # Check if already applied
        if JobApplication.objects.filter(student=request.user, job=job).exists():
            return JsonResponse({
                'success': False,
                'message': 'You have already applied for this job.'
            })
        
        # Create application
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user
            application.job = job
            application.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully applied for {job.title} at {job.company.company_name}!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below.',
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def job_detail(request, job_id):
    """Job detail page"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if user already applied
    has_applied = False
    if request.user.is_authenticated:
        has_applied = JobApplication.objects.filter(
            student=request.user, 
            job=job
        ).exists()
    
    context = {
        'job': job,
        'has_applied': has_applied,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def bookmark_job(request):
    """Toggle job bookmark status"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        job_id = data.get('job_id')
        
        job = get_object_or_404(Job, id=job_id)
        bookmark, created = JobBookmark.objects.get_or_create(
            student=request.user,
            job=job
        )
        
        if not created:
            # Bookmark exists, remove it
            bookmark.delete()
            bookmarked = False
            message = 'Bookmark removed'
        else:    
            # New bookmark created
            bookmarked = True
            message = 'Job bookmarked!'
        
        return JsonResponse({
            'success': True,
            'bookmarked': bookmarked,
            'message': message
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def edit_job(request, job_id):
    """Edit existing job"""
    try:
        company = Company.objects.get(user=request.user)
        job = get_object_or_404(Job, id=job_id, company=company)
        
        if request.method == 'POST':
            form = JobForm(request.POST, instance=job)
            if form.is_valid():
                form.save()
                messages.success(request, 'Job updated successfully!')
                return redirect('jobs:manage_jobs')
        else:
            form = JobForm(instance=job)
        
        context = {
            'job': job,
            'form': form,
            'company': company,
        }
        return render(request, 'jobs/edit_job.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')

@login_required
def delete_job(request, job_id):
    """Delete job"""
    try:
        company = Company.objects.get(user=request.user)
        job = get_object_or_404(Job, id=job_id, company=company)
        
        if request.method == 'POST':
            job_title = job.title
            job.delete()
            messages.success(request, f'Job "{job_title}" deleted successfully!')
            return redirect('jobs:manage_jobs')
        
        context = {
            'job': job,
            'company': company,
        }
        return render(request, 'jobs/confirm_delete.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')

@login_required
def toggle_job_status(request, job_id):
    """Toggle job active status"""
    try:
        company = Company.objects.get(user=request.user)
        job = get_object_or_404(Job, id=job_id, company=company)
        job.is_active = not job.is_active
        job.save()
        
        status_text = 'activated' if job.is_active else 'deactivated'
        return JsonResponse({
            'success': True,
            'is_active': job.is_active,
            'message': f'Job {status_text} successfully!'
        })
        
    except Company.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Company not found'})

@login_required
def view_applications(request, job_id=None):
    """View applications for company jobs"""
    try:
        company = Company.objects.get(user=request.user)
        
        if job_id:
            # View applications for specific job
            job = get_object_or_404(Job, id=job_id, company=company)
            applications = JobApplication.objects.filter(job=job).order_by('-applied_at')
            
            context = {
                'job': job,
                'applications': applications,
                'company': company,
            }
            return render(request, 'jobs/job_applications.html', context)
        else:
            # View all applications for company
            applications = JobApplication.objects.filter(
                job__company=company
            ).select_related('job', 'student').order_by('-applied_at')
            
            context = {
                'applications': applications,
                'company': company,
            }
            return render(request, 'jobs/all_applications.html', context)
            
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')

def job_search(request):
    """Advanced job search with filters"""
    jobs = Job.objects.filter(is_active=True).select_related('company')
    
    # Apply various filters
    search_query = request.GET.get('q', '')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(company__company_name__icontains=search_query)
        )
    
    # Additional filters
    location = request.GET.get('location')
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    job_type = request.GET.get('job_type')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    context = {
        'jobs': jobs,
        'search_query': search_query,
    }
    return render(request, 'jobs/job_search.html', context)

def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('main')

def aboutus(request):
    """About us page view"""
    return render(request, 'Jobs/aboutus.html')

def contactus(request):
    """Contact us page view"""
    return render(request, 'Jobs/contactus.html')
