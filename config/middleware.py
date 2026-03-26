import logging
import time

from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger("mipaka.api")


class RequestLoggingMiddleware:
    """
    Logs every /api/ request with method, path, status, duration, and
    the RapidAPI subscriber (if present).  Skips /health/ to avoid noise.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start) * 1000

        subscriber = request.META.get("HTTP_X_RAPIDAPI_USER", "direct")
        logger.info(
            "%s %s %s %.0fms subscriber=%s",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            subscriber,
        )
        return response


class RapidAPIProxyMiddleware:
    """
    Optional middleware that verifies requests come through the RapidAPI proxy.

    When RAPIDAPI_PROXY_SECRET is set, API requests must include a matching
    X-RapidAPI-Proxy-Secret header. This prevents users from bypassing
    RapidAPI (and your billing) by calling the Railway URL directly.

    Bypassed for:
      - Requests originating from mipaka.dev (landing page explorer)
      - /health/, /admin/, /api/docs/, /api/redoc/, /api/schema/
    """

    ALLOWED_ORIGINS = (
        "https://mipaka.dev",
        "http://mipaka.dev",
        "https://www.mipaka.dev",
    )

    def __init__(self, get_response):
        self.get_response = get_response
        self.proxy_secret = getattr(settings, "RAPIDAPI_PROXY_SECRET", "")

    def _is_allowed_origin(self, request):
        origin = request.META.get("HTTP_ORIGIN", "")
        referer = request.META.get("HTTP_REFERER", "")
        # Allow file:// and localhost origins for local development
        if origin in ("null", "") and not referer:
            return False
        for allowed in self.ALLOWED_ORIGINS:
            if origin == allowed or referer.startswith(allowed):
                return True
        return False

    def __call__(self, request):
        if self.proxy_secret and request.path.startswith("/api/v1/"):
            if self._is_allowed_origin(request):
                return self.get_response(request)
            header = request.META.get("HTTP_X_RAPIDAPI_PROXY_SECRET", "")
            if header != self.proxy_secret:
                return JsonResponse(
                    {"error": "Access this API via RapidAPI",
                     "url": "https://rapidapi.com/ceddyville/api/mipaka"},
                    status=403,
                )
        return self.get_response(request)
