# Generated by Django 5.1.5 on 2025-01-23 12:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChatAPI', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=128, verbose_name='Название чата')),
            ],
        ),
        migrations.CreateModel(
            name='GroupMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(max_length=324, verbose_name='Сообщение')),
                ('date_sent', models.DateTimeField(auto_now_add=True, verbose_name='Созданно')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ChatAPI.chatgroup', verbose_name='Группа')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]
