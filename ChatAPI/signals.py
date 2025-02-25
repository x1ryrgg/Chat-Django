import os
import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from ChatAPI.models import User

logger = logging.getLogger(__name__)



@receiver(pre_delete, sender=User)
def delete_user_image(sender, instance, **kwargs):
    if instance.image:
        os.remove(instance.image.path)
        logger.info('Image %s deleted' % instance.image.url)









