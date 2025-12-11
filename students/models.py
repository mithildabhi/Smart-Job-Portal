from django.db import models
from django.contrib.auth.models import User
import os

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    
    # ✅ UPDATED: Academic fields (renamed to match form expectations)
    college_name = models.CharField(max_length=200, blank=True, null=True)  # Changed from 'college'
    degree = models.CharField(max_length=100, blank=True, null=True)  # Changed from 'course'
    graduation_year = models.IntegerField(blank=True, null=True)  # Changed from 'year_of_study'
    
    # ✅ ADDED: Missing fields that the form expects
    gpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    github_url = models.URLField(blank=True, null=True, help_text="GitHub profile URL")
    portfolio_url = models.URLField(blank=True, null=True, help_text="Portfolio website URL")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True, help_text="Upload your resume (PDF)")
    
    # Existing fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills (e.g., Python, JavaScript, React)")
    experience = models.TextField(blank=True, null=True, help_text="Work experience details")
    education = models.TextField(blank=True, null=True, help_text="Educational background")
    projects = models.TextField(blank=True, null=True, help_text="Personal/academic projects")
    
    def has_profile_picture(self):
        """Check if user has a profile picture"""
        return bool(self.profile_picture and self.profile_picture.name)

    def delete_profile_picture(self):
        """Delete the profile picture file from storage"""
        if self.profile_picture:
            # Delete the physical file from storage
            try:
                if os.path.isfile(self.profile_picture.path):
                    os.remove(self.profile_picture.path)
            except (ValueError, OSError):
                # Handle cases where file doesn't exist or path is invalid
                pass
            
            # Clear the field in the database
            self.profile_picture = None
            self.save()
    
    skills = models.TextField(blank=True, null=True)  # ensure this field exists

    def get_skills_list(self):
        """
        Return list of dicts: [{'name': 'Python', 'percent': 90}, ...]
        If stored 'skills' currently contains only names (comma separated), percent will be 0.
        """
        if not self.skills:
            return []
        items = []
        for item in self.skills.split(','):
            it = item.strip()
            if not it:
                continue
            # support "name||percent" legacy format if present:
            if '||' in it:
                name, pct = it.split('||', 1)
                try:
                    pct = int(pct)
                except Exception:
                    pct = 0
                items.append({'name': name.strip(), 'percent': pct})
            else:
                # just name stored
                items.append({'name': it, 'percent': 0})
        return items

    def set_skills_list(self, skills_list):
        """
        Accepts either:
         - ['Python','Django']  OR
         - [{'name':'Python','percent':90}, ...]
        Normalizes and stores as comma-separated names (backwards compatible).
        If you later change DB to store separate Skill rows, update this.
        """
        normalized_names = []
        for s in skills_list:
            if isinstance(s, dict):
                name = s.get('name', '').strip()
            else:
                name = str(s or '').strip()
            if name:
                normalized_names.append(name)
        # store names as comma separated string (backwards compatible)
        self.skills = ', '.join(normalized_names)
        self.save()

        
    def get_full_name(self):
        """Return user's full name"""
        return self.user.get_full_name() or self.user.username
            
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Keep your existing Student model if needed
# class Student(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=100)

    # def __str__(self):
    #     return self.user.username
