from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import (AbstractBaseUser, BaseUserManager)
from django.db import models

# I suppose that all main models, as User, Company and Relations should be in one place
# since they`re required for authentication



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
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigAutoField(primary_key=True, unique=True, auto_created=True, default=0)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, default="-")
    registration_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password", "first_name", "surname", "phone_number"]
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.surname} {self.email}"
    
    def get_auth_data(self):
        return {'email': self.email,
                'password': self.password,
                'first_name': self.first_name,
                'surname': self.surname,
                'user_id': self.user_id,
                'is_verified': self.is_verified,
                'is_superuser': self.is_superuser}
    

class Companies(models.Model):
    company_id = models.BigAutoField(primary_key=True)
    brand = models.CharField(max_length=255, blank=True)
    is_registered = models.BooleanField(default=False)
    common_info = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=255, blank=True)
    contact_email = models.CharField(max_length=255, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    edrpou = models.IntegerField(blank=True, null=True)
    address = models.TextField(max_length=255, blank=True)
    product_info = models.TextField(blank=True)
    startup_idea = models.TextField(blank=True)
    tags = models.CharField(max_length=255, blank=True)


class CompaniesAndUsersRelations(models.Model):
    relation_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    position = models.IntegerField()

class AuthUser(AbstractBaseUser):
    email = models.EmailField(max_length=100, default=None, unique=True)
    password = models.CharField(max_length=128, default=None)
    first_name = models.CharField(max_length=100, default=None)
    surname = models.CharField(max_length=100, default=None)
    position = models.CharField(max_length=25, default=None)
    company_id = models.IntegerField(default=None)
    user_id = models.IntegerField(default=None)
    is_startup = models.BooleanField(default='undefined')
    is_verified = models.BooleanField(default='undefined')
    is_superuser = models.BooleanField(default=False)
    is_authenticated = models.BooleanField(default=False)
    error = models.CharField(max_length=150, default=None)

    USERNAME_FIELD = 'email'
    
    # using for data formatting
    required_fields = ['email',
                       'password',
                       'first_name', 
                       'surname', 
                       'position', 
                       'company_id',
                       'user_id', 
                       'is_startup', 
                       'is_verified', 
                       'is_superuser',]
    class Meta:
        managed = False # this model is not supposed for migration

    def __str__(self): 
        return str(self.__dict__)
            
    






