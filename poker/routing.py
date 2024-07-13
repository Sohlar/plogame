from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/poker/(?P<room_name>\w+)/$", consumers.PokerConsumer.as_asgi()),
]

print("poker routing initialized")
