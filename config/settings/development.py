import redis as _redis
from .base import *

DEBUG = True

INSTALLED_APPS += ["django_extensions"]

# Looser throttling for local dev
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"anon": "10000/day"}

# Use console email backend in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Fall back to local-memory cache if Redis isn't running
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
