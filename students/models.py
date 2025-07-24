from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# from django.db import models
# from django.contrib.auth.models import User

# class Student(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     student_id = models.CharField(max_length=20, unique=True)
#     phone = models.CharField(max_length=15, blank=True)
#     college = models.CharField(max_length=200, blank=True)
#     course = models.CharField(max_length=100, blank=True)
#     year_of_study = models.IntegerField(blank=True, null=True)
#     skills = models.TextField(blank=True)
#     resume = models.FileField(upload_to='resumes/', blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.user.first_name} {self.user.last_name} - {self.student_id}"