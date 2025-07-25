# companies/views.py - Complete imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
import json

# Import models from correct apps
from jobs.models import Job, Application  # Job models from jobs app
from .models import Company                # Company model from local companies app




def company_register(request):
    """Company registration with proper user type separation"""
    if request.method == 'POST':
        # Get form data
        company_name = request.POST.get('company_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        industry = request.POST.get('industry')
        website = request.POST.get('website', '')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Preserve form data for error cases
        context = {'form_data': request.POST}
        
        # Validation
        if not all([company_name, username, email, phone, industry, password1, password2]):
            messages.error(request, 'All required fields must be filled')
            return render(request, 'companies/company_register.html', context)
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'companies/company_register.html', context)
        
        if len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters long')
            return render(request, 'companies/company_register.html', context)
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'companies/company_register.html', context)
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'companies/company_register.html', context)
        
        try:
            # Create user account
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=company_name
            )
            
            # ✅ Create company profile (ensures proper user type separation)
            company = Company.objects.create(
                user=user,
                company_name=company_name,
                industry=industry,
                phone=phone,
                website=website if website else None
            )
            
            messages.success(request, f'Registration successful for {company_name}! Please login with your credentials.')
            return redirect('companies:company_login')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'companies/company_register.html', context)
    
    return render(request, 'companies/company_register.html')

def company_login(request):
    """Company login view with strict user type validation"""
    context = {}
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Preserve username for form repopulation
        context['username'] = username
        
        # Server-side validation for empty fields
        if not username or not password:
            if not username and not password:
                messages.error(request, 'Please enter both username and password')
            elif not username:
                messages.error(request, 'Please enter your username')
            else:
                messages.error(request, 'Please enter your password')
            
            return render(request, 'companies/company_login.html', context)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # ✅ STRICT: Check if user is actually a company
            try:
                company = Company.objects.get(user=user)
                
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {company.company_name}!')
                    return redirect('companies:company_dashboard')
                else:
                    messages.error(request, 'Your account is disabled. Please contact support.')
                    context['login_error'] = True
                    
            except Company.DoesNotExist:
                # User exists but is NOT a company
                messages.error(request, 'This account is not registered as a company. Please use the student login.')
                context['login_error'] = True
                
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            context['login_error'] = True
    
    return render(request, 'companies/company_login.html', context)

# companies/views.py
@login_required
def post_job(request):
    """Post a new job using company field"""
    if request.method == 'POST':
        try:
            company = Company.objects.get(user=request.user)
            
            # ✅ FIXED: Create job with company, not recruiter
            job = Job.objects.create(
                title=request.POST['title'],
                description=request.POST['description'],
                company=company,  # ← Use company instead of recruiter
                location=request.POST['location'],
                salary=request.POST.get('salary', ''),
                requirements=request.POST.get('requirements', ''),
                job_type=request.POST.get('job_type', 'full_time'),
                deadline=request.POST.get('deadline'),
                is_active=True
            )
            
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect('companies:manage_jobs')
            
        except Company.DoesNotExist:
            messages.error(request, 'Company profile not found.')
            return redirect('companies:company_register')
    
    try:
        company = Company.objects.get(user=request.user)
        return render(request, 'companies/post_job.html', {'company': company})
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')
# companies/views.py
@login_required
def job_list(request):
    """Display all jobs posted by the company"""
    try:
        company = Company.objects.get(user=request.user)
        jobs = Job.objects.filter(company=company).order_by('-posted_on')
        
        # Get statistics for each job
        job_stats = []
        for job in jobs:
            applications_count = Application.objects.filter(job=job).count()
            job_stats.append({
                'job': job,
                'applications_count': applications_count,
            })
        
        context = {
            'company': company,
            'job_stats': job_stats,
            'total_jobs': jobs.count(),
            'active_jobs': jobs.filter(is_active=True).count(),
        }
        return render(request, 'companies/job_list.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')
    
# companies/views.py - Updated to work with your current models

