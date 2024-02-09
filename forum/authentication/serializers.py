from datetime import datetime
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import CustomUser
from authentication.utils import Utils
from validation.validation import (validation_email, validation_password)


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    investor_role = serializers.BooleanField()
    startup_role = serializers.BooleanField()

    class Meta:
        model = CustomUser
        fields = ("email", "password", "password2", "first_name", "surname", "investor_role", "startup_role")
        extra_kwargs = {
            'first_name': {"required": True},
            'surname': {"required": True},
        }

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        password2 = attrs.pop("password2")
        first_name = attrs.get("first_name")
        surname = attrs.get("surname")
        investor_role = attrs.get("investor_role")
        startup_role = attrs.get("startup_role")
        if password != password2:
            raise serializers.ValidationError({"password": "Passwords are different"})
        try:
            validation_email(email)
        except ValidationError as e:
            raise ValidationError({"email": e.detail})
        try:
            validation_password(password, email, first_name, surname)
        except ValidationError as e:
            raise ValidationError({"password": e.detail})
        if not investor_role and not startup_role:
            raise ValidationError("Please choose who you represent ")
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        user.set_password(validated_data.get("password"))
        user.registration_date = datetime.now()
        user.save()
        self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        current_site = get_current_site(self.context['request']).domain
        tokens = RefreshToken.for_user(user)
        access_token = str(tokens.access_token)
        verification_link = reverse('email_verify')
        absurl = f"http://{current_site}{verification_link}?token={str(access_token)}"
        from_email = settings.EMAIL_HOST_USER
        email_body = f'Hello {user.first_name} {user.surname} Use link below to verify your account\n {absurl}'
        data = {'to_email': user.email,
                'from_email': from_email,
                'email_body': email_body,
                'email_subject': "Email verification"}
        Utils.send_verification_email(data)

