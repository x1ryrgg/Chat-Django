import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import transaction

from .models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']
        reply_to_id = text_data_json.get('reply_to')  # Получаем ID родительского сообщения

        sender = await self.get_user(sender_id)
        group = await self.get_chat(self.chat_id)

        # Сохраняем сообщение
        new_message = await self.save_message(group, sender, message, reply_to_id)

        # Отправляем сообщение всем участникам чата
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': new_message.body,
                'sender': new_message.sender.username,
                'date_sent': new_message.date_sent.isoformat(),
                'sender_id': new_message.sender.id,
                'reply_to': new_message.reply_to.id if new_message.reply_to else None,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        date_sent = event['date_sent']
        sender_id = event['sender_id']
        reply_to_id = event['reply_to']

        # Отправляем сообщение клиенту
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'date_sent': date_sent,
            'sender_id': sender_id,
            'reply_to': reply_to_id,
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def get_chat(self, chat_id):
        return ChatGroup.objects.get(id=chat_id)

    @database_sync_to_async
    def save_message(self, group, sender, body, reply_to_id=None):
        reply_to = GroupMessage.objects.get(id=reply_to_id) if reply_to_id else None
        return GroupMessage.objects.create(group=group, sender=sender, body=body, reply_to=reply_to)