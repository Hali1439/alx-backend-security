# ip_tracking/middleware.py
from django.http import HttpResponseForbidden
from django.utils.timezone import now
from django.core.cache import cache
from ipgeolocation import ipgeolocation

from .models import BlockedIP, RequestLog

class IPLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)

        # 1️⃣ Block blacklisted IPs
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP is blocked.")

        # 2️⃣ Get geolocation (cached for 24h)
        geo_data = cache.get(ip)
        if not geo_data:
            geo_data = ipgeolocation.get_location(ip)
            cache.set(ip, geo_data, 60 * 60 * 24)  # cache for 24h

        # 3️⃣ Log request with geolocation
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            timestamp=now(),
            country=geo_data.get("country_name"),
            city=geo_data.get("city")
        )

        return self.get_response(request)

    def get_client_ip(self, request):
        """Get client IP from request headers."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
