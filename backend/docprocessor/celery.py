import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "docprocessor.settings")

app = Celery("docprocessor")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
