from datetime import datetime
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import (AbstractBaseUser, BaseUserManager)
from django.db import models



class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        user:CustomUser = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.registration_date = datetime.now()
        print(user.user_id)
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


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["user_id", "password", "first_name", "surname", "phone_number"]
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
    
    def get_user(self, *args, **kwargs):
        return self.objects.get(**kwargs)
    

class Companies(models.Model):
    company_id = models.BigAutoField(primary_key=True, unique=True)
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


class Positions(models.Model):
    position_id = models.BigAutoField(primary_key=True, unique=True)
    position = models.CharField(max_length=100)
    position_descr = models.CharField(max_length=500, blank=True)


class CompaniesAndUsersRelations(models.Model):
    relation_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_relation')
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name='company_relation')
    position = models.ForeignKey(Positions, on_delete=models.CASCADE)

    def get_relation(self, u_id, c_id):
        return self.objects.filter(
                    user_id=u_id, company_id=c_id)[0].values(AuthUser.required_fields)


class AuthUser(AbstractBaseUser):
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    position = models.CharField(max_length=25)
    company_id = models.ForeignKey(to=Companies,on_delete=models.CASCADE)
    user_id = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    is_startup = models.BooleanField()
    is_verified = models.BooleanField()
    is_superuser = models.BooleanField()
    is_authenticated = models.BooleanField()
    error = models.CharField(max_length=150)

    USERNAME_FIELD = 'email'
    
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


    def __str__(self): 
        return str(self.__dict__)
            
    






