from __future__ import annotations

from django.conf import settings
from rest_framework.permissions import BasePermission
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
        print(f"Expected API key: {expected}")
        if not expected:
            return False

        provided = request.META.get(self.header_name, "") or ""
        return provided == expected
