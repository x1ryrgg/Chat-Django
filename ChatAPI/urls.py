
from django.urls import path, re_path, include
from rest_framework import routers

from . import consumers
from .views import *

router = routers.DefaultRouter()
router.register(r'', ApiUser, basename='users')

testrouter = routers.DefaultRouter()
testrouter.register(r'', TestImageView, basename='testimage')

urlpatterns = [
    path('', index, name='index'),

    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('chats/', ChatsView.as_view(), name='chats'),

    path('create-chat/', GroupChatCreateView.as_view(), name='create-chat'),
    path('chat/<int:chat_id>/leave/', LeaveGroupChat.as_view(), name='leave'),
    path('chat/<int:chat_id>/', GroupChatView.as_view(), name='chat'),
    path('delete_message/<int:message_id>/', DeleteMessage.as_view(), name='delete_message'),
    path('chat/<int:chat_id>/peer/', PeerGroupChatView.as_view(), name='peer'),
    path('chat/<int:chat_id>/peer/delete_chat/', DeleteGroupChat.as_view(), name='delete_chat'),
    path('chat/<int:chat_id>/peer/add_user/', AddGroupUser.as_view(), name='add_user'),
    path('chat/<int:chat_id>/peer/remove_user/<int:user_id>/', RemoveGroupUser.as_view(), name='remove_user'),
    path('chat/<int:chat_id>/peer/add_admin/<int:user_id>/', AddGroupAdmin.as_view(), name='add_admin'),

    path('direct/<int:user_id>/', DirectView.as_view(), name='direct'),



    # test
    path('api/', include(router.urls)),
    path('test/', include(testrouter.urls)),
]