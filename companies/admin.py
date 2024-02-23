from django.contrib import admin
from .models import Company, CompanyAndUserRelation

# Register your models here.

admin.site.register(Company)
admin.site.register(CompanyAndUserRelation)

