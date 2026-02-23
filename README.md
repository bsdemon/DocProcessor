# DocProcessor

Small full-stack CSV import service:

-   Upload CSV via API  
-   Process asynchronously with Celery  
-   Track progress and show final summary in a React UI

## Tech Stack

### Backend

-   Django + Django REST Framework
-   Celery (Redis broker)
-   PostgreSQL
-   Docker / Docker Compose

### Frontend

-   React + TypeScript (Vite)
-   SWR for polling

------------------------------------------------------------------------

## 1) Setup Instructions

### Prerequisites

-   Docker
-   Docker Compose

### Environment variables

**Frontend** - Copy `frontend/.env_example` to `frontend/.env` - Default
example values are suitable for local development.

**Backend** Copy `backend/.env_example` to `backend/.env` - Default
example values are suitable for local development.

- SECRET_KEY – Django secret key used for cryptographic signing.
- DEBUG – Enables Django debug mode (True/False).
- ALLOWED_HOSTS – Comma-separated list of allowed hostnames.
- POSTGRES_DB – Name of the PostgreSQL database.
- POSTGRES_USER – PostgreSQL database user.
- POSTGRES_PASSWORD – Password for the PostgreSQL user.
- POSTGRES_HOST – PostgreSQL host (service name in Docker network).
- POSTGRES_PORT – PostgreSQL port (usually 5432).
- CELERY_BROKER_URL – Redis (or RabbitMQ) URL used by Celery as broker.
- CELERY_RESULT_BACKEND – Backend used by Celery to store task results.
- API_KEY – Pre-shared API key used for simple request authentication.

------------------------------------------------------------------------

## 2) How to Run the Project

### Development (recommended)

``` bash
cd docprocessor_app
docker compose -f docker/docker-compose.yml up --build
```

### Services

-   Frontend: http://localhost:5173  
-   Backend API: http://localhost:8000  

### Run Tests

``` bash
docker compose -f docker/docker-compose.yml exec web uv run python manage.py test
```

------------------------------------------------------------------------

## 3) Brief Explanation of Engineering Decisions

### ImportJob as Single Source of Truth

The entire import lifecycle is modeled as an `ImportJob` record
containing:

-   status (pending, processing, completed, failed)
-   total_rows, processed_rows, success_rows, failed_rows
-   error message
-   timestamps

This keeps the frontend simple: it polls a single endpoint to render
complete state.

### Single-File UI with Multi-Job Backend

The system currently supports uploading one file at a time via the UI.
However, the backend architecture supports multiple concurrent import jobs, since each upload creates an independent `ImportJob` processed asynchronously by Celery.

This keeps the UI simple while maintaining backend scalability.

### Asynchronous Processing with Celery

File upload only creates a job and stores the file. Processing is
delegated to Celery.

Benefits: - API stays responsive - Heavy I/O and CPU work runs outside
request thread - Progress can be tracked independently

### transaction.on_commit Before Enqueue

Celery tasks are scheduled inside `transaction.on_commit(...)` to avoid
race conditions where the worker starts before the DB transaction is
committed.

### Batch Progress Updates

Progress is written to the database every N rows (`BATCH_SIZE`). This
reduces write amplification while still providing near real-time UX
feedback.

### Accurate Row-Based Progress (Streaming Double Pass)

total_rows is computed using a streaming pass over the file, followed by a second streaming pass for processing.
Trade-off:
- Accurate row-based progress reporting
- One additional I/O pass over the file

### Validation Separation

File type, header validation and row validation are separated for clarity,
testability, and maintainability.

### Simple API-Key Guard

A minimal `X-API-KEY` permission is implemented. It is intentionally
simple and appropriate for the scope of this task.

------------------------------------------------------------------------

## 4) What I Would Improve with More Time

### Idempotent Import Handling

Introduce idempotency support (e.g. file hash or client-generated idempotency key)
to prevent accidental duplicate imports when users retry uploads.

### Extensibility (Processor Abstraction)

- Define a `DocumentProcessor` contract via a Python `Protocol`.
- Add a small processor registry/factory to resolve the correct processor by file type (e.g. CSV, XLSX, PDF),
  keeping the Celery task and service layer generic and avoiding format-specific branching.

### Performance

-   Avoid the current double file pass (count rows + process).
-   Adaptive batch sizes for very large files.
-   Further reduce DB writes under heavy load.

### Concurrency & Backpressure Control

Introduce limits on concurrent import jobs to prevent resource exhaustion.
Potentially use queue prioritization or worker pool isolation.

### Granular Failure Modeling

Distinguish between validation failures, system failures,
and infrastructure failures (e.g. broker unavailable).
Provide clearer failure states in the API.

### Handling Duplicate IDs

Duplicate IDs within the same CSV file should be handled explicitly.
A clear and consistent policy must be defined (e.g. fail the row, ignore subsequent duplicates, or apply last-write-wins semantics),
depending on the business requirements.

### Observability

-   Structured logging with `job_id` correlation.
-   Metrics (rows/sec, runtime, queue delay).
-   Store row-level validation errors (first N errors).

### Frontend Validation

- Validate file type before upload (only allow `.csv`).
- Add file size limits with clear error messaging.
- Basic client-side CSV header validation before sending to backend.
- Improve inline error messages and form feedback.

### UX Improvements

-   Replace polling with Server-Sent Events (SSE) or WebSockets.
-   Show estimated time remaining based on throughput.

### Production Hardening

-   File size limits and encoding validation.
-   Proper authentication (JWT or session-based).
-   Retry strategy + dead-letter queue for Celery.
-   Watchdog task to mark stuck jobs as failed.

### Testing

-   More API edge case tests (invalid headers, empty files, permission
    failures).
-   Explicit timestamp assertions.
-   Load testing for large CSV files.

------------------------------------------------------------------------

## Total Time Spent

~ 40 hours
