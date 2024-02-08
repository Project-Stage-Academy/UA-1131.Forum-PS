from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import (AbstractBaseUser, BaseUserManager)
from django.db import models


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email=email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    registration_date = models.DateTimeField(auto_now_add=True)
    investor_role = models.BooleanField(default=False)
    startup_role = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "surname"]
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.surname} {self.email}"
