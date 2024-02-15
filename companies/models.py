from django.db import models

from authentication.models import CustomUser


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

    def __str__(self):
        return self.brand


class CompaniesAndUsersRelations(models.Model):
    relation_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    position = models.IntegerField()

    def __str__(self):
        return f'{self.company_id.brand}'
