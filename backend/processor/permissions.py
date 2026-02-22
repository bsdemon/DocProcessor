from __future__ import annotations

from django.conf import settings
from loguru import logger
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.views import APIView


class HasImportApiKey(BasePermission):
    """
    Very simple API-key guard.
    Client must send header: X-API-Key: <key>
    """

    header_name = "HTTP_X_API_KEY"

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in ("OPTIONS", "HEAD"):
            return True
        expected = getattr(settings, "API_KEY", "") or ""
        if not expected:
            logger.error("API_KEY is not configured on the server.")
            raise PermissionDenied("Server API key is not configured")

        provided = request.META.get(self.header_name, "") or ""
        if not provided:
            raise PermissionDenied("Missing API key")

        if provided != expected:
            raise PermissionDenied("Invalid API key")
        return True
