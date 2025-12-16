from django.conf import settings

def adsense(request):
    return {
        "ADSENSE_CLIENT_ID": settings.ADSENSE_CLIENT_ID,
        "META_AUDIENCE_PLACEMENT_ID": settings.META_AUDIENCE_PLACEMENT_ID,
    }
