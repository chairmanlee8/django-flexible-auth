from django.shortcuts import redirect
from django.db import transaction
from django.conf import settings
from django.core.urlresolvers import reverse

import urllib2

# Some code adapted from Rok: http://stackoverflow.com/questions/4307677/django-google-federated-login

from openid.consumer.consumer import Consumer, \
    SUCCESS, CANCEL, FAILURE, SETUP_NEEDED
from openid.consumer.discover import DiscoveryFailure
from django.utils.encoding import smart_unicode
from _openid import DjangoOpenIDStore

class GoogleProvider():
    SERVICE_NAME = 'google'
    GOOGLE_APPS_URL = "https://www.google.com/accounts/o8/site-xrds?hd=%s"
    GOOGLE_URL = "https://www.google.com/accounts/o8/id"
    
    @classmethod
    def get_view(cls, step):
        from ..models import AuthLink
        step = int(step)
        
        def _1(request):
            consumer = Consumer(request.session, DjangoOpenIDStore())
            realm = "http://" + request.get_host()
            redirect_url = "http://" + request.get_host() + reverse('flexible_auth:auth-process', args=[cls.SERVICE_NAME, step+1])
            
            # catch Google Apps domain that is referring, if any 
            _domain = None
            if 'domain' in request.POST:
                _domain = request.POST['domain']
            elif 'domain' in request.GET:
                _domain = request.GET['domain']
                
            try:
                # two different endpoints depending on whether the using is using Google Account or Google Apps Account
                if _domain:
                    auth_request = consumer.begin(cls.GOOGLE_APPS_URL % _domain)
                else:
                    auth_request = consumer.begin(cls.GOOGLE_URL)
            except DiscoveryFailure as e:
                return CustomError(request, "Google Accounts Error", "Google's OpenID endpoint is not available.")
                
            # add requests for additional account information required, in this case: email, first name & last name + oauth token
            auth_request.addExtensionArg('http://openid.net/srv/ax/1.0', 'mode', 'fetch_request')
            auth_request.addExtensionArg('http://openid.net/srv/ax/1.0', 'required', 'email,firstname,lastname')
            auth_request.addExtensionArg('http://openid.net/srv/ax/1.0', 'type.email', 'http://schema.openid.net/contact/email')
            auth_request.addExtensionArg('http://openid.net/srv/ax/1.0', 'type.firstname', 'http://axschema.org/namePerson/first')
            auth_request.addExtensionArg('http://openid.net/srv/ax/1.0', 'type.lastname', 'http://axschema.org/namePerson/last')
            
            return redirect(auth_request.redirectURL(realm, redirect_url))
           
        @transaction.commit_manually
        def _2(request):
            """ Callback from Google Account service with login the status. Your url could be http://www.yourdomain.com/google-signin-response """
            transaction.rollback() # required due to Django's transaction inconsistency between calls
            oidconsumer = Consumer(request.session, DjangoOpenIDStore())

            # parse GET parameters submit them with the full url to consumer.complete
            _params = dict((k,smart_unicode(v)) for k, v in request.GET.items())
            info = oidconsumer.complete(_params, request.build_absolute_uri().split('?')[0])
            display_identifier = info.getDisplayIdentifier()

            if info.status == FAILURE and display_identifier:
                return CustomError(request, _("Google Login Error"), _("Verification of %(user)s failed: %(error_message)s") % {'user' : display_identifier, 'error_message' : info.message})

            elif info.status == SUCCESS:
                try:
                    _email = info.message.args[('http://openid.net/srv/ax/1.0', 'value.email')]
                    _first_name = info.message.args[('http://openid.net/srv/ax/1.0', 'value.firstname')]
                    _last_name = info.message.args[('http://openid.net/srv/ax/1.0', 'value.lastname')]
                    
                    # Create AuthLink and redirect
                    als = AuthLink.objects.filter(user=request.user, service_name=cls.SERVICE_NAME)
                    for al in als:
                        als.delete()
                        
                    # TODO: get an oauth token from google
                    al = AuthLink(user=request.user, service_name=cls.SERVICE_NAME, params='')
                    al.save()
                    transaction.commit()
                    
                    return redirect(settings.GOOGLE_RETURN_URL)
                except Exception as e:
                    transaction.rollback()
                    system_log_entry(e, request=request)
                    return CustomError(request, _("Login Unsuccessful"), "%s" % e)

            elif info.status == CANCEL:
                return CustomError(request, _("Google Login Error"), _('Google account verification cancelled.'))

            elif info.status == SETUP_NEEDED:
                if info.setup_url:
                    return CustomError(request, _("Google Login Setup Needed"), _('<a href="%(url)s">Setup needed</a>') % { 'url' : info.setup_url })
                else:
                    # This means auth didn't succeed, but you're welcome to try
                    # non-immediate mode.
                    return CustomError(request, _("Google Login Setup Needed"), _('Setup needed'))
            else:
                # Either we don't understand the code or there is no
                # openid_url included with the error. Give a generic
                # failure message. The library should supply debug
                # information in a log.
                return CustomError(request, _("Google Login Error"), _('Google account verification failed for an unknown reason. Please try to create a manual account on Acquee.'))
                    
        return [_1,_2][step]