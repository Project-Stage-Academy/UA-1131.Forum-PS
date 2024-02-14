from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from authentication.models import CustomUser


class CustomAdmin(UserAdmin):
    model = CustomUser
    list_display = ["id",
                    'email', 'first_name', 'surname', "phone_number",
                    'is_superuser', 'is_verified']
    readonly_fields = ("registration_date",)
    ordering = ['email', ]
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'surname', "phone_number")}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Important dates', {'fields': ('last_login', "registration_date")}),
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

