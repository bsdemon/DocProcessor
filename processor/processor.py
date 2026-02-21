import csv
import io
from .models import ImportJob, ImportStatus
from django.utils import timezone
from loguru import logger

class CSVProcessor:

    BATCH_SIZE = 50

    def __init__(self, job: ImportJob):
        self.job = job

        # TODO remove this
        self.total_sum = 0.0
       
    def run(self) -> float:
        ImportJob.objects.filter(id=self.job.id).update(
            status=ImportStatus.PROCESSING,
            updated_at=timezone.now(),
        )


        success = failed = processed = 0

        with self.job.file.open("rb") as bf:
            with io.TextIOWrapper(bf, encoding="utf-8", newline="") as tf:
                reader = csv.DictReader(tf)

                for processed, row in enumerate(reader, start=1):
                    try:
                        self.process_row(row)
                        success += 1
                    except Exception:
                        failed += 1

                    if processed % self.BATCH_SIZE == 0:
                        self.update_progress(processed, success, failed)

        total = processed 
        logger.info(f"Job {self.job.id} finished: total={total}, success={success}, failed={failed}")
        self.finish(total, success, failed)
        return self.total_sum


    def process_row(self, row: dict[str, str]) -> None:
        if not row:
            raise ValueError("Invalid row")

        # TODO process row or ssimulate
        amount = float(row.get("amount", 0))
        self.total_sum += amount

    def update_progress(self, processed: int, success: int, failed: int) -> None:
        ImportJob.objects.filter(id=self.job.id).update(
            processed_rows=processed,
            success_rows=success,
            failed_rows=failed,
            updated_at=timezone.now(),
        )

    def finish(self, total: int, success: int, failed: int) -> None:
        ImportJob.objects.filter(id=self.job.id).update(
            status=ImportStatus.COMPLETED,
            total_rows=total,
            processed_rows=total,
            success_rows=success,
            failed_rows=failed,
            updated_at=timezone.now(),
            error="",
        )

