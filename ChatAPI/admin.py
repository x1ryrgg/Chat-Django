from django.contrib import admin
from .models import *


admin.site.register(GroupMessage)

@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    fields = ('group_name', )

    list_display = ('id', 'group_name', )
    list_display_links = ('id', )
    ordering = ("id",)

admin.site.register(User)

admin.site.register(DirectMessage)