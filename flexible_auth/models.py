from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .contrib._openid import *
from .contrib._oauth import *

from .providers import PROVIDERS

AUTH_PROVIDER_CHOICES = tuple([(k, v[0]) for k, v in PROVIDERS.items()])

# TODO: fix params so that the database is actually normalized. this will likely result in a big arch. change?
# But it should be okay since the only front-facing arch. decision is the views cycle and accessing user's providers.
# Maybe instead of central AuthLink model, have different tables, but that may be a nightmare. Or have AuthLink
# be a proxy to different models. Things to think about.

class AuthLink(models.Model):
    user            = models.ForeignKey(User)
    service_name    = models.CharField(max_length=64, null=False, choices=AUTH_PROVIDER_CHOICES)
    params          = models.CharField(max_length=512, blank=True, null=True)
    ready           = models.BooleanField(default=False)
    expires         = models.DateTimeField(null=True)
    
    def provider_name(self):
        return dict(AUTH_PROVIDER_CHOICES)[self.service_name]
    
class AuthLinkMeta(models.Model):
    user            = models.OneToOneField(User)
    
    def providers(self):
        return AUTH_PROVIDER_CHOICES

@receiver(post_save, sender=User)
def create_authlink_meta(sender, instance, created, **kwargs):
    # This is actually super wasteful. Maybe think of a better way.
    if created:
        meta, new = AuthLinkMeta.objects.get_or_create(user=instance)
