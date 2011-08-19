from django.shortcuts import redirect
from django.conf import settings
from django.core.urlresolvers import reverse

import urllib2
import oauth2

class TwitterProvider():
    SERVICE_NAME = 'twitter'
    REQUEST_URL = "https://api.twitter.com/oauth/request_token"
    AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token=%s"
    ACCESS_URL = "https://api.twitter.com/oauth/access_token"
    
    @classmethod
    def get_view(cls, step):
        from ..models import AuthLink
        step = int(step)
        
        def _1(request):
            consumer = oauth2.Consumer(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
            oauth_callback = "http://" + request.get_host() + reverse('flexible_auth:auth-process', args=[cls.SERVICE_NAME, step+1])
            oauth_request = oauth2.Request.from_consumer_and_token(consumer, parameters={'oauth_callback': oauth_callback}, http_url=cls.REQUEST_URL)
            oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, None)
            
            print oauth_request.to_header()
            uri_request = urllib2.Request(cls.REQUEST_URL, headers=oauth_request.to_header())
            connection = urllib2.urlopen(uri_request)
            response = connection.read()
            
            token = oauth2.Token.from_string(response)
            
            # create temp object
            als = AuthLink.objects.filter(user=request.user, service_name=cls.SERVICE_NAME)
            for al in als:
                als.delete()
                
            al = AuthLink(user=request.user, service_name=cls.SERVICE_NAME, params=response)
            al.save()
            
            return redirect(cls.AUTHORIZE_URL % token.key)
            
        def _2(request):
            al = AuthLink.objects.get(user=request.user, service_name=cls.SERVICE_NAME)
            
            oauth_token = oauth2.Token.from_string(al.params)
            oauth_token.set_verifier(request.GET.get('oauth_verifier'))
            
            consumer = oauth2.Consumer(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
            oauth_request = oauth2.Request.from_consumer_and_token(consumer, token=oauth_token, http_url=cls.ACCESS_URL)
            oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, oauth_token)

            uri_request = urllib2.Request(cls.ACCESS_URL, headers=oauth_request.to_header())
            connection = urllib2.urlopen(uri_request)
            response = connection.read()
            
            al.params = response
            al.ready = True
            al.save()
            
            return redirect(settings.TWITTER_RETURN_URL)
            
        return [_1,_2][step]