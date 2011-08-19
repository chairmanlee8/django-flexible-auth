# TODO: revamp this code. Needs to be more generic.
from contrib import facebook, twitter, google
    
PROVIDERS = {
    'facebook':     ('Facebook',    facebook.FacebookProvider),
    'twitter':      ('Twitter',     twitter.TwitterProvider),
    'google':       ('Google',      google.GoogleProvider),
}