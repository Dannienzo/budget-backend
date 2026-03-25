from django.db import models

# Create your models here.

class Applicant(models.Model):
    name=models.CharField(max_length=200, null=True)
    username=models.CharField(max_length=200, null=True)
    email=models.CharField(max_length=100, null=True)
    password=models.CharField(max_length=200, null=True)
    date=models.DateTimeField(max_length=200, null=True)


    def __str__(self):
        return f'{self.name} {self.username}'

