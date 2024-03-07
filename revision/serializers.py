from rest_framework import serializers
from rest_framework.exceptions import APIException
from reversion.models import Version
from reversion.errors import RevertError


class RevisionSerializer(serializers.ModelSerializer):
    version = serializers.PrimaryKeyRelatedField(read_only=True, source='id')
    updated_at = serializers.DateTimeField(read_only=True, source='revision.date_created')
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True, source='revision.user')
    instance = serializers.JSONField(read_only=True, source='field_dict')

    class Meta:
        model = Version
        fields = ['version', 'updated_at', 'updated_by', 'instance']