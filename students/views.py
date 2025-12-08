from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import StudentProfile
from jobs.models import Job, JobApplication
from .forms import ProfilePictureForm
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods  # ✅ Add this import

def student_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        
        # Server-side validation for password match
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            context = {
                'form_data': {
                    'username': username,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                }  
            }
            return render(request, 'students/student_register.html', context)
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'students/student_register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'students/student_register.html')
        
        try:
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            # ✅ ADD THIS: Create student profile
            from .models import StudentProfile
            StudentProfile.objects.create(user=user)
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('students:student_login')
            
        except Exception as e:
            messages.error(request, 'Registration failed. Please try again.')
            return render(request, 'students/student_register.html')
    
    return render(request, 'students/student_register.html')

def student_login(request):
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
            
            return render(request, 'students/student_login.html', context)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # ✅ NEW: Check if user is actually a student
            try:
                student_profile = StudentProfile.objects.get(user=user)
                
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('students:student_dashboard')
                else:
                    messages.error(request, 'Your account is disabled. Please contact support.')
                    context['login_error'] = True
                    
            except StudentProfile.DoesNotExist:
                # User exists but is NOT a student
                messages.error(request, 'This account is not registered as a student. Please use the company login.')
                context['login_error'] = True
        else:
            # Invalid credentials
            messages.error(request, 'Invalid username or password. Please try again.')
            context['login_error'] = True
    
    return render(request, 'students/student_login.html', context)

def student_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('jobs:main')

@login_required
@require_http_methods(["POST"])
def apply_job(request):
    """Handle AJAX job application submission"""
    
    try:
        # Get job ID
        job_id = request.POST.get('job_id')
        if not job_id:
            return JsonResponse({'success': False, 'message': 'Job ID missing'})
        
        # Get job
        job = get_object_or_404(Job, id=job_id)
        
        # Check if already applied
        existing = JobApplication.objects.filter(student=request.user, job=job).first()
        if existing:
            return JsonResponse({'success': False, 'message': 'Already applied for this job'})
        
        # Get form data
        cover_letter = request.POST.get('cover_letter', '').strip()
        resume = request.FILES.get('resume')
        portfolio_url = request.POST.get('portfolio_url', '').strip()
        
        # Basic validation
        if not cover_letter:
            return JsonResponse({'success': False, 'message': 'Cover letter is required'})
        
        if not resume:
            return JsonResponse({'success': False, 'message': 'Resume is required'})
        
        # Create application
        application = JobApplication.objects.create(
            student=request.user,
            job=job,
            cover_letter=cover_letter,
            resume=resume,
            portfolio_url=portfolio_url if portfolio_url else None
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully applied for {job.title}!'
        })
        
    except Exception as e:
        print(f"Apply job error: {e}")  # Debug print
        return JsonResponse({'success': False, 'message': 'Application failed'})


@login_required
@require_POST
def delete_student_account(request):
    """Ultra-simple delete for debugging"""
    
    try:
        student_name = request.user.username
        
        # Delete user (applications will cascade delete)
        request.user.delete()
        
        # Simple redirect
        return redirect('/')
        
    except Exception as e:
        print(f"Delete error: {e}")
        return redirect('students:student_dashboard')

@login_required
def student_dashboard(request):
    # Ensure only students can access student dashboard
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Access denied. Student profile required.')
        return redirect('students:student_login')
    
    context = {'profile': profile}
    return render(request, 'students/student_dashboard.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import StudentProfile

@login_required
def student_profile(request):
    # Load the existing profile. If it doesn't exist, raise 404 so you can spot it.
    profile = get_object_or_404(StudentProfile.objects.select_related('user'), user=request.user)

    context = {
        'profile': profile,
        'has_profile_picture': bool(profile.profile_picture and profile.profile_picture.name),
        # cache-buster so updated images show immediately in templates during dev
        'image_cache_bust': int(profile.updated_at.timestamp()) if getattr(profile, 'updated_at', None) else None,
    }
    return render(request, 'students/profile.html', context)

@login_required
def upload_profile_picture(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                # Delete old picture manually instead of using the method
                if profile.profile_picture:
                    try:
                        import os
                        if os.path.isfile(profile.profile_picture.path):
                            os.remove(profile.profile_picture.path)
                    except (ValueError, OSError):
                        pass  # File doesn't exist or can't be deleted
                
                form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Profile picture uploaded successfully!',
                    'image_url': profile.profile_picture.url,
                    'has_image': True
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
@require_POST
def delete_profile_picture(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    
    if profile.has_profile_picture():
        profile.delete_profile_picture()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Profile picture deleted successfully!',
                'has_image': False
            })
        else:
            messages.success(request, 'Profile picture deleted successfully!')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'No profile picture to delete.'
            })
        else:
            messages.info(request, 'No profile picture to delete.')
    
    return redirect('students:profile')
