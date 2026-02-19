from django.utils import timezone
from .models import ImportJob, ImportStatus

class ImportService:

    @staticmethod
    def create_job(file: str)-> ImportJob:
        return ImportJob.objects.create(file=file)

    @staticmethod
    def mark_failed(job_id: str, error: str) -> None:
        print(f"==================> {job_id} {error} <======================")
        ImportJob.objects.filter(id=job_id).update(
            status=ImportStatus.FAILED,
            error=error,
            updated_at=timezone.now(),
        )