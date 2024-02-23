from django.db import models

from authentication.models import CustomUser


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

    HEAD = "H"
    REPRESENTATIVE = "R"

    POSITION_CHOICES = ((HEAD, "Head"), 
                        (REPRESENTATIVE, "Representative"))

    relation_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    position = models.CharField(default=REPRESENTATIVE, choices=POSITION_CHOICES, blank=False, null=False)

class Subscription(models.Model):
    subscription_id = models.BigAutoField(primary_key=True)
    investor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    get_email_newsletter = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
