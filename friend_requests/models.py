from django.db import models
from django.utils.translation import gettext_lazy as _
from ChatAPI.models import *


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='from_request', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_request', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user} -> {self.to_user}'



