# Generated by Django 5.1.5 on 2025-02-15 10:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChatAPI', '0002_alter_directmessage_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='directmessage',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='ChatAPI.directmessage'),
        ),
        migrations.AddField(
            model_name='groupmessage',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='ChatAPI.groupmessage'),
        ),
    ]
