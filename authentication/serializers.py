import logging
from datetime import datetime

from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import CustomUser
from authentication.utils import Utils
from validation.serializers import CustomValidationSerializer


class UserRegistrationSerializer(serializers.ModelSerializer, CustomValidationSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    surname = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    class Meta:
        model = CustomUser
        fields = (
            "email", "password", "password2", "first_name", "surname", 'phone_number')

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        password2 = attrs.pop("password2")
        first_name = attrs.get("first_name")
        surname = attrs.get("surname")
        phone_number = attrs.get("phone_number")
        if password != password2:
            raise ValidationError({"password": "Passwords are different"})
        try:
            self.validate_contact_email(email)
        except ValidationError as e:
            raise ValidationError({"email": e.detail})
        try:
            self.validate_password(password, email, first_name, surname)
        except ValidationError as e:
            raise ValidationError({"password": e.detail})
        try:
            self.validate_contact_phone(phone_number)
        except ValidationError as e:
            raise ValidationError({"phone_number": e.detail})
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer, CustomValidationSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    first_name = serializers.CharField(required=True)
    surname = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "surname", 'phone_number',)

    def validate(self, attrs):
        email = attrs.get("email")
        phone_number = attrs.get("phone_number")
        try:
            self.validate_contact_email(email)
        except ValidationError as e:
            raise ValidationError({"email": e.detail})
        try:
            self.validate_contact_phone(phone_number)
        except ValidationError as e:
            raise ValidationError({"phone_number": e.detail})
        return attrs

    def update(self, instance, validated_data):
        logger = logging.getLogger('account_update')
        new_email = validated_data.get("email")
        if new_email != instance.email:
            instance.is_validated = False
            tokens = RefreshToken.for_user(instance)
            access_token = str(tokens.access_token)
            instance = super().update(instance, validated_data)
            Utils.send_verification_email(get_current_site(self.context['request']).domain, instance, access_token)
            logger.info(
                f"User {instance.email} {instance.first_name} {instance.surname} updated his\
                     account information:{validated_data} (Email in process of verification)")
            return instance
        instance = super().update(instance, validated_data)
        logger.info(
            f"User {instance.email} {instance.first_name} {instance.surname} updated his\
                             account information:{validated_data}")

        return instance


class PasswordRecoverySerializer(serializers.ModelSerializer, CustomValidationSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['password', 'password2']

    def validate(self, attrs):
        password1 = attrs.get('password')
        password2 = attrs.get('password2')
        if password1 != password2:
            raise ValidationError(detail="Passwords are different")
        try:
            self.validate_password(password1)
        except ValidationError as e:
            raise ValidationError(detail=e.detail)
        return attrs
