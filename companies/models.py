from django.db import models

from authentication.models import CustomUser, Company


class Subscription(models.Model):
    subscription_id = models.BigAutoField(primary_key=True)
    investor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    get_email_newsletter = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
