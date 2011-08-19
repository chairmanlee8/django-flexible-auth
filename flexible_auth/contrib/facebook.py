from django.shortcuts import redirect
from django.conf import settings
from django.core.urlresolvers import reverse

import urllib2

class FacebookProvider():
    SERVICE_NAME = 'facebook'    
    REQUEST_URL = "https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s"
    ACCESS_URL = "https://graph.facebook.com/oauth/access_token?client_id=%s&redirect_uri=%s&client_secret=%s&code=%s"
    
    @classmethod
    def get_view(cls, step):
        from ..models import AuthLink
        step = int(step)
        
        def _1(request):
            callback_uri = "http://" + request.get_host() + reverse('flexible_auth:auth-process', args=[cls.SERVICE_NAME, step+1])
            return redirect(cls.REQUEST_URL % (settings.FACEBOOK_APP_ID, callback_uri))
        
        def _2(request):
            # get access token
            code = request.GET.get('code')
            callback_uri = "http://" + request.get_host() + reverse('flexible_auth:auth-process', args=[cls.SERVICE_NAME, step])
            uri = cls.ACCESS_URL % (settings.FACEBOOK_APP_ID, callback_uri, settings.FACEBOOK_APP_SECRET, code)
            response = urllib2.urlopen(uri)
            response_data = response.read()
            
            # parse response data
            response_parms = dict([tuple(x.split('=')) for x in response_data.split('&')])
            expires = response_parms.get('expires', None)
            
            # associate fb to user
            als = AuthLink.objects.filter(user=request.user, service_name=cls.SERVICE_NAME)
            for al in als:
                als.delete()
                
            if not expires:
                expiretime = None
            else:
                expiretime = datetime.now() + timedelta(seconds=int(expires))
                
            al = AuthLink(user=request.user, service_name=cls.SERVICE_NAME, params=response_data, ready=True, expires=expiretime)
            al.save()
            
            return redirect(settings.FACEBOOK_RETURN_URL)

        return [_1,_2][step]
        
