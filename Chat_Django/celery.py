import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Chat_Django.settings')

app = Celery('Chat_Django')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_beat_message': {
        'task': 'ChatAPI.tasks.send_beat_message',
        'schedule': crontab(minute='*/1'),
    },
}

