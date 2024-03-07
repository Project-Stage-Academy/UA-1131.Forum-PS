import re
from validation.serializers import CustomValidationSerializer
from .models import Company, Subscription
import re



class CompaniesSerializer(CustomValidationSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class SubscriptionSerializer(CustomValidationSerializer):
    class Meta:
        model = Subscription
        fields = ['investor', 'company', 'get_email_newsletter']

class SubscriptionListSerializer(CustomValidationSerializer):
    class Meta:
        model = Subscription
        fields = ['subscription_id', 'company_id', 'get_email_newsletter']
