from django.conf import settings


def add_site_settings(request):
    """
    Adds settings for customizing a tourney site to the context (for template
    rendering)
    """
    return {
        'SITE_NAME': settings.SITE_NAME
    }
