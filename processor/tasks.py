from celery import shared_task
from .services import ImportService
from .models import ImportJob
from .processor import CSVProcessor


# TODO watchdog celery task to update log waited PENDING
@shared_task(bind=True)
def process_import(self, job_id: str):
    try:
        job = ImportJob.objects.get(id=job_id)
        # TODO remove total
        processor = CSVProcessor(job)
        total = processor.run()
        print(f"======> Total sum {total} <=======")
    except Exception as e:
        # TODO better exception handling
        # TODO if Redis is down, Celery also go down and this will not mark task as Failed
        ImportService.mark_failed(job_id=job_id, error=str(e))
        raise
