"""
ASGI config for plo_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from poker import routing


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plo_project.settings")

print("ASGI Application starting")
print(f"Websocket URL patterns: {routing.websocket_urlpatterns}")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns)),
    }
)

print("ASGI application configured")
