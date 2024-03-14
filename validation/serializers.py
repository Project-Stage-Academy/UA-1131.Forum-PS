import re
from string import punctuation

import zxcvbn
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class CustomValidationSerializer(serializers.Serializer):
    @staticmethod
    def validate_edrpou(value):
        if not isinstance(value, int) or len(str(value)) != 8:
            raise serializers.ValidationError("EDRPOU must be an 8-digit number")
        return value

    @staticmethod
    def validate_contact_email(email_to_validate: str):
        pattern = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
        if not re.match(pattern, email_to_validate):
            raise ValidationError("Email is invalid")
        return email_to_validate

    @staticmethod
    def validate_contact_phone(phone_number_to_validate: str):
        pattern = r'^\+?[\d]{7,13}$'
        if not re.match(pattern, phone_number_to_validate):
            raise ValidationError("Phone number is invalid")
        return phone_number_to_validate

    @staticmethod
    def validation_password(password_to_validate, email=None, first_name=None, surname=None):
        if len(password_to_validate) < 8:
            raise ValidationError("Password length should be at least 8 characters ")
        if (not any(symbol.isdigit() for symbol in password_to_validate)
                or not any(symbol.islower() for symbol in password_to_validate)
                or not any(symbol.isupper() for symbol in password_to_validate)
                or not any(symbol in punctuation for symbol in password_to_validate)):
            raise ValidationError(
                "Password should include at least one uppercase latter, one lowercase letter, one digit and one symbol")
        complexity = zxcvbn.zxcvbn(password_to_validate, user_inputs=[email, first_name, surname])
        if complexity["score"] <= 2:
            raise ValidationError("Password is weak, please enter another one")

        return password_to_validate
