from rest_framework.throttling import AnonRateThrottle


class SmartAnonThrottle(AnonRateThrottle):
    """
    Custom throttle that skips rate-limiting for RapidAPI-proxied requests.

    RapidAPI enforces its own per-subscriber rate limits, so double-throttling
    would cause false 429s. For direct (non-RapidAPI) anonymous traffic, the
    standard IP-based anon throttle still applies.
    """

    def allow_request(self, request, view):
        # RapidAPI-proxied requests carry this header — trust RapidAPI's
        # own rate-limiting instead of applying Django's.
        if request.META.get("HTTP_X_RAPIDAPI_PROXY_SECRET"):
            return True
        return super().allow_request(request, view)
