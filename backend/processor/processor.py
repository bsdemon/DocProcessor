import csv
import io
from typing import Any

from loguru import logger

from .validators import CSVHeaderValidator, CSVRowValidator

from .models import ImportJob, ImportStatus

from django.utils import timezone


class CSVProcessor:
    BATCH_SIZE = 50

    def __init__(self, job: ImportJob):
        self.job = job

        self.total_sum = 0.0

    def run(self) -> float:
        ImportJob.objects.filter(id=self.job.id).update(
            status=ImportStatus.PROCESSING,
            processed_rows=0,
            success_rows=0,
            failed_rows=0,
            error="",
            updated_at=timezone.now(),
        )

        with self.job.file.open("rb") as bf:
            with io.TextIOWrapper(bf, encoding="utf-8", newline="") as tf:
                r = csv.DictReader(tf)
                total_rows = max(0, sum(1 for _ in r))
                CSVHeaderValidator.validate_header(r.fieldnames)

        ImportJob.objects.filter(id=self.job.id).update(
            total_rows=total_rows,
            updated_at=timezone.now(),
        )

        success = failed = processed = 0

        with self.job.file.open("rb") as bf:
            with io.TextIOWrapper(bf, encoding="utf-8", newline="") as tf:
                reader = csv.DictReader(tf)

                for processed, row in enumerate(reader, start=1):
                    try:
                        validated = CSVRowValidator.validate_row(row)
                        self.process_row(validated)
                        success += 1
                    except (ValueError, SyntaxError) as exc:
                        logger.error(
                            f"Row failed validation: job={self.job.id} row={row} error={str(exc)}"
                        )
                        failed += 1
                    except Exception as exc:
                        logger.exception(
                            f"Row failed: job={self.job.id} row={processed} error={str(exc)}"
                        )
                        failed += 1

                    if processed % self.BATCH_SIZE == 0:
                        self.update_progress(processed, success, failed)

        self.finish(total_rows, success, failed)
        return self.total_sum

    def process_row(self, row: dict[str, Any]) -> None:
        if not row:
            raise ValueError("Invalid row")

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
        status = ImportStatus.COMPLETED
        ImportJob.objects.filter(id=self.job.id).update(
            status=status,
            total_rows=total,
            processed_rows=total,
            success_rows=success,
            failed_rows=failed,
            error="",
            updated_at=timezone.now(),
        )
