Quickstart
==========

This quickstart will give you an overview of the basic process of using django-flexible-auth.
You can load the example project ``authentitron`` from ``example/authentitron``.

.. note :: Facebook authentication will not work behind a local IP address or local loopback.

Dependencies
------------

* python-oauth2
* python-openid

Initial Setup
-------------

Before running the example project, we need to configure ``settings.py``. We have already added
``flexible_auth`` to the installed apps list, but due to the directory structure of this package,
you will need to create a symlink or hardlink to the ``flexible_auth`` app directory, two
directories above ``settings.py``, so that Django can see it from here.

Next you will need to put in keys and secrets for the social networking services at the bottom ::

    FACEBOOK_RETURN_URL =       '/'
    TWITTER_RETURN_URL =        '/'
    GOOGLE_RETURN_URL =         '/'
    FACEBOOK_APP_ID =           ''
    FACEBOOK_APP_SECRET =       ''
    TWITTER_CONSUMER_KEY =      ''
    TWITTER_CONSUMER_SECRET =   ''
    
The ``*_RETURN_URL`` simply tells `django-flexible-auth` where to redirect the user after
authenticating.

Finally, if you haven't done so, create a Django superuser, so you have something to log into. Once
you have finished these steps, you should be able to run a dev server via ``django-admin.py`` and
see it working.

Interacting with ``flexible_auth``
----------------------------------

If you look inside the urlconf for ``flexible_auth``, you will see that only two views are exposed,
via three url's.

auth_process
^^^^^^^^^^^^

``auth_process`` begins the process for linking a social account to the currently logged in Django
user. The url takes the format ``/<provider>/[step]``. Generally, you will always omit the ``step``
argument (and have it default to ``0``). There are no use cases which require the use of the ``step``
parameter. ``provider`` can be any key from the dictionary ``PROVIDERS`` inside ``providers.py`` ::

    PROVIDERS = {
        'facebook':     facebook.FacebookProvider,
        'twitter':      twitter.TwitterProvider,
        'google':       google.GoogleProvider,
    }
    
Simply call this view from anywhere in your code to begin the account linking process.

auth_unprocess
^^^^^^^^^^^^^^

The ``auth_unprocess`` view is even simpler. Simply call ``/<provider>/unlink`` to unlink a provider
account from the current user.

