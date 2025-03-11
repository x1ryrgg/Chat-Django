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


@app.task(bind=True, default_retry_delay=5 * 60, max_retries=3)
def add_retry(self, x, y):
    try:
        return x + y
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


"""
вместо delay, который сразу включает таску можно использовать 
apply_async, в котором можно указать countdown, через какое время запустить таску
"""





