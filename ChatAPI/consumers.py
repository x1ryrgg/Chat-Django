import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import transaction

from .models import User
from .models import GroupMessage, ChatGroup

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        # Проверяем, является ли пользователь участником чата
        user = self.scope['user']
        chat = await self.get_chat(self.chat_id)
        if user not in await self.get_users(chat):
            return

        # Присоединяемся к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Отключаемся от группы комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = self.scope['user']

        # Сохраняем сообщение в базу данных
        group_message = await self.save_message(sender, self.chat_id, message)

        # Отправляем сообщение всем участникам группы
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': group_message.body,
                'sender': group_message.sender.username,
                'date_sent': group_message.date_sent.isoformat(),
                'sender_id': group_message.sender.id
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        date_sent = event['date_sent']
        sender_id = event['sender_id']

        # Отправляем сообщение клиенту
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'date_sent': date_sent,
            'sender_id': sender_id
        }))

    @transaction.atomic
    async def save_message(self, sender, chat_id, message):
        chat = await self.get_chat(chat_id)
        return await database_sync_to_async(GroupMessage.objects.create)(
            group=chat,
            sender=sender,
            body=message
        )

    @database_sync_to_async
    def get_chat(self, chat_id):
        return ChatGroup.objects.get(id=chat_id)

    @database_sync_to_async
    def get_users(self, chat):
        return list(chat.group_users.all())
