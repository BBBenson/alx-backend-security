from .models import RequestLog, BlockedIP

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Check if IP is blocked
        if BlockedIP.objects.filter(ip_address=ip).exists():
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("IP address blocked")
        
        # Log the request
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path
        )
        
        response = self.get_response(request)
        return response