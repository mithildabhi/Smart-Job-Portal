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

from .supabase_storage import upload_profile_picture as supabase_upload_profile_picture

@login_required
def upload_profile_picture_view(request):
    """
    POST endpoint: '/students/profile/upload-picture/'
    Expects multipart/form-data with field name 'profile_picture'.
    Returns JSON.
    """
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    # DEBUG: uncomment to log what's in request.FILES
    # print("FILES keys:", list(request.FILES.keys()))
    uploaded_file = request.FILES.get('profile_picture')  # <- IMPORTANT: use request.FILES

    if not uploaded_file:
        # If no file present, return a readable JSON error (avoid 500)
        return JsonResponse({'success': False, 'message': 'No file provided in request.FILES with key "profile_picture".'}, status=400)

    try:
        # Upload (this will call supabase_storage.upload_profile_picture and return a URL or path)
        public_url = supabase_upload_profile_picture(uploaded_file, bucket='public', user_path=f'users/{request.user.id}')

        # Save the resulting URL/path into the profile model
        profile, created = StudentProfile.objects.get_or_create(user=request.user)
        # If your model uses a URLField named 'profile_picture_url', use that:
        if hasattr(profile, 'profile_picture_url'):
            profile.profile_picture_url = public_url
        else:
            # fallback: try to set profile_picture (if it's a CharField/URLField)
            try:
                profile.profile_picture = public_url
            except Exception:
                # last resort: attach as an attribute (not recommended)
                profile.profile_picture_url = public_url
        profile.save()

        return JsonResponse({'success': True, 'image_url': public_url})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

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
from django.http import JsonResponse, HttpResponseBadRequest

