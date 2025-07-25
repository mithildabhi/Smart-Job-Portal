from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=100)
    posted_on = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()
    salary = models.CharField(max_length=100, blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default='full_time')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-posted_on']

class Application(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),           # ✅ Changed to match template
        ('Shortlisted', 'Shortlisted'),   # ✅ Added for better workflow
        ('Rejected', 'Rejected'),         # ✅ Changed to match template
        ('Interviewed', 'Interviewed'),   # ✅ Added for interview stage
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    
    # ✅ FIXED: Use StudentProfile instead of User directly
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='applications')
    
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)  # ✅ Made optional
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # ✅ ADDED: Cover letter field for applications
    cover_letter = models.TextField(blank=True, null=True)
    
    # ✅ ADDED: Prevent duplicate applications
    class Meta:
        unique_together = ['student', 'job']
        ordering = ['-applied_on']

    def __str__(self):
        return f"{self.student.user.username} → {self.job.title}"
