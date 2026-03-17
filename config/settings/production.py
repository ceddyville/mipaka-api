import redis as _redis
from .base import *

DEBUG = False

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Tighten CORS in production — update once you have a real domain
CORS_ALLOWED_ORIGINS = [
    # "https://mipaka.dev",
]
CORS_ALLOW_ALL_ORIGINS = False

# Cache — use Redis if available, otherwise fall back to local memory
try:
    _r = _redis.from_url(
        config("REDIS_URL", default="redis://localhost:6379/0"))
    _r.ping()
except Exception:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
