from django.contrib import admin
from .models import Job, JobApplication

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'job_type', 'created_at', 'deadline', 'is_active', 'applications_count']
    list_filter = ['job_type', 'is_active', 'created_at', 'company']
    search_fields = ['title', 'company__company_name', 'location', 'required_skills']
    readonly_fields = ['created_at', 'applications_count']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'title', 'description', 'location')
        }),
        ('Job Details', {
            'fields': ('job_type', 'experience_required', 'positions_available', 'required_skills')
        }),
        ('Salary Information', {
            'fields': ('salary_min', 'salary_max', 'salary'),
            'description': 'Use salary_min/max for filtering, or salary field for custom text'
        }),
        ('Requirements & Timeline', {
            'fields': ('requirements', 'deadline')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def applications_count(self, obj):
        return obj.applications.count()
    applications_count.short_description = 'Applications'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'job_title', 'company_name', 'status', 'applied_at', 'reviewed_at']
    list_filter = ['status', 'applied_at', 'job__company', 'job__job_type']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 
                    'job__title', 'job__company__company_name']
    readonly_fields = ['applied_at', 'days_since_applied']
    date_hierarchy = 'applied_at'
    
    fieldsets = (
        ('Application Details', {
            'fields': ('job', 'student', 'applied_at', 'days_since_applied')
        }),
        ('Application Content', {
            'fields': ('cover_letter', 'resume', 'portfolio_url')
        }),
        ('Review Status', {
            'fields': ('status', 'reviewed_at', 'reviewed_by', 'notes')
        }),
    )
    
    def student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username
    student_name.short_description = 'Student'
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job'
    
    def company_name(self, obj):
        return obj.job.company.company_name
    company_name.short_description = 'Company'
    
    def days_since_applied(self, obj):
        return f"{obj.days_since_applied} days ago"
    days_since_applied.short_description = 'Applied'


