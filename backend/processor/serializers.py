from typing import Optional, Set

from rest_framework import serializers

from .models import ImportJob


ALLOWED_CONTENT_TYPES: Set[str] = {
    "text/csv",
    "application/csv",
    "text/plain",
    "application/vnd.ms-excel",
}


def _validate_extension(filename: str) -> None:
    if not filename.lower().endswith(".csv"):
        raise serializers.ValidationError("File must be a .csv")


def _validate_not_empty(head: bytes) -> None:
    if not head:
        raise serializers.ValidationError("File is empty.")


def _validate_not_binary(head: bytes) -> None:
    if b"\x00" in head:
        raise serializers.ValidationError("File looks like a binary file, not CSV.")


def _validate_content_type(content_type: Optional[str]) -> None:
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise serializers.ValidationError(f"Unsupported content type: {content_type}")


class ImportUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, f):
        filename = f.name or ""
        _validate_extension(filename)
        _validate_content_type(f.content_type)

        pos = f.tell()
        head = f.read(4096)
        f.seek(pos)

        _validate_not_empty(head)
        _validate_not_binary(head)

        return f


class ImportStatusSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()

    class Meta:
        model = ImportJob
        fields = "__all__"

    def get_progress(self, obj: ImportJob) -> int:
        if obj.total_rows == 0:
            return 0
        return int(obj.processed_rows / obj.total_rows * 100)
