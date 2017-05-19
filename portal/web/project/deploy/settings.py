'''
-*- Production Settings -*-

This file contains production-specific settings. Complete the deployment
checklist and make any necessary changes.

https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/
'''

from .common_settings import *


# When DEBUG is off (ie, for production), these email addresses will receive
# an email for any unhandled exceptions while processing a request. See the
# logging configuration in common_settings for how that is set up.
ADMINS = [
    # ('Admin Name', 'admin.email@example.com'),
]

# To force SSL if the upstream proxy server doesn't do it for us, set to True
SECURE_SSL_REDIRECT = False


# Django's development server will automatically serve static files for you,
# but in production, Django expects your web server to take care of that. You
# will need to set STATIC_ROOT to a directory on your filesystem, and
# STATIC_URL to something like "/static/". Then configure your webserver to
# serve that directory at that url.
# Finally, run "manage.py collectstatic" and django will copy static files
# from various places into your STATIC_ROOT. You need to re-run collectstatic
# each time you redeploy with changes to static files.
STATIC_ROOT = path('static-root')

# manifest storage is useful for its automatic cache busting properties
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'


# Set your MEDIA_ROOT to some directory that's writable by your web server if
# your app involves writing to the filesystem using the default storage class
MEDIA_ROOT = path('media-root')
