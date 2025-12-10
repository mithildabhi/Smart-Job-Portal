# companies/views.py - Complete imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from django.core.paginator import Paginator
from django.db.models import Q, Count
import os
from datetime import timedelta
import json
from django.views.decorators.http import require_POST

from jobs.models import Job, JobApplication  # From jobs app
from .models import Company               # Local companies app
from students.models import StudentProfile  # Import StudentProfile model
from django.views.decorators.http import require_http_methods




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
  
@login_required
@require_POST
def upload_company_logo(request):
    """Handle company logo upload"""
    try:
        company = Company.objects.get(user=request.user)
        
        if 'logo' in request.FILES:
            # Delete old logo if exists
            if company.logo:
                if os.path.isfile(company.logo.path):
                    os.remove(company.logo.path)
            
            # Save new logo
            company.logo = request.FILES['logo']
            company.save()
            
            messages.success(request, 'Company logo updated successfully!')
        else:
            messages.error(request, 'No logo file provided.')
            
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
    except Exception as e:
        messages.error(request, f'Error uploading logo: {str(e)}')
    
    return redirect('companies:company_profile')

@login_required
@require_POST
def update_company_info(request):
    user = request.user
    company = getattr(user, 'company', None)
    if not company:
        return JsonResponse({'success': False, 'message': 'Company not found'})

    # Extract fields from POST
    company_name = request.POST.get('company_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    location = request.POST.get('location')
    industry = request.POST.get('industry')
    website = request.POST.get('website')

    # Validate and update fields (add your validation as needed)
    if company_name:
        company.company_name = company_name
    if phone is not None:
        company.phone = phone
    if location is not None:
        company.location = location
    if industry is not None:
        company.industry = industry
    if website is not None:
        company.website = website

    try:
        company.save()
        # Also update user email
        if email:
            user.email = email
            user.save()
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({
        'success': True,
        'company_name': company.company_name,
        'email': user.email,
        'phone': company.phone or '',
        'location': company.location or '',
        'industry': company.industry or '',
        'website': company.website or '',
    })


@login_required
@require_POST
def update_company_description(request):
    user = request.user
    company = getattr(user, 'company', None)
    if not company:
        return JsonResponse({'success': False, 'message': 'Company not found'})

    description = request.POST.get('description')
    if description is not None:
        company.description = description
        try:
            company.save()
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
        return JsonResponse({'success': True, 'description': company.description})

    return JsonResponse({'success': False, 'message': 'No description provided'})

@login_required
@require_POST
def delete_company_logo(request):
    """Handle company logo deletion"""
    try:
        company = Company.objects.get(user=request.user)
        
        if company.logo:
            # Delete file from filesystem
            if os.path.isfile(company.logo.path):
                os.remove(company.logo.path)
            
            # Remove from database
            company.logo = None
            company.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Logo removed successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No logo to remove.'
            })
            
    except Company.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Company profile not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error removing logo: {str(e)}'
        })
          
@login_required
def manage_jobs(request):
    """Enhanced job management with activate/deactivate/delete functionality"""
    try:
        company = Company.objects.get(user=request.user)
        jobs = Job.objects.filter(company=company).order_by('-created_at')
        
        # Handle job actions (activate/deactivate/delete)
        if request.method == 'POST':
            action = request.POST.get('action')
            job_id = request.POST.get('job_id')
            print("DEBUG POST RECEIVED:", request.POST)

            job = get_object_or_404(Job, id=job_id, company=company)
            print("BEFORE action:", job.id, job.title, "is_active=", job.is_active)

            if action == 'activate':
                job.is_active = True
                job.save()
                messages.success(request, f'Job "{job.title}" has been activated.')
            
            elif action == 'deactivate':
                job.is_active = False       # 👈 set to False for deactivate
                job.save()
                messages.success(request, f'Job "{job.title}" has been deactivated.')

            elif action == 'delete':
                job_title = job.title
                job.delete()
                messages.success(request, f'Job "{job_title}" has been deleted.')

            # Debug after save/delete
            if action in ['activate', 'deactivate']:
                job.refresh_from_db()
                print("AFTER action:", job.id, job.title, "is_active=", job.is_active)
            else:
                print(f"AFTER delete: job {job_id} deleted")

            return redirect('companies:manage_jobs')
        
        # Get statistics for each job
        job_stats = []
        for job in jobs:
            applications_count = JobApplication.objects.filter(job=job).count()
            recent_applications = JobApplication.objects.filter(job=job).order_by('-applied_at')[:3]
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
            'total_applications': sum(stat['applications_count'] for stat in job_stats),
        }
        return render(request, 'companies/manage_jobs.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')

