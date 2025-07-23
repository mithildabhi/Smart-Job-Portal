from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.

def home(request):
    return HttpResponse("Hello from the Students app!")

@login_required
def student_dashboard(request):
    return render(request, 'students/dashboard.html')

@login_required
def student_profile(request):
    return render(request, 'students/profile.html')