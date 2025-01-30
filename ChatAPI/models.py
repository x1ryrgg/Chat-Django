from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import ForeignKey
from unidecode import unidecode
from django.utils.text import slugify


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Имя пользователя ')
    date_birth = models.DateField(blank=True, null=True, verbose_name="Дата рождения")

    def __str__(self):
        return f"Ник: {self.username} | ID: {self.pk} | Email: {self.email}"


class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, verbose_name="Название чата")
    group_users = models.ManyToManyField(User, verbose_name="Пользователи чата")


    class Meta:
        verbose_name = "Название чата"
        verbose_name_plural = "Названия чатов"

    def __str__(self):
        return f"Название группы: {self.group_name}"


class GroupMessage(models.Model):
    group = ForeignKey(ChatGroup, on_delete=models.CASCADE, verbose_name="Группа")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    body = models.CharField(max_length=324, verbose_name="Сообщение",)
    date_sent = models.DateTimeField(auto_now_add=True, verbose_name="Созданно")

    class Meta:
        verbose_name = "Группа_сообщения"
        verbose_name_plural = "Группы_сообщения"
        ordering = ["date_sent"]

    def __str__(self):
        return f"Название группы: {self.group.group_name} | Пользователь: {self.sender} | Сообщение: {self.body} '\n' "


class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь_1", related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь_2", related_name="receiver")
    body = models.CharField(max_length=324, verbose_name="Сообщение")
    time_sent = models.DateTimeField(auto_now_add=True, verbose_name="Созданно")

    class Meta:
        verbose_name = 'Личное_сообщения'
        verbose_name_plural = 'Личные_сообщения'
        ordering = ["-time_sent"]

    def __str__(self):
        return f"Пользователь_1: {self.sender} | Пользователь_2: {self.receiver} | Сообщение: {self.body} '\n' "
