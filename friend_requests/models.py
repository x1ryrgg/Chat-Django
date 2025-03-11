from django.db import models
from django.utils.translation import gettext_lazy as _
from ChatAPI.models import *


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='from_request', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_request', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user} -> {self.to_user}'


class Notification(models.Model):
    class Type(models.TextChoices):
        MESSAGE = ('message', 'сообщение')
        REQUEST = ('request', 'запрос')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification')
    type = models.TextField(max_length=7, choices=Type.choices)
    content = models.TextField(max_length=100)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.type} -> {self.content[:50]}"


