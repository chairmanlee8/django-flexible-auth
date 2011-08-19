from django.conf.urls.defaults import patterns, include, url
from views import auth_process, auth_unprocess

urlpatterns = patterns('',
    url(r'(?P<provider>\w+)/unlink/$',          auth_unprocess, name='auth-unlink'),
    url(r'(?P<provider>\w+)/(?P<step>\d+)/$',   auth_process,   name='auth-process'),
    url(r'(?P<provider>\w+)/$',                 auth_process,   name='auth-process'),
)
