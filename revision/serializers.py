from rest_framework import serializers
from rest_framework.exceptions import APIException
from reversion.models import Version
from reversion.errors import RevertError


class RevisionSerializer(serializers.ModelSerializer):
    """
    Serializer with the model set to Version:
    1) version_id - primary key of the version instance.
    2) updated_at - creation date of the version instance, which simultaneously indicates when the instance was updated.
    3) updated_by - user id of the user that has performed the update, if authentication is implemented.
    4) instance - a JSON object representation of the instance after the update.
    """
    version_id = serializers.PrimaryKeyRelatedField(read_only=True, source='id')
    updated_at = serializers.DateTimeField(read_only=True, source='revision.date_created')
    updated_by = serializers.SlugRelatedField(read_only=True, source='revision.user', slug_field='email')
    instance = serializers.JSONField(read_only=True, source='field_dict')

    class Meta:
        model = Version
        fields = ['version_id', 'updated_at', 'updated_by', 'instance']