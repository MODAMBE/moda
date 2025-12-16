import os
import django

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# ======================================================
# ⚙️ Configuration Django
# ======================================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ModApp.settings')

# Initialise Django
django.setup()

# Application ASGI HTTP
django_asgi_app = get_asgi_application()

# Import du routing WebSocket APRÈS l'initialisation
from eglise import routing as eglise_routing

# ======================================================
# 🚀 Application ASGI principale (HTTP + WebSocket)
# ======================================================
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                eglise_routing.websocket_urlpatterns
            )
        )
    ),
})

