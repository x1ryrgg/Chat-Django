from django.urls import path, re_path

from . import consumers
from .views import *



urlpatterns = [
    path('', index, name='index'),

    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('chats/', ChatsView.as_view(), name='chats'),

    path('create-chat/', GroupChatCreateView.as_view(), name='create-chat'),
    path('chat/<int:chat_id>/leave/', LeaveGroupChat.as_view(), name='leave'),
    path('chat/<int:chat_id>/', GroupChatView.as_view(), name='chat'),
    path('chat/<int:chat_id>/peer/', PeerGroupChatView.as_view(), name='peer'),
    path('chat/<int:chat_id>/peer/delete_chat/', DeleteGroupChat.as_view(), name='delete_chat'),
    path('chat/<int:chat_id>/peer/add_user/', AddGroupUser.as_view(), name='add_user'),
    path('chat/<int:chat_id>/peer/remove_user/<int:user_id>/', RemoveGroupUser.as_view(), name='remove_user'),
    path('chat/<int:chat_id>/peer/add_admin/<int:user_id>/', AddGroupAdmin.as_view(), name='add_admin'),

    path('direct/<int:user_id>/', DirectView.as_view(), name='direct'),


    # test JWT
    path('api/register/', RegisterViewAPI.as_view(), name='register1'),
    path('api/login/', LoginViewAPI.as_view(), name='login1')
]