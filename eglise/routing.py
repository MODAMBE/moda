from django.urls import re_path
from . import consumers

# ======================================
# WebSocket URL patterns
# ======================================
websocket_urlpatterns = [

    # Chat (messages)
    re_path(
        r"^ws/discussion/(?P<discussion_id>\w+)/$",
        consumers.ChatConsumer.as_asgi()
    ),

    # Appel Audio / Vidéo
    re_path(
        r"^ws/call/(?P<appel_id>\w+)/$",
        consumers.CallConsumer.as_asgi()
    ),
]
