from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def date(value):
    if value:
        value = timezone.datetime.fromisoformat(value)
    return value.strftime('%Y-%m-%d')