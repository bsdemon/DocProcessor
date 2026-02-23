from django.contrib import admin

from .models import ImportJob


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "processed_rows",
        "failed_rows",
        "total_rows",
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "id",
        "file",
        "status",
        "total_rows",
        "processed_rows",
        "success_rows",
        "failed_rows",
        "error",
        "created_at",
        "updated_at",
    )
