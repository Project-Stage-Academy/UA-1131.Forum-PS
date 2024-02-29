from django.contrib import admin

from authentication.models import Company, CompanyAndUserRelation

# Register your models here.

admin.site.register(Company)
admin.site.register(CompanyAndUserRelation)


