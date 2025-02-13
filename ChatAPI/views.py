import logging
import json

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.cache import cache
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
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
    permission_classes = [IsAuthenticated, ]
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

        # Кешируем количество входящих запросов на дружбу
        count_requests_cache_key = f'friend_request_count_{user.username}'
        count_requests = cache.get(count_requests_cache_key)
        if count_requests is None:
            count_requests = FriendRequest.objects.filter(to_user=user).count()
            cache.set(count_requests_cache_key, count_requests, 60)  # Кешируем на 60 секунд

        # Кешируем список чатов пользователя
        chatgroup_cache_key = f'chatgroup_data_{user.username}'
        chatgroup_data = cache.get(chatgroup_cache_key)
        if not chatgroup_data:
            chatgroup_query = ChatGroup.objects.filter(group_users=user).prefetch_related('group_users', 'group_admin_users')
            chatgroup_data = ChatGroupSerializer(chatgroup_query, many=True).data
            cache.set(chatgroup_cache_key, chatgroup_data, 60)  # Кешируем на 60 секунд

        filter = UserNameFilter(request.GET, queryset=user.friends.all())
        filter_serializer = UserSerializer(filter.qs, many=True).data

        context = {
            'user': UserSerializer(user).data,
            'serializer': chatgroup_data,
            'filter': filter,
            'filter_serializer': filter_serializer,
            'title': 'Все чаты',
            'count_requests': count_requests,
        }

        return render(request, 'chatAPI/chats.html', context)


class GroupChatCreateView(APIView):
    permission_classes = [IsAuthenticated, ]
    @staticmethod
    def get(request):
        form = ChatForm()
        users_queryset = User.objects.filter(pk__in=request.user.friends.all())
        form.fields['group_users'].queryset = users_queryset
        return render(request, 'ChatAPI/group-create.html', context={'form': form,
                                                                     'title': 'Создание группового чата'})

    @staticmethod
    def post(request):
        form = ChatForm(data=request.POST)

        if form.is_valid():
            chat_group = form.save(commit=False)
            chat_group.creator = request.user
            chat_group.save()
            form.save_m2m()

            chat_group.group_users.add(request.user)
            return redirect(reverse_lazy('chats'))

        return render(request, 'ChatAPI/group-create.html', context={'form': form,
                                                                      'title': 'Создание группового чата'})


class DeleteGroupChat(APIView):
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def post(request, chat_id):
        chat = get_object_or_404(ChatGroup, id=chat_id)
        if chat.creator == request.user:
            chat.delete()
            return redirect('chats')

        messages.error(request, _("Только создатель чата можешь удалить его."))
        return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))


class LeaveGroupChat(APIView):
    permission_classes = [IsAuthenticated, ]
    @staticmethod
    def post(request, chat_id):
        chat = get_object_or_404(ChatGroup, pk=chat_id)
        user = request.user

        if user in chat.group_users.all():
            chat.group_users.remove(user)
            chat.save()
            return redirect(reverse_lazy('chats'))


class AddGroupUser(APIView):
    permission_classes = [IsAuthenticated, ]
    @staticmethod
    def get(request, chat_id):
        chat = get_object_or_404(ChatGroup, pk=chat_id)

        if request.user not in chat.group_admin_users.all():
            messages.error(request, _("Только администратор может добавлять пользователей."))
            return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))

        existing_users = chat.group_users.all() # в форме отображаются пользователи которых не в чате.
        user_friends = request.user.friends.all() # а так же только друзья.
        users_queryset = User.objects.exclude(pk=request.user.pk).exclude(pk__in=existing_users).filter(pk__in=user_friends)
        form = UserGroupForm()
        form.fields['group_users'].queryset = users_queryset
        return render(request, 'ChatAPI/action_user.html', context={'chat': chat, 'form': form,
                                                                 'title': 'Добавление пользователей в чат'})
    @staticmethod
    def post(request, chat_id):
        chat = get_object_or_404(ChatGroup, pk=chat_id)
        form = UserGroupForm(data=request.POST)

        if form.is_valid():
            selected_users = form.cleaned_data['group_users']

            for user in selected_users:
                chat.group_users.add(user)
            return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))


