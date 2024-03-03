from datetime import datetime

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
import logging
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
            raise serializers.ValidationError({"password": "Passwords are different"})
        try:
            self.validation_email(email)
        except ValidationError as e:
            raise ValidationError({"email": e.detail})
        try:
            self.validation_password(password, email, first_name, surname)
        except ValidationError as e:
            raise ValidationError({"password": e.detail})
        try:
            self.validation_phone_number(phone_number)
        except ValidationError as e:
            raise ValidationError({"phone_number": e.detail})
        return attrs

    def create(self,validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        tokens = RefreshToken.for_user(user)
        access_token = str(tokens.access_token)
        Utils.send_verification_email(get_current_site(self.context['request']).domain, user, access_token)
        return user


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
            self.validation_email(email)
        except ValidationError as e:
            raise ValidationError({"email": e.detail})
        try:
            self.validation_phone_number(phone_number)
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


class UserPasswordUpdateSerializer(serializers.ModelSerializer, CustomValidationSerializer):
    previous_password = serializers.CharField(label="Previous password", required=True, write_only=True)
    new_password = serializers.CharField(label="New password", required=True, write_only=True)

    class Meta:
        model = CustomUser
        fields = ("previous_password", "new_password")

    def validate(self, attrs):
        previous_password = attrs.get("previous_password")
        new_password = attrs.get("new_password")
        user = self.instance
        if not check_password(previous_password, user.password):
            raise ValidationError({"previous_password": "Wrong previous password"})
        try:
            self.validation_password(new_password)
        except ValidationError as e:
            raise ValidationError({"password": e.detail})
        return attrs

    def update(self, instance, validated_data):
        logger = logging.getLogger('account_update')
        new_password = validated_data.pop("new_password")
        instance.set_password(new_password)
        instance = super().update(instance, validated_data)
        Utils.send_password_update_email(instance)
        logger.info(
            f"{datetime.now()}: User {instance.email} {instance.first_name} {instance.surname} updated his password")
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
            raise serializers.ValidationError({"password": "Passwords are different"})
        try:
            self.validation_password(password1)
        except ValidationError as e:
            raise ValidationError({"password": e.detail})
        return attrs

    def update(self, instance, validated_data):
        new_password = validated_data.pop("password")
        instance.password = make_password(new_password)
        instance.save()
        Utils.send_password_update_email(instance)
        return instance