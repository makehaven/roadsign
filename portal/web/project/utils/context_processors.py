
from django.conf import settings


def google_analytics(request):
    """
    Add Google Analytics tracking context
    """
    return {'GA': settings.GOOGLE_ANALYTICS_KEY}
