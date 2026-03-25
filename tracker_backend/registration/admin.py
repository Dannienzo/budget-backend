from django.contrib import admin
from .models import *

# Register your models here.

class ApplicantAdmin(admin.ModelAdmin):

    list_display=('name', 'username', 'email', 'password')

    list_filter=( 'username', 'email', 'password')


admin.site.register(Applicant, ApplicantAdmin)