from rest_framework import serializers
from .models import Companies


class CompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companies
        fields = '__all__'

    @staticmethod
    def validate_edrpou(value):
        if not isinstance(value, int) or len(str(value)) != 8:
            raise serializers.ValidationError("EDRPOU must be an 8-digit number")
        return value
