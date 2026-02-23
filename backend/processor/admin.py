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

    readonly_fields = [field.name for field in ImportJob._meta.fields]
