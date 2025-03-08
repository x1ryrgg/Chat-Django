import logging
import json

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.cache import cache
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .tasks import *

from .models import *
from .serializers import *
from .forms import *
from .filters import *
from .permissions import *
from friend_requests.models import *

User = get_user_model()


def index(request):
    if request.user.is_anonymous:
        return redirect('login')
    return redirect('chats')


def show_errors(request, form) -> None:
    errors_json = form.errors.as_json()
    errors_dict = json.loads(errors_json)

    for field, errors in errors_dict.items():
        for error in errors:
            message = error['message']
            messages.warning(request, _(message))


class LoginView(APIView):
    @staticmethod
    def get(request):
        if request.user.is_anonymous:
            return render(request, 'ChatAPI/login.html', context={'title': 'Авторизация',
                                                                  'form': LoginForm()})
        return redirect('chats')

    @staticmethod
    def post(request):
        if request.user.is_authenticated:
            return redirect('chats')

        if request.user.is_anonymous:
            form = LoginForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('chats')
                else:
                    return redirect('login')
        show_errors(request, form)
        return redirect('login')


class SignupView(APIView):
    @staticmethod
    def get(request):
        if request.user.is_anonymous:
            form = SignUpForm()
            return render(request, 'ChatAPI/signup.html', context={'title': 'Регистрация', 'form': form})
        return redirect('chats')

    @staticmethod
    def post(request):
        if request.user.is_authenticated:
            return redirect('chats')

        form = SignUpForm(data=request.data)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            if User.objects.filter(email=email).exists():
                messages.error(request, _("Пользователь с такой почтой уже зарегестирован."))
                return redirect('signup')
            User.objects.create_user(username=username,email=email, password=password,)
            messages.success(request, _("Вы успешно зарегистрированы, можете войти в свой аккаунт."))
        else:
            show_errors(request, form)
            return redirect('signup')
        return redirect('login')


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    @staticmethod
    def get(request):
        if not request.user.is_anonymous:
            logout(request)
        return redirect('login')


class ChatsView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        user = request.user

        chats_data_key = f'chatgroup_data_{user.username}'
        chats_data = cache.get(chats_data_key)
        if not chats_data:
            chats_query = Chat.objects.filter(members=user).prefetch_related('members')
            chats_data = ChatSerializer(chats_query,many=True).data
            cache.set(chats_data_key, chats_data, 60)

        count_requests = FriendRequest.objects.filter(to_user=user).count()

        context = {
            'user': UserSerializer(user).data,
            'chats': chats_data,
            'count_requests': count_requests,
            'title': 'Чаты',
        }

        return render(request, 'chatAPI/index.html', context)


class DirectChat(APIView):
    @staticmethod
    def post(request):
        user = User.objects.get(pk=request.data.get('id'))
        try:
            room = Chat.objects.annotate(count=Count('members')).filter(
                members=user.pk, count=2, type=Chat.Type.DIRECT
            ).filter(members=request.user.pk)[0]
        except IndexError:
            room = Chat.objects.create(group_name="Direct with %s" % user.username, type=Chat.Type.DIRECT)
            logger.info("Direct room %s created by %s", room, request.user)
            room.members.add(user.id, request.user.id)
        return redirect('chat', chat_id=room.id)


class GroupChatCreateView(APIView):
    permission_classes = [IsAuthenticated]
    @staticmethod
    def get(request):
        form = CreateChatForm()
        users_queryset = User.objects.filter(pk__in=request.user.friends.all())
        form.fields['members'].queryset = users_queryset
        return render(request, 'ChatAPI/group-create.html', context={'form': form,
                                                                     'title': 'Создание группового чата'})

    @staticmethod
    def post(request):
        form = CreateChatForm(data=request.POST)

        if form.is_valid():
            chat_group = form.save(commit=False)
            chat_group.type = 'group'
            chat_group.creator = request.user
            chat_group.save()
            form.save_m2m()

            chat_group.members.add(request.user)
            return redirect(reverse_lazy('chats'))

        return render(request, 'ChatAPI/group-create.html', context={'form': form,
                                                                      'title': 'Создание группового чата'})


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)

        user = request.user

        messages = Message.objects.filter(chat=chat).select_related('chat', 'sender')

        return render(request, 'chatAPI/chat.html', context={
            'chat': chat,
            'serializer': MessageSerializer(messages, many=True).data,
            'title': chat.group_name,
            'chat_id': chat_id,
            'user': UserSerializer(user).data,
        })


