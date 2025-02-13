from django.core.mail import send_mail

from Chat_Django import settings
from Chat_Django.celery import app
from celery import shared_task
from ChatAPI.models import User



@app.task
def send_message(username, email):
    send_mail(
        subject='Привет, тестовое сообщение.',
        message=f'сообщение от {username}, почта: {email}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False
    )

@app.task
def send_beat_message():
    send_mail(
        subject='Beat Message',
        message=f'Это спам рассылка приходит каждые 5 минут.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False
    )


@shared_task
def add(x, y):
    return x + y





