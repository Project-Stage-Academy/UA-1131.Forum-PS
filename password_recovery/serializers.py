
from rest_framework import serializers



class PasswordRecoverySerializer(serializers.Serializer):
    email = serializers.EmailField()


