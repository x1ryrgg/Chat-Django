import logging
import json

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Q
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
from .models import *
from .serializers import *
from .forms import *
from .filters import *

logger = logging.getLogger(__name__)

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
            logger.warning("Got an invalid %s form: %s", form.__class__.__name__, message)


class LoginView(APIView):
    @staticmethod
    def get(request):
        if request.user.is_anonymous:
            form = LoginForm()
            return render(request, 'ChatAPI/login.html', context={'title': 'Авторизация', 'form': form})
        logger.info("User %s tried to login" % request.user)
        messages.info(request, _("Вы уже вошли в аккаунт."))
        return redirect('chats')

    @staticmethod
    def post(request):
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
        logger.info("User %s tried to login" % request.user)
        messages.info(request, _("Вы уже зарегестрировали аккаунт."))
        return redirect('chats')

    @staticmethod
    def post(request):
        form = SignUpForm(data=request.data)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            if User.objects.filter(email=email).exists():
                logger.info("Пользователь пытается зарегестрироваться уже с сущетвующей почтой %s" % email)
                return redirect('signup')
            user = User.objects.create_user(username=username,email=email, password=password,)
            messages.success(request, _("Вы успешно зарегистрированы, можете войти в свой аккаунт."))
            logger.info("User %s successfully registered" % user)
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
        else:
            logger.info("Anonymous user try to log out")
        return redirect('login')


class ChatsView(APIView):
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def get(request):
        user = request.user

        query_filter = UserNameFilter(request.GET, queryset=User.objects.exclude(username=user.username))
        user_serializer = UserSerializer(query_filter.qs, many=True)

        chatgroup_query = ChatGroup.objects.filter(group_users=user)
        serializer = ChatGroupSerializer(chatgroup_query, many=True)

        context = {'serializer': serializer.data, 'filter': query_filter,
                    'user_serializer': user_serializer.data, 'title': 'Все чаты', 'user': user}

        return render(request, 'chatAPI/chats.html', context)


class GroupChatCreateView(APIView):
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def get(request):
        form = ChatForm()
        users_queryset = User.objects.exclude(pk=request.user.pk)
        form.fields['group_users'].queryset = users_queryset
        return render(request, 'ChatAPI/group-create.html', context={'form': form,
                                                                     'title': 'Создание группового чата'})

    @staticmethod
    def post(request):
        form = ChatForm(data=request.POST)

        if form.is_valid():
            chat_group = form.save(commit=False)
            chat_group.save()
            form.save_m2m()

            chat_group.group_users.add(request.user)
            return redirect(reverse_lazy('chats'))

        return render(request, 'ChatAPI/group-create.html', context={{'form': form,
                                                                      'title': 'Создание группового чата'}})


class LeaveGroupChatView(APIView):
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def post(request, chat_id):
        chat = get_object_or_404(ChatGroup, pk=chat_id)
        user = request.user

        if user in chat.group_users.all():
            chat.group_users.remove(user)
            chat.save()
            return redirect(reverse_lazy('chats'))

class AddGroupChatView(APIView):
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def get(request, chat_id):
        chat = get_object_or_404(ChatGroup, pk=chat_id)
        form = AddUserGroupForm()

        existing_users = chat.group_users.all() # в форме отображаются пользователи которых не в чате.
        users_queryset = User.objects.exclude(pk=request.user.pk).exclude(pk__in=existing_users)
        form.fields['group_users'].queryset = users_queryset

        return render(request, 'ChatAPI/add_user.html', context={'chat': chat, 'form': form,
                                                                 'title': 'Добавление пользователей в чат'})

    @staticmethod
    def post(request, chat_id):
        chat = get_object_or_404(ChatGroup, pk=chat_id)
        form = AddUserGroupForm(data=request.POST)

        if form.is_valid():
            selected_users = form.cleaned_data['group_users']

            for user in selected_users:
                chat.group_users.add(user)

            return redirect(reverse_lazy('chat', kwargs={'chat_id': chat_id}))

        existing_users = chat.group_users.all()
        users_queryset = User.objects.exclude(pk=request.user.pk).exclude(pk__in=existing_users)
        form.fields['group_users'].queryset = users_queryset

        return render(request, 'ChatAPI/add_user.html', context={'chat': chat, 'form': form,
                                                                 'title': 'Добавление пользователей в чат'})


class GroupChatView(APIView):
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def get_group_context(chat_id):
        chat = get_object_or_404(ChatGroup, id=chat_id)

        query = GroupMessage.objects.filter(group__id=chat_id).select_related('group', 'sender')
        serializer = GroupMessageSerializer(query, many=True)
        form = GroupMessageForm()
        return {
            'serializer': serializer.data,
            'form': form,
            'title': 'Групповой чат',
            'chat': chat,
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