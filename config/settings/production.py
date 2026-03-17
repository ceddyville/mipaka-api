from .base import *

DEBUG = False

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Tighten CORS in production — update once you have a real domain
CORS_ALLOWED_ORIGINS = [
    # "https://mipaka.dev",
]
CORS_ALLOW_ALL_ORIGINS = False
