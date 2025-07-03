import os
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# ✅ Set the correct Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Settlex.settings')

# ✅ Ensure Django is fully loaded before importing anything else
django.setup()

# ✅ Now import WebSocket routes AFTER Django is set up
from settlements_app.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

