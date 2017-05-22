import django.contrib.auth.backends

from .models import OAuthUser


class OAuthBackend(django.contrib.auth.backends.ModelBackend):
    """A Django authorization backend that is used to log in a user from an
    OAuthUser object

    """
    def authenticate(self, oauthuser):
        if not isinstance(oauthuser, OAuthUser):
            return

        if oauthuser.user is not None:
            return oauthuser.user

