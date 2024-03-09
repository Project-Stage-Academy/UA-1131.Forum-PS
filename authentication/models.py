from datetime import datetime
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import (AbstractBaseUser, BaseUserManager)
from django.db import models
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from forum.errors import Error
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        user: CustomUser = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.registration_date = datetime.now()
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email=email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigAutoField(primary_key=True, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, default="-")
    registration_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = None
    company = None
    position = None
    is_authenticated = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["user_id", "password", "first_name", "surname", "phone_number"]
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.surname} {self.email}"

    @classmethod
    def get_user(cls, *args, **kwargs):
        return cls.objects.get(**kwargs)

    @classmethod
    def generate_company_related_token(cls, request):
        try:
            raw_token: str = request.headers.get('Authorization')
            access_token = raw_token.split(' ')[1]
            decoded_token = AccessToken(access_token)
            decoded_token.payload['company_id'] = request.data['company_id']
            return str(decoded_token)
        except TokenError as e:
            raise e

    def get_company_type(self):
        if not self.company:
            raise NotAuthenticated(detail=Error.NO_RELATED_TO_COMPANY.msg)
        try:
            return self.company.is_startup
        except (KeyError, TypeError):
            raise NotAuthenticated(detail=Error.NO_COMPANY_TYPE.msg)

    def get_email(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.surname}"

    def get_short_name(self):
        return self.first_name


class Company(models.Model):
    company_id = models.BigAutoField(primary_key=True)
    brand = models.CharField(max_length=255, blank=True)
    is_startup = models.BooleanField(default=False)
    common_info = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=255, blank=True)
    contact_email = models.CharField(max_length=255, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    edrpou = models.IntegerField(null=True)
    address = models.CharField(max_length=255, blank=True)
    product_info = models.TextField(blank=True)
    startup_idea = models.TextField(blank=True)
    tags = models.CharField(max_length=255, blank=True)


class CompanyAndUserRelation(models.Model):
    FOUNDER = "F"
    REPRESENTATIVE = "R"

    POSITION_CHOICES = ((FOUNDER, "Founder"),
                        (REPRESENTATIVE, "Representative"))

    relation_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_relations",
                                db_column="user_id")
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_relations",
                                   db_column="company_id")
    position = models.CharField(default=REPRESENTATIVE, max_length=30, choices=POSITION_CHOICES, blank=False,
                                null=False)

    @classmethod
    def get_relation(cls, u, c):
        relation = cls.objects.filter(user_id=u, company_id=c).first()
        return relation


class UserLoginActivity(models.Model):
    # Login Status
    SUCCESS = 'S'
    FAILED = 'F'

    LOGIN_STATUS = ((SUCCESS, 'Success'),
                    (FAILED, 'Failed'))

    login_IP = models.GenericIPAddressField(null=True, blank=True)
    login_datetime = models.DateTimeField(auto_now=True)
    login_email = models.CharField(max_length=40, null=True, blank=True)
    status = models.CharField(max_length=1, default=SUCCESS, choices=LOGIN_STATUS, null=True, blank=True)
    user_agent_info = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'user_login_activity'
        verbose_name_plural = 'user_login_activities'