class RemoveGroupUser(APIView):
    permission_classes = [IsAuthenticated]
    @staticmethod
    def post(request, chat_id, user_id):
        chat = get_object_or_404(ChatGroup, pk=chat_id)
        user_to_remove = get_object_or_404(User, pk=user_id)

        if request.user not in chat.group_admin_users.all():
            messages.error(request, "Только администратор может убирать пользователей.")
            return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))

        if user_to_remove in chat.group_admin_users.all() or user_to_remove == request.user:
            messages.error(request, "Администраторов нельзя удалять из чата.")
            return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))

        chat.group_users.remove(user_to_remove)
        messages.success(request, f"Пользователь {user_to_remove.username} успешно удален из чата.")
        return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))


class GroupChatView(APIView):
    permission_classes = [IsAuthenticated, ]
    @staticmethod
    def get_group_context(chat_id):
        chat = get_object_or_404(ChatGroup, id=chat_id)

        query = GroupMessage.objects.filter(group__id=chat_id).select_related('group', 'sender')
        serializer = GroupMessageSerializer(query, many=True)
        form = GroupMessageForm()
        return {
            'chat': chat,
            'serializer': serializer.data,
            'form': form,
            'title': chat.group_name,
        }

    @staticmethod
    def get(request, chat_id):
        context = GroupChatView.get_group_context(chat_id)

        if request.user not in context['chat'].group_users.all():
            return redirect(reverse_lazy('chats'))

        context['chat_id'] = chat_id
        return render(request, 'chatAPI/groupchat.html', context)

    @staticmethod
    def post(request, chat_id):
        form = GroupMessageForm(data=request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.group = get_object_or_404(ChatGroup, id=chat_id)
            message.save()

            context = GroupChatView.get_group_context(chat_id)
            return render(request, 'ChatAPI/messages.html', context)

        messages.error(request, _("Ошибка при отправке сообщения."))
        context = GroupChatView.get_group_context(chat_id)
        context['form'] = form
        return render(request, 'chatAPI/groupchat.html', context)


class PeerGroupChatView(APIView):
    permission_classes = [IsAuthenticated, ]
    @staticmethod
    def get(request, chat_id):
        chat = get_object_or_404(ChatGroup, id=chat_id)

        users = chat.group_users.all()
        admins = chat.group_admin_users.all()
        return render(request, 'ChatAPI/peer.html', context={'chat': chat, 'title': chat.group_name,
                                                             'users': users, 'user': request.user, 'admins': admins})


class AddGroupAdmin(APIView):
    permission_classes = [IsAuthenticated, ]
    @staticmethod
    def post(request, chat_id, user_id):
        chat = get_object_or_404(ChatGroup, id=chat_id)
        user = get_object_or_404(User, id=user_id)

        if request.user not in chat.group_users.all():
            messages.error(request, _('Только администратор может назначать пользователя админом.'))
            return redirect(reverse_lazy('peer'), kwargs={'chat_id': chat_id})

        chat.group_admin_users.add(user)
        messages.success(request, _(f'{user.username} успешно установленен как админ.'))
        return redirect(reverse_lazy('peer', kwargs={'chat_id': chat_id}))


class DirectView(APIView):
    permission_classes = [IsAuthenticated, ]
    @staticmethod
    def get_direct_context(user_id, current_user):
        query = DirectMessage.objects.filter(
            (Q(sender=current_user) & Q(receiver=user_id)) |
            (Q(sender=user_id) & Q(receiver=current_user))
        ).select_related('sender', 'receiver')

        serializer = DirectMessageSerializer(query, many=True)
        form = DirectMessageForm()
        return {
            'serializer': serializer.data,
            'form': form,
            'title': 'Личный чат'
        }

    @staticmethod
    def get(request, user_id):
        context = DirectView.get_direct_context(user_id, request.user)
        context['user_id'] = user_id
        return render(request, 'chatAPI/direct.html', context)

    @staticmethod
    def post(request, user_id):
        form = DirectMessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = get_object_or_404(User, id=user_id)
            message.save()

            context = DirectView.get_direct_context(user_id, request.user)
            return render(request, 'ChatAPI/messages.html', context)

        messages.error(request, _("Ошибка при отправке сообщения."))
        context = DirectView.get_direct_context(user_id, request.user)
        context['form'] = form
        return render(request, 'chatAPI/direct.html', context)


class RegisterViewAPI(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors)


class LoginViewAPI(TokenObtainPairView):
    pass