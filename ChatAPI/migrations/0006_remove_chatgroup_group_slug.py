# Generated by Django 5.1.5 on 2025-01-23 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ChatAPI', '0005_alter_chatgroup_group_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatgroup',
            name='group_slug',
        ),
    ]
