from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from authentication.models import CustomUser, UserLoginActivity, CompanyAndUserRelation, Company


class CustomAdmin(UserAdmin):
    model = CustomUser
    list_display = ["user_id",
                    'email', 'first_name', 'surname', "phone_number",
                    'is_superuser', 'is_verified']
    readonly_fields = ("registration_date",)
    ordering = ['email', ]
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'surname', "phone_number")}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Important dates', {'fields': ("registration_date",)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',)}
         ),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_verified',
            )}
         ),
    )


admin.site.register(CustomUser, CustomAdmin)


class CompanyAndUserRelationAdmin(admin.ModelAdmin):
    list_display = ('relation_id', 'user_id', 'company_id', 'position')
    list_per_page = 20


admin.site.register(CompanyAndUserRelation, CompanyAndUserRelationAdmin)


class UserLoginActivityAdmin(admin.ModelAdmin):
    list_display = ["login_email", "status", "login_datetime"]


admin.site.register(UserLoginActivity, UserLoginActivityAdmin)
admin.site.register(Company)

