from django.contrib import admin
from .models import ImportJob


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "processed_rows",
        "total_rows",
        "created_at",
    )
