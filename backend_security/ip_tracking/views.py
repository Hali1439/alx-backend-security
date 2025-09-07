# ip_tracking/views.py
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django_ratelimit.decorators import ratelimit

# Authenticated: 10 requests/min
# Anonymous: 5 requests/min
@ratelimit(key='ip', rate='5/m', method='GET', block=True)
def public_view(request):
    return HttpResponse("This is an anonymous view with rate limit 5 req/min.")

@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def login_view(request):
    return HttpResponse("Login attempt (max 10 req/min per IP)")
