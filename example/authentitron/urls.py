from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from views import login_django, logout_django

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$',              direct_to_template, {'template': 'index.html'},         name='home'),
    url(r'^login-view/$',   direct_to_template, {'template': 'login_django.html'},  name='login-view'),
    url(r'^login/$',        login_django,                                           name='login'),
    url(r'^logout/$',       logout_django,                                          name='logout'),
    url(r'^auth/',          include('flexible_auth.urls', namespace='flexible_auth')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
