'''
-*- Development Settings -*-

This file contains development-specific settings. You can run the django
development server without making any changes to this file, but it's not
suitable for production. The production settings files are located under
the './deploy' directory.
'''

from .common_settings import *


# Set your MEDIA_ROOT to a directory that does not already exist.
MEDIA_ROOT = path('files')
