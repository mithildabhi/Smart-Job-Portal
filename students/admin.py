from django.contrib import admin
from .models import StudentProfile, Student

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user' ,'phone', 'location', 'college', 'course']
    list_filter = ['course', 'college', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

# @admin.register(Student)
# class StudentAdmin(admin.ModelAdmin):
#     list_display = ['name', 'email']
#     search_fields = ['name', 'email']
