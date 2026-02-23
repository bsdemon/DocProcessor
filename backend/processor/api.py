from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .permissions import HasImportApiKey
from .serializers import ImportJobStatusSerializer, ImportUploadSerializer
from .services import ImportService
from .tasks import process_import
from .models import ImportJob


class ImportUploadApi(APIView):
    permission_classes = [HasImportApiKey]

    def post(self, request: Request) -> Response:
        serializer = ImportUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = ImportService.create_job(serializer.validated_data["file"])
        transaction.on_commit(lambda: process_import.delay(str(job.id)))
        return Response({"id": job.id}, status=status.HTTP_201_CREATED)


class ImportStatusApi(APIView):
    permission_classes = [HasImportApiKey]

    def get(self, request: Request, uuid: str) -> Response:
        job = get_object_or_404(ImportJob, pk=uuid)
        data = ImportJobStatusSerializer.from_instance(job)
        return Response(data, status=status.HTTP_200_OK)