@login_required
def manage_jobs(request):
    """Manage jobs using recruiter field instead of company"""
    try:
        company = Company.objects.get(user=request.user)
        # Filter jobs by recruiter (which is the company user)
        jobs = Job.objects.filter(recruiter=request.user).order_by('-posted_on')
        
        if request.method == 'POST':
            action = request.POST.get('action')
            job_id = request.POST.get('job_id')
            
            try:
                job = get_object_or_404(Job, id=job_id, recruiter=request.user)
                
                if action == 'activate':
                    job.is_active = True  # You'll need to add this field
                    job.save()
                    messages.success(request, f'Job "{job.title}" activated successfully!')
                elif action == 'deactivate':
                    job.is_active = False
                    job.save()
                    messages.success(request, f'Job "{job.title}" deactivated successfully!')
                elif action == 'delete':
                    job_title = job.title
                    job.delete()
                    messages.success(request, f'Job "{job_title}" deleted successfully!')
                    
            except Job.DoesNotExist:
                messages.error(request, 'Job not found.')
                
            return redirect('companies:manage_jobs')
        
        # Get statistics for each job
        job_stats = []
        for job in jobs:
            applications_count = Application.objects.filter(job=job).count()
            recent_applications = Application.objects.filter(job=job).order_by('-applied_on')[:3]
            job_stats.append({
                'job': job,
                'applications_count': applications_count,
                'recent_applications': recent_applications,
            })
        
        context = {
            'company': company,
            'job_stats': job_stats,
            'total_jobs': jobs.count(),
            'active_jobs': jobs.filter(is_active=True).count() if hasattr(Job, 'is_active') else jobs.count(),
            'inactive_jobs': jobs.count() - jobs.filter(is_active=True).count() if hasattr(Job, 'is_active') else 0,
            'total_applications': sum([stat['applications_count'] for stat in job_stats])
        }
        return render(request, 'companies/manage_jobs.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')

@login_required
def view_applications(request):
    """View applications using company field"""
    try:
        company = Company.objects.get(user=request.user)
        
        # ✅ FIXED: Filter by company instead of recruiter
        company_jobs = Job.objects.filter(company=company)
        
        # Get applications for those jobs
        applications = Application.objects.filter(
            job__in=company_jobs
        ).order_by('-applied_on')
        
        # Group applications by job
        jobs_with_applications = []
        for job in company_jobs:
            job_applications = applications.filter(job=job)
            if job_applications.exists():
                jobs_with_applications.append({
                    'job': job,
                    'applications': job_applications,
                    'application_count': job_applications.count(),
                })
        
        context = {
            'company': company,
            'applications': applications,
            'jobs_with_applications': jobs_with_applications,
            'company_jobs': company_jobs,
            'total_applications': applications.count(),
        }
        return render(request, 'companies/view_applications.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')




@login_required
def company_dashboard(request):
    """Company dashboard with user type protection"""
    try:
        company = Company.objects.get(user=request.user)
        
        # ✅ FIX: Use 'company' field instead of 'recruiter'
        total_jobs = Job.objects.filter(company=company).count()
        active_jobs = Job.objects.filter(company=company, is_active=True).count()
        inactive_jobs = Job.objects.filter(company=company, is_active=False).count()
        
        # Get recent applications for company jobs
        recent_applications = Application.objects.filter(
            job__company=company
        ).order_by('-applied_on')[:5]
        
        # Get total applications count
        total_applications = Application.objects.filter(job__company=company).count()
        
        context = {
            'company': company,
            'user': request.user,
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'inactive_jobs': inactive_jobs,
            'recent_applications': recent_applications,
            'total_applications': total_applications,
        }
        return render(request, 'companies/company_dashboard.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Access denied. Company profile required.')
        return redirect('companies:company_login')

@login_required
def company_profile(request):
    """Display company profile"""
    try:
        company = Company.objects.get(user=request.user)
        context = {
            'company': company,
            'user': request.user,
        }
        return render(request, 'companies/company_profile.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')

    
# companies/views.py

@login_required
def manage_jobs(request):
    """Enhanced job management with activate/deactivate/delete functionality"""
    try:
        company = Company.objects.get(user=request.user)
        # ✅ FIXED: Use company instead of recruiter
        jobs = Job.objects.filter(company=company).order_by('-posted_on')
        
        # Handle job actions (activate/deactivate/delete)
        if request.method == 'POST':
            action = request.POST.get('action')
            job_id = request.POST.get('job_id')
            
            try:
                # ✅ FIXED: Filter by company instead of recruiter
                job = get_object_or_404(Job, id=job_id, company=company)
                
                if action == 'activate':
                    job.is_active = True
                    job.save()
                    messages.success(request, f'Job "{job.title}" activated successfully!')
                elif action == 'deactivate':
                    job.is_active = False
                    job.save()
                    messages.success(request, f'Job "{job.title}" deactivated successfully!')
                elif action == 'delete':
                    job_title = job.title
                    job.delete()
                    messages.success(request, f'Job "{job_title}" deleted successfully!')
                    
            except Job.DoesNotExist:
                messages.error(request, 'Job not found.')
                
            return redirect('companies:manage_jobs')
        
        # Get statistics for each job
        job_stats = []
        for job in jobs:
            applications_count = Application.objects.filter(job=job).count()
            recent_applications = Application.objects.filter(job=job).order_by('-applied_on')[:3]
            job_stats.append({
                'job': job,
                'applications_count': applications_count,
                'recent_applications': recent_applications,
            })
        
        context = {
            'company': company,
            'job_stats': job_stats,
            'total_jobs': jobs.count(),
            'active_jobs': jobs.filter(is_active=True).count(),
            'inactive_jobs': jobs.filter(is_active=False).count(),
            'total_applications': sum([stat['applications_count'] for stat in job_stats])
        }
        return render(request, 'companies/manage_jobs.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')

    
    # Get statistics for each job
    job_stats = []
    for job in jobs:
        applications_count = Application.objects.filter(job=job).count()
        recent_applications = Application.objects.filter(job=job).order_by('-applied_on')[:3]
        job_stats.append({
            'job': job,
            'applications_count': applications_count,
            'recent_applications': recent_applications,
        })
    
    context = {
        'company': company,
        'job_stats': job_stats,
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(is_active=True).count() if hasattr(Job, 'is_active') else jobs.count(),
        'inactive_jobs': jobs.count() - jobs.filter(is_active=True).count() if hasattr(Job, 'is_active') else 0,
        'total_applications': sum([stat['applications_count'] for stat in job_stats])
    }
    return render(request, 'companies/manage_jobs.html', context)
