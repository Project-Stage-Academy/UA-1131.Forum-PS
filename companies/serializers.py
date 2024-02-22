from rest_framework import serializers
from .models import Companies
import re


class CompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companies
        fields = '__all__'

    @staticmethod
    def validate_edrpou(value):
        if not isinstance(value, int) or len(str(value)) != 8:
            raise serializers.ValidationError("EDRPOU must be an 8-digit number")
        return value
    
    @staticmethod
    def validate_contact_email(email):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise serializers.ValidationError('Incorrect email')
        return email
    
    @staticmethod
    def validate_contact_phone(phone):
        if not re.match(r'^\+380\d{2,5}\d{7}$', phone):
            raise serializers.ValidationError('Incorrect phone number')
        return phone