@login_required
def toggle_job_status(request, job_id):
    """Toggle job active/inactive status"""
    try:
        company = Company.objects.get(user=request.user)
        job = get_object_or_404(Job, id=job_id, company=company)
        
        job.is_active = not job.is_active
        job.save()
        
        status = "activated" if job.is_active else "deactivated"
        messages.success(request, f'Job "{job.title}" has been {status}.')
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
    
    return redirect('companies:manage_jobs')

@login_required
def delete_job(request, job_id):
    """Delete a job posting"""
    try:
        company = Company.objects.get(user=request.user)
        job = get_object_or_404(Job, id=job_id, company=company)
        
        if request.method == 'POST':
            job_title = job.title
            job.delete()
            messages.success(request, f'Job "{job_title}" has been deleted.')
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
    
    return redirect('companies:manage_jobs')

    
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
    
@login_required
def company_dashboard(request):
    """Enhanced company dashboard with recruitment statistics"""
    try:
        company = Company.objects.get(user=request.user)
        
        # Get current date for calculations
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        # === RECRUITMENT STATISTICS ===
        total_jobs = Job.objects.filter(company=company).count()
        total_applications = JobApplication.objects.filter(job__company=company).count()
        
        interviews_scheduled = JobApplication.objects.filter(
            job__company=company,
            status__in=['interviewed', 'shortlisted']
        ).count()
        
        positions_filled = JobApplication.objects.filter(
            job__company=company,
            status='hired'
        ).count()
        
        active_jobs = Job.objects.filter(company=company, is_active=True).count()
        
        recent_applications = JobApplication.objects.filter(
            job__company=company,
            applied_at__gte=last_30_days
        ).count()
        
        # === RECENT ACTIVITIES ===
        recent_activities = []
        
        # Recent applications
        new_applications = JobApplication.objects.filter(
            job__company=company,
            applied_at__gte=last_7_days
        ).select_related('student', 'job').order_by('-applied_at')[:5]
        
        for app in new_applications:
            recent_activities.append({
                'type': 'application',
                'title': 'New application received',
                'description': f'{app.student.get_full_name() or app.student.username} applied for {app.job.title}',
                'time': app.applied_at,
                'icon': 'fas fa-user-plus',
                'color': 'primary'
            })
        
        # Sort activities by time
        recent_activities.sort(key=lambda x: x['time'], reverse=True)
        recent_activities = recent_activities[:8]
        
        # Additional metrics
        total_apps = JobApplication.objects.filter(job__company=company).count()
        responded_apps = JobApplication.objects.filter(
            job__company=company
        ).exclude(status='pending').count()
        
        response_rate = round((responded_apps / total_apps * 100) if total_apps > 0 else 0, 1)
        
        context = {
            'company': company,
            'user': request.user,
            
            # Recruitment Statistics
            'total_jobs': total_jobs,
            'total_applications': total_applications,
            'interviews_scheduled': interviews_scheduled,
            'positions_filled': positions_filled,
            'active_jobs': active_jobs,
            'recent_applications': recent_applications,
            'response_rate': response_rate,
            
            # Recent Activities
            'recent_activities': recent_activities,
        }
        
        return render(request, 'companies/company_dashboard.html', context)
        
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('companies:company_register')

