from django.db import models

from authentication.models import Company, CompanyAndUserRelation, CustomUser


class Subscription(models.Model):
    subscription_id = models.BigAutoField(primary_key=True)
    investor = models.ForeignKey(CompanyAndUserRelation, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    get_email_newsletter = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def get_subscription(cls, *args, **kwargs):
        return cls.objects.get(**kwargs)

    @classmethod
    def get_subscriptions(cls, *args, **kwargs):
        return cls.objects.filter(**kwargs)

    def get_info(self):
        data = {'subscribed_at': self.subscribed_at,
                'company_name': self.company.brand,
                'company_id': self.company.company_id}
        return data
