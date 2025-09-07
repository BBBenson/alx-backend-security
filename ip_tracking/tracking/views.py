from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m')
@ratelimit(key='user', rate='10/m')
def login_view(request):
    # Your login logic here
    return render(request, 'login.html')