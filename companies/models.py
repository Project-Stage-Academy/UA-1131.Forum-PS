from django.db import models
from authentication.models import CompanyAndUserRelation, Company

class Subscription(models.Model):
    subscription_id = models.BigAutoField(primary_key=True)
    investor = models.ForeignKey(CompanyAndUserRelation, on_delete=models.CASCADE, to_field='relation_id')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    get_email_newsletter = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_subcription(cls, *args, **kwargs):
        return cls.objects.get(**kwargs)
         
    @classmethod
    def get_subcriptions(cls, *args, **kwargs):
        return cls.objects.filter(**kwargs)