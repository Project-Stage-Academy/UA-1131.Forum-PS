import re
from rest_framework import serializers
from validation.serializers import CustomValidationSerializer
from .models import Company, Subscription
import re


class CompaniesSerializer(serializers.ModelSerializer, CustomValidationSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['investor', 'company', 'get_email_newsletter']

class SubscriptionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['subscription_id', 'company_id', 'get_email_newsletter']
