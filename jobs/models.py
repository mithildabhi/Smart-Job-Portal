# jobs/models.py
from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=100)
    posted_on = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()
    salary = models.CharField(max_length=100, blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    job_type = models.CharField(max_length=50, default='full_time')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    applied_on = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.student.username} → {self.job.title}"

    