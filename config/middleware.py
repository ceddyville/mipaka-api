from django.conf import settings
from django.http import JsonResponse


class RapidAPIProxyMiddleware:
    """
    Optional middleware that verifies requests come through the RapidAPI proxy.

    When RAPIDAPI_PROXY_SECRET is set, API requests must include a matching
    X-RapidAPI-Proxy-Secret header. This prevents users from bypassing
    RapidAPI (and your billing) by calling the Railway URL directly.

    Excluded paths (always allowed without the header):
      - /health/       (Railway healthcheck)
      - /admin/        (Django admin)
      - /api/docs/     (Swagger — useful for you to test)
      - /api/redoc/
      - /api/schema/
    """

    EXCLUDED_PREFIXES = ("/health", "/admin", "/api/docs",
                         "/api/redoc", "/api/schema")

    def __init__(self, get_response):
        self.get_response = get_response
        self.proxy_secret = getattr(settings, "RAPIDAPI_PROXY_SECRET", "")

    def __call__(self, request):
        if self.proxy_secret and request.path.startswith("/api/v1/"):
            header = request.META.get("HTTP_X_RAPIDAPI_PROXY_SECRET", "")
            if header != self.proxy_secret:
                return JsonResponse(
                    {"error": "Access this API via RapidAPI",
                     "url": "https://rapidapi.com/ceddyville/api/mipaka"},
                    status=403,
                )
        return self.get_response(request)
