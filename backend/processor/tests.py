from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APITestCase

from .models import ImportJob, ImportStatus
from .processor import CSVProcessor
from .services import ImportService


class ImportUploadApiTest(APITestCase):

    @patch("processor.api.process_import")
    def test_upload_creates_job_and_returns_id(self, mock_task):
        csv_content = b"amount,name\n10,foo\n20,bar"
        file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")

        response = self.client.post("/api/imports/", {"file": file}, format="multipart")

        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)
        self.assertTrue(ImportJob.objects.filter(id=response.data["id"]).exists())

    def test_upload_without_file_returns_400(self):
        response = self.client.post("/api/imports/", {}, format="multipart")
        self.assertEqual(response.status_code, 400)


class ImportStatusApiTest(APITestCase):

    def test_status_returns_expected_fields(self):
        job = ImportJob.objects.create(
            file="imports/test.csv",
            status=ImportStatus.PROCESSING,
            total_rows=100,
            processed_rows=50,
        )

        response = self.client.get(f"/api/imports/{job.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], ImportStatus.PROCESSING)
        self.assertEqual(response.data["progress"], 50)

    def test_status_returns_404_for_unknown_job(self):
        response = self.client.get("/api/imports/00000000-0000-0000-0000-000000000000/")
        self.assertEqual(response.status_code, 404)


class CSVProcessorTest(TestCase):

    def _make_job(self, csv_content: bytes) -> ImportJob:
        file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
        return ImportJob.objects.create(file=file)

    def test_all_valid_rows_counted_as_success(self):
        job = self._make_job(b"amount,name\n10,foo\n20,bar\n30,baz")
        CSVProcessor(job).run()

        job.refresh_from_db()
        self.assertEqual(job.status, ImportStatus.COMPLETED)
        self.assertEqual(job.total_rows, 3)
        self.assertEqual(job.success_rows, 3)
        self.assertEqual(job.failed_rows, 0)

    def test_invalid_rows_counted_as_failed(self):
        # non-numeric amount → float("bad") raises ValueError
        job = self._make_job(b"amount,name\nbad,foo\nalso_bad,bar")
        CSVProcessor(job).run()

        job.refresh_from_db()
        self.assertEqual(job.status, ImportStatus.COMPLETED)
        self.assertEqual(job.failed_rows, 2)
        self.assertEqual(job.success_rows, 0)

    def test_status_transitions_to_processing_then_completed(self):
        job = self._make_job(b"amount\n5")
        self.assertEqual(job.status, ImportStatus.PENDING)

        CSVProcessor(job).run()

        job.refresh_from_db()
        self.assertEqual(job.status, ImportStatus.COMPLETED)


class ImportServiceTest(TestCase):

    def test_mark_failed_sets_status_and_error(self):
        job = ImportJob.objects.create(file="imports/test.csv")
        ImportService.mark_failed(job_id=str(job.id), error="something went wrong")

        job.refresh_from_db()
        self.assertEqual(job.status, ImportStatus.FAILED)
        self.assertEqual(job.error, "something went wrong")
