from django.contrib import admin
from .models import Companies, CompaniesAndUsersRelations

# Register your models here.

admin.site.register(Companies)
admin.site.register(CompaniesAndUsersRelations)

