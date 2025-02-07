from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import ForeignKey
from unidecode import unidecode
from django.utils.text import slugify


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True, db_index=True, )
    date_birth = models.DateField(blank=True, null=True, )
    friends = models.ManyToManyField('self')

    def __str__(self):
        return f"Пользователь: {self.username}"


class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, )
    group_users = models.ManyToManyField(User, related_name="group_users")
    group_admin_users = models.ManyToManyField(User, related_name="group_admins")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Групповой чат"
        verbose_name_plural = "Групповые чаты"

    def __str__(self):
        return f"Групповой чат: {self.group_name}"

    def save(self, *args, **kwargs):
        # При создании чата автоматически назначаем создателя как админа
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new and self.creator:
            self.group_admin_users.add(self.creator)

class GroupMessage(models.Model):
    group = ForeignKey(ChatGroup, on_delete=models.CASCADE, )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, )
    body = models.CharField(max_length=324, verbose_name="Сообщение",)
    date_sent = models.DateTimeField(auto_now_add=True, )

    class Meta:
        verbose_name = "Группа_сообщения"
        verbose_name_plural = "Группы_сообщения"
        ordering = ["date_sent"]

    def __str__(self):
        return f"Название группы: {self.group.group_name} | Пользователь: {self.sender} | Сообщение: {self.body} '\n' "


class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    body = models.CharField(max_length=324)
    time_sent = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Личное_сообщения'
        verbose_name_plural = 'Личные_сообщения'
        ordering = ["-time_sent"]

    def __str__(self):
        return f"Пользователь_1: {self.sender} | Пользователь_2: {self.receiver} | Сообщение: {self.body} '\n' "
