# students/forms.py
from django import forms
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
import sys
from .models import StudentProfile
from django.contrib.auth.models import User

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'profile-picture-input'
            })
        }
    
    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        
        if picture:
            # Check file size (5MB limit)
            if picture.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large. Please keep it under 5MB.")
            
            # Check file type
            valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if picture.content_type not in valid_types:
                raise ValidationError("Please upload a valid image file (JPG, PNG, GIF).")
            
            # Check image dimensions and resize if necessary
            try:
                img = Image.open(picture)
                
                # Resize image if it's too large (max 1000x1000)
                if img.width > 1000 or img.height > 1000:
                    # Resize image while maintaining aspect ratio
                    img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                    
                    # Save the resized image back to the file
                    output = BytesIO()
                    
                    # Determine format for saving
                    format_mapping = {
                        'image/jpeg': 'JPEG',
                        'image/jpg': 'JPEG',
                        'image/png': 'PNG',
                        'image/gif': 'GIF'
                    }
                    
                    save_format = format_mapping.get(picture.content_type, 'JPEG')
                    
                    # Convert RGBA to RGB for JPEG format
                    if save_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                        # Create a white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    img.save(output, format=save_format, quality=85, optimize=True)
                    output.seek(0)
                    
                    # Update the file object
                    picture.file = output
                    picture.size = sys.getsizeof(output.getvalue())
                    
            except Exception as e:
                raise ValidationError("Invalid image file. Please upload a valid image.")
        
        return picture


# Additional form for quick profile picture operations
class QuickProfilePictureForm(forms.Form):
    """Simple form for AJAX profile picture uploads"""
    profile_picture = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'style': 'display: none;'  # For custom upload buttons
        })
    )
    
    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        
        if picture:
            # Basic validations
            if picture.size > 5 * 1024 * 1024:  # Limit to 5MB
                raise ValidationError("Image file too large ( > 5MB )")

            # Validate image format
            valid_formats = ['image/jpeg', 'image/png', 'image/gif']
            if picture.content_type not in valid_formats:
                raise ValidationError("Unsupported image format. Please upload JPEG, PNG, or GIF.")

        return picture


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'profile_picture', 'bio', 'phone', 'location', 'date_of_birth',
            'skills', 'experience', 'education', 'projects',
            'linkedin_url', 'github_url', 'portfolio_url', 'resume',
            'college_name', 'degree', 'graduation_year', 'gpa'
        ]
        
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Python, JavaScript, React, Node.js, MySQL, Git...'
            }),
            'experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your work experience, internships, or relevant projects...'
            }),
            'education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Educational background, certifications, courses...'
            }),
            'projects': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your personal or academic projects...'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/yourusername'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourportfolio.com'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'college_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'University/College Name'
            }),
            'degree': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bachelor of Computer Science'
            }),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2025'
            }),
            'gpa': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '3.8',
                'step': '0.01'
            }),
        }

class BasicInfoForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class SkillsForm(forms.Form):
    skills = forms.CharField(widget=forms.HiddenInput(), required=False)
