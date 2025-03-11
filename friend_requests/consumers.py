import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}_notifications"

        # Присоединяемся к группе уведомлений пользователя
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Отключаемся от группы уведомлений
        await self.channel_layer.group_discard(
            f"user_{self.user_id}_notifications",
            self.channel_name
        )

    async def send_notification(self, event):
        # Отправляем уведомление клиенту
        notification = event['notification']

        await self.send(text_data=json.dumps({
            'type': notification['type'],
            'content': notification['content'],
            'created_at': notification['created_at']
        }))
