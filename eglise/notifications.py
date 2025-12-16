# eglise/notifications.py
from pyfcm import FCMNotification

# Ne crée pas de push_service à la volée au niveau global
# On va le créer directement dans la fonction

def envoyer_notification_push(utilisateur, titre, message):
    """
    Envoi d'une notification push via FCM.
    utilisateur.profile.fcm_token doit contenir le token FCM de l'utilisateur.
    """
    fcm_token = getattr(utilisateur.profile, 'fcm_token', None)
    if not fcm_token:
        print(f"[Notification] Pas de token FCM pour {utilisateur.username}. Message: {titre} - {message}")
        return

    # Créer le service FCM ici
    push_service = FCMNotification(api_key="TON_API_KEY")  # Remplace "TON_API_KEY" par ta vraie clé

    result = push_service.notify_single_device(
        registration_id=fcm_token,
        message_title=titre,
        message_body=message
    )
    print(f"[Notification] Envoyée à {utilisateur.username} : {result}")
