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

    def create(self, validated_data):
        return Subscription.objects.create(**self.validated_data)

