from django.urls import path, re_path

from . import consumers
from .views import *



urlpatterns = [
    path('', index, name='index'),

    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('chats/', ChatsView.as_view(), name='chats'),
    path('chat/<int:chat_id>/', GroupChatView.as_view(), name='chat'),
    path('direct/<int:user_id>/', DirectView.as_view(), name='direct'),

]