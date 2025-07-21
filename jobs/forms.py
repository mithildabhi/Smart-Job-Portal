from django import forms
from .models import Job, Application

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'deadline']

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']
