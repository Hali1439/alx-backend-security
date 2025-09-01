# ip_tracking/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from ip_tracking.models import RequestLog, SuspiciousIP

@shared_task
def detect_suspicious_ips():
    """
    Flags IPs with:
    - More than 100 requests in the last hour
    - Accessing sensitive paths like /admin or /login
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # 1. Detect high request volume
    request_counts = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(count=models.Count('id'))
    )

    for rc in request_counts:
        if rc['count'] > 100:
            SuspiciousIP.objects.get_or_create(
                ip_address=rc['ip_address'],
                defaults={'reason': f"High request volume: {rc['count']} requests in last hour"}
            )

    # 2. Detect access to sensitive paths
    sensitive_paths = ['/admin', '/login']
    suspicious_logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago, path__in=sensitive_paths)

    for log in suspicious_logs:
        SuspiciousIP.objects.get_or_create(
            ip_address=log.ip_address,
            defaults={'reason': f"Accessed sensitive path: {log.path}"}
        )
