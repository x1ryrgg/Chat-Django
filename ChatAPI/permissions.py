from django.shortcuts import get_object_or_404
from rest_framework import permissions
from ChatAPI.models import Chat


class IsAdmin(permissions.BasePermission):
    """
    Разрешение, которое позволяет использовать ресурс только администраторам чата.
    """

    def has_permission(self, request, view):
        chat_id = view.kwargs.get('chat_id')
        if not chat_id:
            return False

        chat = get_object_or_404(Chat, id=chat_id)

        return request.user != chat.creator