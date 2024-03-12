from rest_framework.serializers import ModelSerializer
from validation.serializers import CustomValidationSerializer

from .models import Company, Subscription


class CompaniesSerializer(CustomValidationSerializer, ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class SubscriptionSerializer(CustomValidationSerializer, ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['investor', 'company', 'get_email_newsletter']