class PeerGroupChatView(APIView):
    permission_classes = [IsAuthenticated]
    @staticmethod
    def get(request, chat_id):
        chat = get_object_or_404(Chat.objects.select_related('creator'), id=chat_id)

        serializer = UserSerializer(chat.members.all(), many=True).data

        return render(request, 'ChatAPI/peer.html', context={'chat': chat, 'title': chat.group_name,
                                                             'users': serializer, 'user': request.user, })


class AddGroupUser(APIView):
    permission_classes = [IsAuthenticated]
    @staticmethod
    def get(request, chat_id):
        chat = get_object_or_404(Chat.objects.select_related('creator'), pk=chat_id)

        if request.user != chat.creator:
            messages.error(request, _("Только администратор может добавлять пользователей."))
            return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))

        existing_users = chat.members.all() # в форме отображаются пользователи которых не в чате.
        user_friends = request.user.friends.all() # а так же только друзья.
        users_queryset = User.objects.exclude(pk=request.user.pk).exclude(pk__in=existing_users).filter(pk__in=user_friends)
        form = UserGroupForm()
        form.fields['members'].queryset = users_queryset
        return render(request, 'ChatAPI/action_user.html', context={'chat': chat, 'form': form,
                                                                 'title': 'Добавление пользователей в чат'})
    @staticmethod
    def post(request, chat_id):
        chat = get_object_or_404(Chat, pk=chat_id)
        form = UserGroupForm(data=request.POST)

        if form.is_valid():
            selected_users = form.cleaned_data['members']

            for user in selected_users:
                chat.members.add(user)
            return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))


class RemoveGroupUser(APIView):
    permission_classes = [IsAuthenticated]
    @staticmethod
    def post(request, chat_id, user_id):
        chat = get_object_or_404(Chat, pk=chat_id)
        user_to_remove = get_object_or_404(User, pk=user_id)

        if request.user != chat.creator:
            messages.error(request, "Только администратор может убирать пользователей.")
            return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))

        chat.members.remove(user_to_remove)
        messages.success(request, f"Пользователь {user_to_remove.username} успешно удален из чата.")
        return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))


class DeleteMessage(APIView):
    permission_classes = [IsAuthenticated]
    @staticmethod
    def post(request, message_id):

        message = get_object_or_404(Message, id=message_id)

        if message.sender != request.user:
            messages.error(request, "Вы мотеже удалять только свои сообщения")
            return redirect(reverse_lazy('chat', kwargs={'chat_id': message.chat.id}))

        message.delete()
        messages.success(request, 'Сообщение успешно удалено.')
        return redirect(reverse_lazy('chat', kwargs={'chat_id': message.chat.id}))


# class AddGroupAdmin(APIView):
#     permission_classes = [IsAuthenticated, ]
#     @staticmethod
#     def post(request, chat_id, user_id):
#         chat = get_object_or_404(Chat, id=chat_id)
#         user = get_object_or_404(User, id=user_id)
#
#         if request.user not in chat.group_users.all():
#             messages.error(request, _('Только администратор может назначать пользователя админом.'))
#             return redirect(reverse_lazy('peer'), kwargs={'chat_id': chat_id})
#
#         chat.group_admin_users.add(user)
#         messages.success(request, _(f'{user.username} успешно установленен как админ.'))
#         return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))


class LeaveGroupChat(APIView):
    permission_classes = [IsAuthenticated]
    @staticmethod
    def post(request, chat_id):
        chat = get_object_or_404(Chat, pk=chat_id)
        user = request.user

        if user in chat.members.all():
            chat.members.remove(user)
            chat.save()
            return redirect(reverse_lazy('chats'))


class DeleteGroupChat(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        if chat.creator == request.user:
            chat.delete()
            return redirect('chats')

        messages.error(request, _("Только создатель чата можешь удалить его."))
        return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))


def websocketest(request):
    return render(request, 'ChatAPI/websocket.html', context={"text": 'Hello World!'})