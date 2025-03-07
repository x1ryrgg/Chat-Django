import json
from random import randint
from time import sleep

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer, JsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from .models import *
from .serializers import MessageSerializer

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.chat_id = self.scope['url_route']['kwargs']['chat_id']
            self.room_group_name = f'chat_{self.chat_id}'
            self.user = self.scope['user']

            # Проверка аутентификации
            if isinstance(self.user, AnonymousUser):
                await self.close()
                return

            # Проверка существования чата
            chat_exists = await database_sync_to_async(Chat.objects.filter(id=self.chat_id).exists)()
            if not chat_exists:
                await self.close()
                return

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            await self.close()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message')

            # Проверка наличия текста сообщения
            if not message:
                return

            # Создание сообщения
            chat = await database_sync_to_async(Chat.objects.get)(id=self.chat_id)
            new_message = await database_sync_to_async(Message.objects.create)(
                chat=chat,
                sender=self.user,
                body=message
            )

            # Отправка сообщения в группу
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.user.username,
                    'timestamp': new_message.created_at.isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Message receive error: {str(e)}")
            await self.close()

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'sender': event['sender'],
                'timestamp': event['timestamp']
            }))
        except Exception as e:
            logger.error(f"Message send error: {str(e)}")


class TestConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        for i in range(1000):
            self.send(json.dumps({'message': randint(1, 100)}))
            sleep(1)