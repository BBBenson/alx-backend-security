from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_suspicious_ips():
    # Check for IPs with more than 100 requests in the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    # Get IPs with high request volume
    high_volume_ips = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago
    ).values('ip_address').annotate(
        count=Count('id')
    ).filter(count__gt=100)
    
    for ip_data in high_volume_ips:
        ip = ip_data['ip_address']
        SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            defaults={'reason': f'High request volume: {ip_data["count"]} requests in 1 hour'}
        )
    
    # Check for access to sensitive paths
    sensitive_paths = ['/admin/', '/login/']
    sensitive_access = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago,
        path__in=sensitive_paths
    ).values('ip_address').annotate(
        count=Count('id')
    ).filter(count__gt=5)  # More than 5 accesses to sensitive paths
    
    for ip_data in sensitive_access:
        ip = ip_data['ip_address']
        SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            defaults={'reason': f'Multiple accesses to sensitive paths: {ip_data["count"]} times'}
        )