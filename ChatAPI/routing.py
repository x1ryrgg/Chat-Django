from django.urls import path

from . import consumers
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/chat/<int:chat_id>', ChatConsumer.as_asgi()),
]