@login_required
def view_applications(request):
    """
    List + filter + paginate applications.  
    Each application gets a .skills_list attribute so the template never
    needs a custom filter.
    """
    company = get_object_or_404(Company, user=request.user)

    qs = JobApplication.objects.filter(job__company=company) \
                               .select_related("job", "student") \
                               .prefetch_related("student__studentprofile") \
                               .order_by("-applied_at")

    # ── filters ───────────────────────────────────────────────────────────
    job_filter    = request.GET.get("job_filter", "all")
    status_filter = request.GET.get("status_filter", "all")
    search        = request.GET.get("search", "").strip()

    if job_filter != "all":
        qs = qs.filter(job_id=job_filter)

    if status_filter != "all":
        qs = qs.filter(status=status_filter)

    if search:
        qs = qs.filter(
            Q(student__first_name__icontains=search)  |
            Q(student__last_name__icontains=search)   |
            Q(student__email__icontains=search)       |
            Q(job__title__icontains=search)
        )

    # ── enrich objects ───────────────────────────────────────────────────
    apps = []
    for app in qs:
        # guarantee profile object
        profile, _ = StudentProfile.objects.get_or_create(user=app.student)
        app.student.studentprofile = profile

        app.skills_list = [s.strip() for s in (profile.skills or "").split(",") if s.strip()]
        apps.append(app)

    # ── pagination ───────────────────────────────────────────────────────
    paginator  = Paginator(apps, 8)
    page_obj   = paginator.get_page(request.GET.get("page"))

    # ── quick stats ───────────────────────────────────────────────────────
    stats = {
        'total':        qs.count(),
        'pending':      qs.filter(status="pending").count(),
        'shortlisted':  qs.filter(status="shortlisted").count(),
        'hired':        qs.filter(status="hired").count(),
        'rejected':     qs.filter(status="rejected").count(),
    }

    context = dict(
        company           = company,
        applications      = page_obj,
        company_jobs      = Job.objects.filter(company=company).order_by("-created_at"),
        total_applications= stats['total'],
        pending_applications     = stats['pending'],
        shortlisted_applications = stats['shortlisted'],
        hired_applications       = stats['hired'],
        rejected_applications    = stats['rejected'],
        job_filter        = job_filter,
        status_filter     = status_filter,
        search_filter     = search,
        is_paginated      = page_obj.has_other_pages(),
        page_obj          = page_obj,
    )
    return render(request, "companies/view_applications.html", context)

@login_required
def application_detail(request, application_id):  # ✅ Changed parameter name
    """Get detailed application information via AJAX"""
    try:
        company = Company.objects.get(user=request.user)
        application = JobApplication.objects.select_related(
            'job', 
            'student'
        ).get(
            id=application_id,
            job__company=company
        )
        
        # Get student profile if exists
        student_profile = None
        try:
            student_profile = StudentProfile.objects.get(user=application.student)
        except StudentProfile.DoesNotExist:
            pass
        
        # Format the response data
        data = {
            'success': True,
            'application': {
                'id': application.id,
                'cover_letter': application.cover_letter,
                'resume': application.resume.url if application.resume else None,
                'portfolio_url': application.portfolio_url,
                'applied_date': application.applied_at.strftime('%B %d, %Y at %I:%M %p'),
                'status': application.status,
                'notes': getattr(application, 'notes', '') or '',
                'student': {
                    'name': application.student.get_full_name() or application.student.username,
                    'email': application.student.email,
                    'username': application.student.username,
                    'profile_picture': student_profile.profile_picture.url if (student_profile and student_profile.profile_picture) else None,
                    'profile': {
                        'bio': student_profile.bio if student_profile else None,
                        'education': student_profile.education if student_profile else None,
                        'experience': student_profile.experience if student_profile else None,
                        'skills': student_profile.skills if student_profile else None,
                        'projects': student_profile.projects if student_profile else None,
                        'phone': student_profile.phone if student_profile else None,
                        'location': student_profile.location if student_profile else None,
                    } if student_profile else None
                },
                'job': {
                    'title': application.job.title,
                    'company': application.job.company.company_name,
                    'location': application.job.location,
                    'job_type': application.job.get_job_type_display()
                }
            }
        }
        return JsonResponse(data)
        
    except (Company.DoesNotExist, JobApplication.DoesNotExist):
        return JsonResponse({
            'success': False, 
            'message': 'Application not found or access denied.'
        })


