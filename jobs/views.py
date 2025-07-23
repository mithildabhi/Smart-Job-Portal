from django.shortcuts import render
from django .http import HttpResponse
from django.template import loader
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Job, Application
from .forms import JobForm, StatusUpdateForm

def main(request):
    template = loader.get_template('templates/Jobs/main.html')
    return HttpResponse(template.render()) 


@login_required
def recruiter_dashboard(request):
    jobs = Job.objects.filter(recruiter=request.user)
    return render(request, 'jobs/recruiter_dashboard.html', {'jobs': jobs})

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

@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applications = Application.objects.filter(job=job)
    return render(request, 'jobs/applicants.html', {'job': job, 'applications': applications})

@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect('view_applicants', job_id=application.job.id)
    else:
        form = StatusUpdateForm(instance=application)
    return render(request, 'jobs/update_status.html', {'form': form})

