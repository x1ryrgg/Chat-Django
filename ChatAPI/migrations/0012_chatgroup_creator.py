# Generated by Django 5.1.5 on 2025-02-01 17:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChatAPI', '0011_alter_groupmessage_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatgroup',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Создатель чата'),
        ),
    ]