@login_required
def save_application_notes(request, application_id):  # ✅ Changed parameter name
    """Save internal notes for an application"""
    if request.method == 'POST':
        try:
            company = Company.objects.get(user=request.user)
            application = JobApplication.objects.get(
                id=application_id,
                job__company=company
            )
            
            data = json.loads(request.body)
            notes = data.get('notes', '')
            
            application.notes = notes
            application.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Notes saved successfully.'
            })
                
        except (Company.DoesNotExist, JobApplication.DoesNotExist):
            return JsonResponse({
                'success': False, 
                'message': 'Application not found or access denied.'
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid JSON data.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error saving notes: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required
def bulk_update_applications(request):
    """Bulk update multiple applications"""
    if request.method == 'POST':
        try:
            company = Company.objects.get(user=request.user)
            data = json.loads(request.body)
            
            application_ids = data.get('application_ids', [])
            new_status = data.get('status')
            
            if not application_ids or not new_status:
                return JsonResponse({
                    'success': False,
                    'message': 'Missing application IDs or status.'
                })
            
            # Update applications
            updated_count = JobApplication.objects.filter(
                id__in=application_ids,
                job__company=company
            ).update(
                status=new_status,
                reviewed_at=timezone.now()
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully updated {updated_count} applications to {new_status}.',
                'updated_count': updated_count
            })
            
        except Company.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Company not found.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating applications: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



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


@login_required
def get_application_statistics(request):
    """Get application statistics for dashboard charts"""
    try:
        company = Company.objects.get(user=request.user)
        
        # Monthly application trends
        monthly_stats = JobApplication.objects.filter(
            job__company=company,
            applied_at__gte=timezone.now() - timedelta(days=365)
        ).extra(
            select={'month': 'EXTRACT(month FROM applied_at)'}
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Status distribution
        status_stats = JobApplication.objects.filter(
            job__company=company
        ).values('status').annotate(
            count=Count('id')
        )
        
        return JsonResponse({
            'success': True,
            'monthly_stats': list(monthly_stats),
            'status_stats': list(status_stats)
        })
        
    except Company.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Company not found'
        })

@login_required
@require_http_methods(["POST"])
def update_application_status(request, application_id):  # ✅ Changed from 'pk' to 'application_id'
    """AJAX – change status from the board"""
    if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": False, "message": "Bad request"}, status=400)

    try:
        application = get_object_or_404(JobApplication, pk=application_id, job__company__user=request.user)
        data = json.loads(request.body or "{}")
        new_status = data.get("status")

        if new_status not in {"pending", "shortlisted", "interviewed", "hired", "rejected"}:
            return JsonResponse({"success": False, "message": "Invalid status"}, status=422)

        application.status = new_status
        application.reviewed_at = timezone.now()
        application.save(update_fields=["status", "reviewed_at"])

        # Status messages for better UX
        status_messages = {
            'pending': f'{application.student.get_full_name() or application.student.username} moved back to pending review',
            'shortlisted': f'{application.student.get_full_name() or application.student.username} has been shortlisted',
            'interviewed': f'Interview scheduled for {application.student.get_full_name() or application.student.username}',
            'hired': f'Congratulations! {application.student.get_full_name() or application.student.username} has been hired!',
            'rejected': f'Application from {application.student.get_full_name() or application.student.username} has been rejected'
        }

        return JsonResponse({
            "success": True,
            "message": status_messages.get(new_status, f"Status updated to {new_status.title()}"),
            "new_status": new_status,
            "application_id": application.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error updating status: {str(e)}"}, status=500)
