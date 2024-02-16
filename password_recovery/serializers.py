
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentication.models import CustomUser
from validation.serializers import CustomValidationSerializer


class PasswordRecoverySerializer(serializers.ModelSerializer, CustomValidationSerializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        # Specify metadata options here
        fields = ['email', 'password', 'password2']

    def validate(self, attrs):
        email = attrs.get("email")
        password1 = attrs.get('password')
        password2 = attrs.get('password2')
        first_name = attrs.get("first_name")
        surname = attrs.get("surname")
        if password1 != password2:
            raise serializers.ValidationError({"password": "Passwords are different"})
        try:
            self.validation_password(password1, email, first_name, surname)
        except ValidationError as e:
            raise ValidationError({"password": e.detail})
        return attrs


