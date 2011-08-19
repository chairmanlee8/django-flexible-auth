from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from .providers import *
from .models import AuthLink

def auth_process(request, provider, step=0):
    return PROVIDERS[provider][1].get_view(step)(request)
    
def auth_unprocess(request, provider):
    to = request.GET.get('redirect', '/')
    
    als = AuthLink.objects.filter(user=request.user, service_name=provider)
    for al in als:
        al.delete()
        
    return redirect(to)
    