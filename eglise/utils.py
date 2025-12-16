def check_all_vip_expiration():
    from .models import VIPSubscription
    for vip in VIPSubscription.objects.all():
        vip.check_expiration()
