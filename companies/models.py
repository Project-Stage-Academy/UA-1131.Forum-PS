from authentication.models import CustomUser, Company, CompanyAndUserRelation
from django.db import models

class Subscription(models.Model):
    subscription_id = models.BigAutoField(primary_key=True)
    investor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    get_email_newsletter = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)


class CompanyArticle(models.Model):
    article_id = models.BigAutoField(primary_key=True)
    relation = models.ForeignKey(CompanyAndUserRelation, on_delete=models.CASCADE)
    article_text = models.TextField(null=True)
    article_tags = models.TextField(null=True)
    added_at = models.DateTimeField(auto_now_add=True)