@login_required
def saved_jobs(request):
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Access denied. Student profile required.')
        return redirect('students:student_login')
    
    return render(request, 'students/saved_jobs.html')

@login_required
def student_applications(request):
    """View student's job applications"""
    # Get all applications for the current student
    applications = JobApplication.objects.filter(
        student=request.user
    ).select_related('job', 'job__company').order_by('-applied_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        applications = applications.filter(
            Q(job__title__icontains=search_query) |
            Q(job__company__company_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(applications, 10)  # 10 applications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    total_applications = applications.count()
    pending_applications = applications.filter(status='pending').count()
    shortlisted_applications = applications.filter(status='shortlisted').count()
    hired_applications = applications.filter(status='hired').count()
    rejected_applications = applications.filter(status='rejected').count()
    
    context = {
        'applications': page_obj,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'shortlisted_applications': shortlisted_applications,
        'hired_applications': hired_applications,
        'rejected_applications': rejected_applications,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'students/student_application.html', context)

@login_required  
def withdraw_application(request, application_id):
    """Withdraw a job application"""
    if request.method == 'POST':
        try:
            profile = StudentProfile.objects.get(user=request.user)
            application = get_object_or_404(JobApplication, 
                id=application_id, 
                student=profile,  # ✅ Now using student=profile correctly
                status='Pending'
            )
            
            application.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Application withdrawn successfully'
            })
            
        except StudentProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Student profile not found'
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

@login_required
@require_POST
def update_student_profile(request):
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Profile not found'}, status=404)

    # Read fields (accept both names for robustness)
    phone = request.POST.get('phone', '').strip()
    location = request.POST.get('location', '').strip()
    date_of_birth = request.POST.get('date_of_birth', '').strip()
    linkedin_url = request.POST.get('linkedin_url', '').strip()
    college_name = request.POST.get('college_name', '').strip() or request.POST.get('college', '').strip()
    email = request.POST.get('email', '').strip()

    # Update profile fields
    profile.phone = phone
    profile.location = location
    profile.linkedin_url = linkedin_url
    if date_of_birth:
        try:
            from django.utils.dateparse import parse_date
            profile.date_of_birth = parse_date(date_of_birth)
        except Exception:
            profile.date_of_birth = None
    profile.college_name = college_name
    profile.save()

    # Optionally update user email and name if provided
    user = request.user
    if email:
        user.email = email
        user.save()

    return JsonResponse({
        'success': True,
        'phone': profile.phone,
        'location': profile.location,
        'date_of_birth': profile.date_of_birth.isoformat() if profile.date_of_birth else '',
        'linkedin_url': profile.linkedin_url,
        'college_name': profile.college_name,
        'email': user.email,
    })


import json
 
@login_required
@require_POST
def update_skills(request):
    """
    Expects either:
    - form-data with 'skills' string (comma-separated), OR
    - JSON body: {"skills": ["Python", "Django", "React"]}
    Returns JSON with updated skills list.
    """
    try:
        # prefer JSON if content-type is application/json
        if request.content_type and 'application/json' in request.content_type:
            payload = json.loads(request.body.decode('utf-8') or '{}')
            skills_input = payload.get('skills', [])
            # skills_input should be a list; if a string, split it
            if isinstance(skills_input, str):
                skill_list = [s.strip() for s in skills_input.split(',') if s.strip()]
            else:
                skill_list = [str(s).strip() for s in skills_input]
        else:
            # fallback to form submission
            skills_raw = request.POST.get('skills', '')
            # If skills sent as CSV
            skill_list = [s.strip() for s in skills_raw.split(',') if s.strip()]

        profile = StudentProfile.objects.get(user=request.user)

        # Save
        profile.set_skills_list(skill_list)

        return JsonResponse({
            'success': True,
            'skills': profile.get_skills_list()
        })
    except StudentProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Profile not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
