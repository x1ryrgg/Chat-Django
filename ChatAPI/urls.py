
from django.urls import path, re_path, include
from rest_framework import routers
from django.contrib.auth import views as auth_views
from . import consumers
from .views import *

router = routers.DefaultRouter()
router.register(r'', Constance, basename='constance')


urlpatterns = [
    path('', index, name='index'),

    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', ResetPasswordView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
             auth_views.PasswordResetConfirmView.as_view(template_name='ChatAPI/password_reset/password_reset_confirm.html'),
             name='password_reset_confirm'),
    path('password-reset-complete/',
             auth_views.PasswordResetCompleteView.as_view(template_name='ChatAPI/password_reset/password_reset_complete.html'),
             name='password_reset_complete'),

    path('chats/', ChatsView.as_view(), name='chats'),

    path('create-chat/', GroupChatCreateView.as_view(), name='create-chat'),
    path('chat/<int:chat_id>/', ChatView.as_view(), name='chat'),

    path('direct/', DirectChat.as_view(), name='direct_or_create'),

    path('chat/<int:chat_id>/leave/', LeaveGroupChat.as_view(), name='leave'),
    path('delete_message/<int:message_id>/', DeleteMessage.as_view(), name='delete_message'),
    path('chat/<int:chat_id>/peer/', PeerGroupChatView.as_view(), name='peer'),
    path('chat/<int:chat_id>/peer/delete_chat/', DeleteGroupChat.as_view(), name='delete_chat'),
    path('chat/<int:chat_id>/peer/add_user/', AddGroupUser.as_view(), name='add_user'),
    path('chat/<int:chat_id>/peer/remove_user/<int:user_id>/', RemoveGroupUser.as_view(), name='remove_user'),
    # path('chat/<int:chat_id>/peer/add_admin/<int:user_id>/', AddGroupAdmin.as_view(), name='add_admin'),

    # test
    path('test/', websocketest),
    path('api/constance/', include(router.urls))
]