from django.urls import path, re_path
from twisted.test.test_ftp import TestConsumer

from . import consumers
from .consumers import ChatConsumer, TestConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_id>\d+)/$', consumers.ChatConsumer.as_asgi()),

    path('ws/test/', TestConsumer.as_asgi()),
]