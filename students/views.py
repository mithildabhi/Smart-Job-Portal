from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def student_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'students/student_register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'students/student_register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'students/student_register.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        # Create student profile (you'll need to define this model)
        # StudentProfile.objects.create(user=user)
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('students:student_login')
    
    return render(request, 'students/student_register.html')

def student_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('students:student_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'students/student_login.html')

def student_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('jobs:main')

@login_required
def student_dashboard(request):
    return render(request, 'students/student_dashboard.html')

@login_required
def student_profile(request):
    return render(request, 'students/profile.html')

@login_required
def saved_jobs(request):
    return render(request, 'students/profile.html')


@login_required
def student_applications(request):
    return render(request, 'students/profile.html')
