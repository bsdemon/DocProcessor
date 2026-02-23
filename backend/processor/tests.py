from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils.dateparse import parse_datetime
from rest_framework.test import APITestCase

from .models import ImportJob, ImportStatus
from .processor import CSVProcessor
from .services import ImportService

csv_content = (
    b"id,name,email,amount\n1,name-1,foo@example.com,100\n2,name-2,bar@example.com,200"
)

csv_content_with_errors = b"id,name,email,amount\n1,name-2,bar@,200\n1,,baz@foo.com,300\n3,name-3,bazz@foo.bar,asd"


@override_settings(API_KEY="test-key")
class ImportUploadApiTest(APITestCase):
    @patch("processor.api.process_import")
    def test_upload_creates_job_and_returns_id(self, mock_task):
        file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")

        response = self.client.post(
            "/api/imports/",
            {"file": file},
            format="multipart",
            HTTP_X_API_KEY="test-key",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)
        self.assertTrue(ImportJob.objects.filter(id=response.data["id"]).exists())

    def test_upload_without_file_returns_400(self):
        response = self.client.post(
            "/api/imports/",
            {},
            format="multipart",
            HTTP_X_API_KEY="test-key",
        )
        self.assertEqual(response.status_code, 400)


@override_settings(API_KEY="test-key")
class ImportStatusApiTest(APITestCase):
    def test_status_returns_expected_fields(self):
        job = ImportJob.objects.create(
            file="imports/test.csv",
            status=ImportStatus.PROCESSING,
            total_rows=100,
            processed_rows=50,
            failed_rows=10,
            success_rows=50,
        )

        response = self.client.get(f"/api/imports/{job.id}/", HTTP_X_API_KEY="test-key")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], ImportStatus.PROCESSING)
        self.assertEqual(response.data["progress"], 50)
        self.assertEqual(response.data["total_rows"], 100)
        self.assertEqual(response.data["processed_rows"], 50)
        self.assertEqual(response.data["success_rows"], 50)
        self.assertEqual(response.data["failed_rows"], 10)
        self.assertEqual(response.data["error"], "")

        created_at = parse_datetime(response.data["created_at"])
        updated_at = parse_datetime(response.data["updated_at"])
        self.assertIsNotNone(created_at)
        self.assertIsNotNone(updated_at)

    def test_status_returns_404_for_unknown_job(self):
        response = self.client.get(
            "/api/imports/00000000-0000-0000-0000-000000000000/",
            HTTP_X_API_KEY="test-key",
        )
        self.assertEqual(response.status_code, 404)


@override_settings(API_KEY="test-key")
class CSVProcessorTest(TestCase):
    def _make_job(self, csv_content: bytes) -> ImportJob:
        file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
        return ImportJob.objects.create(file=file)

    def test_all_valid_rows_counted_as_success(self):
        job = self._make_job(csv_content)
        CSVProcessor(job).run()

        job.refresh_from_db()
        self.assertEqual(job.status, ImportStatus.COMPLETED)
        self.assertEqual(job.total_rows, 2)
        self.assertEqual(job.success_rows, 2)
        self.assertEqual(job.failed_rows, 0)

    def test_invalid_rows_counted_as_failed(self):
        job = self._make_job(csv_content_with_errors)
        CSVProcessor(job).run()

        job.refresh_from_db()
        self.assertEqual(job.status, ImportStatus.COMPLETED)
        self.assertEqual(job.failed_rows, 3)
        self.assertEqual(job.success_rows, 0)

    def test_status_transitions_to_processing_then_completed(self):
        job = self._make_job(csv_content)
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
