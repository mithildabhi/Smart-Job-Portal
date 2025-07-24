# companies/models.py - Final version
from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100, default='Technology')
    phone = models.CharField(max_length=20, default='+91 0000000000')
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=200, default="Mumbai, India")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name_plural = "Companies"
