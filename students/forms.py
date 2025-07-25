# students/forms.py
from django import forms
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
import sys
from .models import StudentProfile

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