@login_required
@require_POST
def update_skills(request):
    """
    Accepts payload:
      {"skills": ["python", "django"]}   OR
      {"skills": [{"name":"python"}, {"name":"django", "percent": 0}]}

    Saves only names (backwards compatible). Returns:
      { "success": True, "skills": [{"name":"python"}, ...] }
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    incoming = data.get('skills', [])
    if not isinstance(incoming, list):
        return HttpResponseBadRequest('skills must be a list')

    # Normalize to a list of names (strings)
    names = []
    for item in incoming:
        if isinstance(item, str):
            n = item.strip()
            if n:
                names.append(n)
        elif isinstance(item, dict):
            n = str(item.get('name', '')).strip()
            if n:
                names.append(n)
        else:
            # ignore unexpected types
            continue

    # get profile
    profile = getattr(request.user, 'studentprofile', None)
    if profile is None:
        return JsonResponse({'success': False, 'message': 'Profile not found'}, status=404)

    # Save names (use model helper if available, else write to field)
    if hasattr(profile, 'set_skills_list') and callable(profile.set_skills_list):
        profile.set_skills_list(names)
    else:
        profile.skills = ', '.join(names)
        profile.save()

    # Return normalized server-side representation
    resp = [{'name': n} for n in names]
    return JsonResponse({'success': True, 'skills': resp})


@login_required
@require_POST
def update_education(request):
    """
    AJAX endpoint to update education list.
    Expects JSON body: { "education": [ {degree,institute,start_year,end_year,cgpa,description}, ... ] }

    Validation:
      - 'education' must be a list
      - Each item must be a dict
      - cgpa, if provided, must be numeric
      - At most 2 education entries allowed
      - (currently requires at least 1; change to 2 if you want strict minimum 2)
    """
    import json
    from django.http import JsonResponse, HttpResponseBadRequest

    try:
        data = json.loads(request.body.decode('utf-8'))
        edu = data.get('education', [])
        if not isinstance(edu, list):
            return HttpResponseBadRequest('education must be a list')
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    # Normalize and validate entries
    cleaned = []
    for e in edu:
        if not isinstance(e, dict):
            # ignore non-dict entries
            continue
        degree = str(e.get('degree', '') or '').strip()
        institute = str(e.get('institute', '') or '').strip()
        description = str(e.get('description', '') or '').strip()
        start_year = str(e.get('start_year', '') or '').strip()
        end_year = str(e.get('end_year', '') or '').strip()
        cgpa_raw = e.get('cgpa', '')
        cgpa = str(cgpa_raw).strip() if cgpa_raw is not None else ''

        # Validate cgpa numeric if present (allow decimals)
        if cgpa:
            try:
                # allow numeric values like "8.5" or "8"
                _ = float(cgpa)
            except Exception:
                return JsonResponse({
                    'success': False,
                    'message': f'CGPA must be a number for entry "{degree or institute}".'
                }, status=400)

        # consider entry valid if degree or institute or description present
        if degree or institute or description:
            cleaned.append({
                'degree': degree,
                'institute': institute,
                'start_year': start_year,
                'end_year': end_year,
                'cgpa': cgpa,
                'description': description
            })

    # Enforce maximum 2 entries
    if len(cleaned) > 2:
        return JsonResponse({
            'success': False,
            'message': 'You can only save up to 2 education entries.'
        }, status=400)

    # Optionally enforce a minimum (currently requiring at least 1)
    if len(cleaned) < 1:
        return JsonResponse({
            'success': False,
            'message': 'Please add at least one education entry before saving.'
        }, status=400)

    profile = getattr(request.user, 'studentprofile', None)
    if profile is None:
        return JsonResponse({'success': False, 'message': 'Profile not found'}, status=404)

    # Save using model helper if available (recommended)
    if hasattr(profile, 'set_education_list') and callable(profile.set_education_list):
        profile.set_education_list(cleaned)
    else:
        try:
            profile.education = json.dumps(cleaned)
            profile.save()
        except Exception:
            return JsonResponse({'success': False, 'message': 'Could not save education'}, status=500)

    saved = profile.get_education_list() if hasattr(profile, 'get_education_list') else cleaned
    return JsonResponse({'success': True, 'education': saved})



@login_required
@require_POST
def update_experience(request):
    """
    Expects: { "experience": [ {title,company,start,end,duration,description}, ... ] }
    Enforces max 4 entries.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        incoming = data.get('experience', [])
        if not isinstance(incoming, list):
            return HttpResponseBadRequest('experience must be a list')
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    cleaned = []
    for e in incoming:
        if not isinstance(e, dict):
            continue
        title = str(e.get('title','') or '').strip()
        company = str(e.get('company','') or '').strip()
        start = str(e.get('start','') or '').strip()
        end = str(e.get('end','') or '').strip()
        duration = str(e.get('duration','') or '').strip()
        desc = str(e.get('description','') or '').strip()
        if title or company or desc:
            cleaned.append({
                'title': title, 'company': company, 'start': start, 'end': end,
                'duration': duration, 'description': desc
            })

    if len(cleaned) > 4:
        return JsonResponse({'success': False, 'message': 'You can only save up to 4 experience entries.'}, status=400)

    profile = getattr(request.user, 'studentprofile', None)
    if profile is None:
        return JsonResponse({'success': False, 'message': 'Profile not found'}, status=404)

    if hasattr(profile, 'set_experience_list') and callable(profile.set_experience_list):
        profile.set_experience_list(cleaned)
    else:
        profile.experience = json.dumps(cleaned)
        profile.save()

    saved = profile.get_experience_list() if hasattr(profile, 'get_experience_list') else cleaned
    return JsonResponse({'success': True, 'experience': saved})


@login_required
@require_POST
def update_projects(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        projects = data.get('projects', [])
        if not isinstance(projects, list):
            return HttpResponseBadRequest('projects must be a list')
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    profile = getattr(request.user, 'studentprofile', None)
    if not profile:
        return JsonResponse({'success': False, 'message': 'Profile not found'}, status=404)

    # enforce max 3
    if len(projects) > 3:
        return JsonResponse({'success': False, 'message': 'Max 3 projects allowed'}, status=400)

    # sanitize fields: trim and ensure strings
    cleaned = []
    for p in projects:
        title = (p.get('title','') if isinstance(p, dict) else str(p)).strip()
        tech = (p.get('technologies','') if isinstance(p, dict) else '').strip()
        start = (p.get('start','') if isinstance(p, dict) else '').strip()
        end = (p.get('end','') if isinstance(p, dict) else '').strip()
        desc = (p.get('description','') if isinstance(p, dict) else '').strip()
        cleaned.append({
            'title': title,
            'technologies': tech,
            'start': start,
            'end': end,
            'description': desc
        })

    # Save using your model helper - implement set_projects_list in StudentProfile
    profile.set_projects_list(cleaned)   # <-- add this helper in model
    saved = profile.get_projects_list()
    return JsonResponse({'success': True, 'projects': saved})
    