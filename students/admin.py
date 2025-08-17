from django.contrib import admin
from .models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 
        'phone', 
        'location', 
        'college_name',    # ✅ Changed from 'college' 
        'degree',          # ✅ Changed from 'course'
        'graduation_year', # ✅ Added new field
        'created_at'
    ]
    
    list_filter = [
        'degree',          # ✅ Changed from 'course'
        'college_name',    # ✅ Changed from 'college' 
        'graduation_year', # ✅ Added new field
        'created_at',
        'location'
    ]
    
    search_fields = [
        'user__username', 
        'user__first_name', 
        'user__last_name',
        'user__email',
        'college_name',    # ✅ Changed from 'college'
        'degree',          # ✅ Changed from 'course'
        'location'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    # ✅ ADDED: Organized fieldsets for better admin interface
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'profile_picture')
        }),
        ('Personal Details', {
            'fields': ('phone', 'location', 'date_of_birth', 'bio')
        }),
        ('Academic Information', {
            'fields': ('college_name', 'degree', 'graduation_year', 'gpa')
        }),
        ('Professional Details', {
            'fields': ('skills', 'experience', 'projects', 'education')
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'github_url', 'portfolio_url')
        }),
        ('Documents', {
            'fields': ('resume',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
