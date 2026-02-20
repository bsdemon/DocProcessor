import csv
from .models import ImportJob, ImportStatus


class CSVProcessor:

    BATCH_SIZE = 50

    def __init__(self, job: ImportJob):
        self.job = job

        # TODO remove this
        self.total_sum = 0.0
       

    def run(self) -> float:
        self.job.status = ImportStatus.PROCESSING
        self.job.save(update_fields=["status"])

        with self.job.file.open("r", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            total = sum(1 for _ in reader)

            f.seek(0)
            reader = csv.DictReader(f)  # recreate reader, reader is iterator

        ImportJob.objects.filter(id=self.job.id).update(
            total_rows=total
        )

        success = 0
        failed = 0

        for index, row in enumerate(reader, start=1):
            try:
                self.process_row(row)
                success += 1
            except Exception:
                failed += 1

            if index % self.BATCH_SIZE == 0:
                self.update_progress(index, success, failed)
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
        )

    def finish(self, total: int, success: int, failed: int) -> None:
        ImportJob.objects.filter(id=self.job.id).update(
            status=ImportStatus.COMPLETED,
            processed_rows=total,
            success_rows=success,
            failed_rows=failed,
        )