@login_required
def view_applications(request):
    """View all applications for company jobs with filtering and status management"""
    try:
        company = Company.objects.get(user=request.user)
        
        # Get filter parameters
        job_filter = request.GET.get('job', 'all')
        status_filter = request.GET.get('status', 'all')
        
        # Get all jobs posted by this company
        company_jobs = Job.objects.filter(company=company)
        
        # Filter applications based on parameters
        applications = Application.objects.filter(job__in=company_jobs).order_by('-applied_on')
        
        if job_filter != 'all':
            applications = applications.filter(job_id=job_filter)
            
        if status_filter != 'all' and hasattr(Application, 'status'):
            applications = applications.filter(status=status_filter)
        
        # Group applications by job for better organization
        jobs_with_applications = []
        for job in company_jobs:
            job_applications = applications.filter(job=job)
            if job_applications.exists():
                jobs_with_applications.append({
                    'job': job,
                    'applications': job_applications,
                    'application_count': job_applications.count(),
                    'pending_count': job_applications.filter(status='pending').count() if hasattr(Application, 'status') else 0,
                    'accepted_count': job_applications.filter(status='accepted').count() if hasattr(Application, 'status') else 0,
                })
        
        # Get statistics
        total_applications = applications.count()
        pending_applications = applications.filter(status='pending').count() if hasattr(Application, 'status') else total_applications
        accepted_applications = applications.filter(status='accepted').count() if hasattr(Application, 'status') else 0
        rejected_applications = applications.filter(status='rejected').count() if hasattr(Application, 'status') else 0
        
        context = {
            'company': company,
            'applications': applications,
            'jobs_with_applications': jobs_with_applications,
            'company_jobs': company_jobs,
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'accepted_applications': accepted_applications,
            'rejected_applications': rejected_applications,
            'job_filter': job_filter,
            'status_filter': status_filter,
        }
        return render(request, 'companies/view_applications.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')

@login_required
def update_application_status(request):
    """Update application status via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            application_id = data.get('application_id')
            status = data.get('status')
            
            # Verify company owns this application
            company = Company.objects.get(user=request.user)
            application = get_object_or_404(Application, 
                id=application_id,
                job__company=company
            )
            
            # Update status if Application model has status field
            if hasattr(application, 'status'):
                application.status = status
                application.save()
                
                # Send email notification to applicant (optional)
                messages.success(request, f'Application status updated to {status}')
                return JsonResponse({
                    'success': True,
                    'message': f'Application status updated to {status}'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': 'Status field not available'
                })
                
        except (Company.DoesNotExist, Application.DoesNotExist):
            return JsonResponse({
                'success': False, 
                'error': 'Application not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method'
    })

def company_logout(request):
    """Company logout view"""
    if request.user.is_authenticated:
        try:
            company = Company.objects.get(user=request.user)
            company_name = company.company_name
        except Company.DoesNotExist:
            company_name = request.user.username
        
        logout(request)
        messages.success(request, f'Goodbye {company_name}! You have been logged out successfully.')
    
    return redirect('jobs:main')

# companies/views.py

@login_required
def delete_company_account(request):
    """Delete company account with confirmation"""
    try:
        company = Company.objects.get(user=request.user)
        
        if request.method == 'POST':
            # Get confirmation from POST data
            confirmation = request.POST.get('confirm_delete')
            
            if confirmation == 'confirmed':
                # Store company name for farewell message
                company_name = company.company_name
                user = request.user
                
                # Delete the company (this will also delete related jobs due to CASCADE)
                company.delete()
                
                # Delete the user account
                user.delete()
                
                # Add success message
                messages.success(request, f'Company account for {company_name} has been permanently deleted. Thank you for using Smart Job Portal.')
                return redirect('jobs:main')  # Redirect to home page
            else:
                messages.error(request, 'Account deletion was cancelled.')
                return redirect('companies:company_dashboard')
        
        # For GET request, show confirmation page
        context = {
            'company': company,
        }
        return render(request, 'companies/delete_account_confirm.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_dashboard')
