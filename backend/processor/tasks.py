from celery import shared_task
from loguru import logger

from .services import ImportService
from .models import ImportJob
from .processor import CSVProcessor


@shared_task(bind=True)
def process_import(self, job_id: str) -> None:
    try:
        job = ImportJob.objects.get(id=job_id)
        processor = CSVProcessor(job)
        total = processor.run()
        logger.info(f"ImportJob {job_id} completed successfully with amount: {total}")
    except ImportJob.DoesNotExist:
        logger.error(f"ImportJob {job_id} does not exist")
        return
    except Exception as e:
        ImportService.mark_failed(job_id=job_id, error=str(e))
        raise
