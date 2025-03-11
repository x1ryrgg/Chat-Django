import os

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import ForeignKey
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from unidecode import unidecode
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from .managers import *


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True, db_index=True, )
    date_birth = models.DateField(blank=True, null=True, )
    image = models.ImageField(blank=True, null=True, upload_to='photo')
    friends = models.ManyToManyField('self', blank=True)
    email = models.EmailField(null=False, unique=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    def __str__(self):
        return f"User: {self.username}| pk: {self.pk}"


class Chat(models.Model):
    class Type(models.TextChoices):
        DIRECT = ('direct', 'директ')
        GROUP = ('group', 'группа')

    type = models.CharField(choices=Type.choices, default=Type.DIRECT, max_length=6)
    group_name = models.CharField(max_length=64, null=True, blank=True, default='noname_chat')
    members = models.ManyToManyField(User, related_name="members", blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="chat_creator")
    created_at = models.DateTimeField(auto_now_add=True)
    objects = ChatManager()

    def __str__(self):
        return f'Name: {self.group_name} | pk: {self.pk} | type: {self.type}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="chat")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_message")
    body = models.TextField(max_length=500, )
    created_at = models.DateTimeField(auto_now_add=True)
    objects = MessageManager()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Sender {self.sender} | message {self.body[:50]} in chat [{self.chat}]'




