from django.contrib import admin
from .models import *


admin.site.register(GroupMessage)

admin.site.register(User)

admin.site.register(DirectMessage)

admin.site.register(ChatGroup)