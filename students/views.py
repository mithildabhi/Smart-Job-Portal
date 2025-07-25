from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import StudentProfile
from jobs.models import Application
from .forms import ProfilePictureForm
from django.views.decorators.http import require_POST

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
def student_dashboard(request):
    # Ensure only students can access student dashboard
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Access denied. Student profile required.')
        return redirect('students:student_login')
    
    context = {'profile': profile}
    return render(request, 'students/student_dashboard.html', context)

@login_required
def student_profile(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    context = {
        'profile': profile,
        'has_profile_picture': bool(profile.profile_picture and profile.profile_picture.name),
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
    
    return redirect('students:student_profile')
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
    """Student view applications with filtering and live data"""
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Access denied. Student profile required.')
        return redirect('students:student_login')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    sort_filter = request.GET.get('sort', 'recent')
    
    # ✅ FIX: Use student=profile (now it should work)
    applications = Application.objects.filter(
        student=profile
    ).select_related('job__company').order_by('-applied_on')
    
    # Apply status filter
    if status_filter != 'all':
        applications = applications.filter(status=status_filter)
    
    # Apply sorting
    if sort_filter == 'oldest':
        applications = applications.order_by('applied_on')
    elif sort_filter == 'company':
        applications = applications.order_by('job__company__company_name')
    else:  # recent
        applications = applications.order_by('-applied_on')
    
    # Calculate statistics
    total_applications = Application.objects.filter(student=profile).count()
    pending_applications = Application.objects.filter(student=profile, status='Pending').count()
    shortlisted_applications = Application.objects.filter(student=profile, status='Shortlisted').count()
    interview_applications = Application.objects.filter(student=profile, status='Interviewed').count()
    
    context = {
        'profile': profile,
        'applications': applications,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'shortlisted_applications': shortlisted_applications,
        'interview_applications': interview_applications,
        'status_filter': status_filter,
        'sort_filter': sort_filter,
    }
    
    return render(request, 'students/student_applications.html', context)

@login_required  
def withdraw_application(request, application_id):
    """Withdraw a job application"""
    if request.method == 'POST':
        try:
            profile = StudentProfile.objects.get(user=request.user)
            application = get_object_or_404(Application, 
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
