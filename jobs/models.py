from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()
    
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary = models.CharField(max_length=100, blank=True, null=True)
    
    requirements = models.TextField(blank=True, null=True)
    required_skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default='full_time')
    is_active = models.BooleanField(default=True)
    
    experience_required = models.CharField(max_length=100, blank=True, null=True)
    positions_available = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.title} at {self.company.company_name}"
    
    def get_absolute_url(self):
        return reverse('jobs:job_detail', kwargs={'job_id': self.id})
    
    # ✅ REMOVED: @property applications_count to avoid conflict with .annotate()
    # This prevents the "property has no setter" error
    
    @property 
    def is_expired(self):
        return self.deadline < timezone.now().date()
    
    @property
    def required_skills_list(self):
        """Convert comma-separated skills to list"""
        if self.required_skills:
            return [skill.strip() for skill in self.required_skills.split(',')]
        return []
    
    def save(self, *args, **kwargs):
        """Custom save method with proper date handling"""
        # ✅ FIXED: Handle deadline conversion if it's a string
        if self.deadline and isinstance(self.deadline, str):
            try:
                self.deadline = datetime.strptime(self.deadline, '%Y-%m-%d').date()
            except ValueError:
                # Let Django's form validation handle invalid dates
                pass
        
        # ✅ FIXED: Auto-deactivate expired jobs with safety check
        if self.deadline and hasattr(self.deadline, 'year'):
            if self.deadline < timezone.now().date():
                self.is_active = False
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('interviewed', 'Interviewed'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    
    cover_letter = models.TextField(help_text="Tell us why you're perfect for this role")
    resume = models.FileField(upload_to='applications/resumes/%Y/%m/', 
                             help_text="Upload PDF or Word document (Max 5MB)")
    portfolio_url = models.URLField(blank=True, null=True, 
                                   help_text="Link to your portfolio or website")
    
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                   blank=True, null=True, 
                                   related_name='reviewed_applications')
    notes = models.TextField(blank=True, null=True, 
                           help_text="Internal notes from recruiter")
    
    class Meta:
        unique_together = ['student', 'job']
        ordering = ['-applied_at']
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'

    def __str__(self):
        return f"{self.student.get_full_name() or self.student.username} → {self.job.title}"
    
    @property
    def days_since_applied(self):
        return (timezone.now() - self.applied_at).days
    
    def mark_as_reviewed(self, reviewer, status=None):
        """Mark application as reviewed"""
        self.reviewed_at = timezone.now()
        self.reviewed_by = reviewer
        if status:
            self.status = status
        self.save()


class JobBookmark(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarked_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='bookmarks')
    bookmarked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'job']
        ordering = ['-bookmarked_at']
    
    def __str__(self):
        return f"{self.student.username} bookmarked {self.job.title}"
