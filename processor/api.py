from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from .serializers import ImportUploadSerializer, ImportStatusSerializer
from .services import ImportService
from .tasks import process_import
from .models import ImportJob


class ImportUploadApi(APIView):

    def post(self, request):
        serializer = ImportUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO if there is pending job for the same file or we have running job for the same file
        # TODO proper error handlind
        job = ImportService.create_job(serializer.validated_data["file"])
        transaction.on_commit(lambda: process_import.delay(str(job.id)))
        return Response({"id": job.id}, status=status.HTTP_201_CREATED)


class ImportStatusApi(APIView):

    def get(self, request, pk):
        job = get_object_or_404(ImportJob, pk=pk)
        return Response(ImportStatusSerializer(job).data)


        # # TODO fix the way it needs to be handled
        # def dispatch():
        #     try:
        #         process_import.apply_async(args=[job.id], retry=False)
        #         # process_import.delay(job.id)
        #     except OperationalError:
        #         # broker is down / unreachable
        #         print("=====================> No connection to broker OperationalError <=================================")
        #         ImportService.mark_failed(job.id, error="Task queue unavailable")
        #     except (OSError, ConnectionError) as exc:
        #         print("=====================> No connection to broker OSError, ConnectionError <=================================")
        #         print(exc)
        #     except Exception as exc:
        #         print("=====================> No connection to broker EEEEXception <=================================")
        #         print(type(exc).__name__, exc)  # will show: ModuleNotFoundError No module named '127'
        #         raise
        # transaction.on_commit(dispatch)