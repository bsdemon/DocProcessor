from rest_framework import serializers
from .models import ImportJob


class ImportUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class ImportStatusSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()

    class Meta:
        model = ImportJob
        fields = "__all__"

    def get_progress(self, obj):
        if obj.total_rows == 0:
            return 0
        return int(obj.processed_rows / obj.total_rows * 100)