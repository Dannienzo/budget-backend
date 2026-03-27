from django.db import models
import random 
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Applicant(models.Model):
    name=models.CharField(max_length=200, null=True)
    username=models.CharField(max_length=200, null=True)
    email=models.CharField(max_length=100, null=True)
    password=models.CharField(max_length=200, null=True)
    date=models.DateTimeField(max_length=200, null=True)


    def __str__(self):
        return f'{self.name} {self.username}'


class OTPVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

