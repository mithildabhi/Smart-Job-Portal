from django import forms
from .models import JobApplication, Job

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'resume', 'portfolio_url']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write a compelling cover letter explaining why you\'re perfect for this role...'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-portfolio.com'
            }),
        }
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Check file size (5MB limit)
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 5MB.')
            
            # Check file type
            allowed_types = [
                'application/pdf', 
                'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            if resume.content_type not in allowed_types:
                raise forms.ValidationError('Only PDF and Word documents are allowed.')
        
        return resume
    
    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter')
        if len(cover_letter.strip()) < 100:
            raise forms.ValidationError('Cover letter must be at least 100 characters long.')
        return cover_letter

class JobForm(forms.ModelForm):
    """Form for companies to post/edit jobs"""
    required_skills = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Python, Django, JavaScript, React'
        }),
        help_text='Enter skills separated by commas'
    )
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'location', 'job_type', 
            'experience_required', 'positions_available',
            'salary_min', 'salary_max', 'salary',
            'required_skills', 'requirements', 'deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_required': forms.TextInput(attrs={'class': 'form-control'}),
            'positions_available': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary': forms.TextInput(attrs={'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
