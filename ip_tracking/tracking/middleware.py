from django.core.cache import cache
from django.http import HttpResponseForbidden
from ipware import get_client_ip
import requests
from .models import RequestLog, BlockedIP

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get client IP using django-ipware
        ip, is_routable = get_client_ip(request)
        if ip is None:
            ip = "0.0.0.0"
        
        # Check if IP is blocked
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("IP address blocked")
        
        # Get geolocation data (cached for 24 hours)
        cache_key = f'geo_{ip}'
        geo_data = cache.get(cache_key)
        
        if not geo_data:
            try:
                # Using ipapi.co for geolocation (free tier available)
                response = requests.get(f'https://ipapi.co/{ip}/json/')
                if response.status_code == 200:
                    data = response.json()
                    geo_data = {
                        'country': data.get('country_name'),
                        'city': data.get('city')
                    }
                    cache.set(cache_key, geo_data, 86400)  # 24 hours
                else:
                    geo_data = {'country': None, 'city': None}
            except:
                geo_data = {'country': None, 'city': None}
        
        # Log the request
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            country=geo_data.get('country'),
            city=geo_data.get('city')
        )
        
        response = self.get_response(request)
        return response