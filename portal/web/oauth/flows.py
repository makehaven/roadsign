import oauth2client.client
from django.conf import settings
from django.urls import reverse


def get_google_flow(request):
    return oauth2client.client.OAuth2WebServerFlow(
        client_id=settings.GOOGLE_OPENIDCONNECT_KEY,
        client_secret=settings.GOOGLE_OPENIDCONNECT_SECRET,
        scope='openid email',
        redirect_uri=request.build_absolute_uri(reverse(
            "oauth_complete", kwargs={"provider": "google"}
        )),
        access_type="online",
    )