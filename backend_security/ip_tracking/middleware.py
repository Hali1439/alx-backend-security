from django.utils import timezone
from .models import RequestLog
from ipware import get_client_ip   # pip install django-ipware


class IPLogMiddleware:
    """Middleware to log client IP, request path, and timestamp."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get client IP reliably (even behind proxies/load balancers)
        ip, is_routable = get_client_ip(request)
        if ip is None:
            ip = "0.0.0.0"  # fallback for unknown IPs

        # Save log
        RequestLog.objects.create(
            ip_address=ip,
            timestamp=timezone.now(),
            path=request.path,
        )

        response = self.get_response(request)
        return response
