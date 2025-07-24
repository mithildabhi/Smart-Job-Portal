from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Company

# Company Inline for User Admin
class CompanyProfileInline(admin.StackedInline):
    model = Company
    can_delete = True
    verbose_name_plural = 'Company Profile'
    extra = 0

# Enhanced Company Admin
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'industry', 'phone', 'location', 'created_at']
    list_filter = ['industry', 'created_at', 'location']
    search_fields = ['company_name', 'user__username', 'user__email', 'phone']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Company Details', {
            'fields': ('company_name', 'industry', 'location', 'description')
        }),
        ('Contact Information', {
            'fields': ('phone', 'website')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    # Enable bulk deletion
    actions = ['delete_selected']
    
    def delete_queryset(self, request, queryset):
        """Custom bulk delete for companies"""
        for company in queryset:
            # Delete the user associated with this company (CASCADE will handle the rest)
            if company.user:
                company.user.delete()
        
    delete_queryset.short_description = "Delete selected companies and their users"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
