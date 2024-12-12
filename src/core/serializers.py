from dateutil import parser
from rest_framework import serializers

from core.models import StoredFile


class StoredFileSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(allow_blank=False)
    upload_date = serializers.CharField()

    class Meta:
        model = StoredFile
        fields = ['filename', 'upload_date']

    def validate_upload_date(self, value):
        try:
            parser.isoparse(value)
        except ValueError:
            raise serializers.ValidationError("Invalid date format.")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.upload_date is not None:
            rep['upload_date'] = instance.upload_date.isoformat()
        return rep


class UserDataSerializer(serializers.Serializer):
    username = serializers.CharField()
    folder = serializers.CharField()
    numberMessages = serializers.IntegerField()
    size = serializers.IntegerField(min_value=0)
