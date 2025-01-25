import logging
import json

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import ListView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .models import *
from .serializers import *
from .forms import *
from .models import *
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

        query_filter = UserNameFilter(request.GET, queryset=User.objects.all())
        user_serializer = UserSerializer(query_filter.qs, many=True)

        chat_group_query = ChatGroup.objects.all()
        serializer = ChatGroupSerializer(chat_group_query, many=True)

        context = {'serializer': serializer.data, 'filter': query_filter,
                    'user_serializer': user_serializer.data, 'title': 'Все чаты', 'user': user}

        return render(request, 'chatAPI/chats.html', context)

class GroupChatView(APIView):
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def get_group_context(chat_id):
        query = GroupMessage.objects.filter(group__id=chat_id)
        serializer = GroupMessageSerializer(query, many=True)
        form = GroupMessageForm()
        return {
            'serializer': serializer.data,
            'form': form,
            'title': 'Групповой чат'
        }

    @staticmethod
    def get(request, chat_id):
        context = GroupChatView.get_group_context(chat_id)
        context['chat_id'] = chat_id
        return render(request, 'chatAPI/chat_one.html', context)

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
        return render(request, 'chatAPI/chat_one.html', context)


class DirectView(APIView):
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def get_direct_context(user_id, current_user):
        query = DirectMessage.objects.filter(
            (Q(sender=current_user) & Q(receiver=user_id)) |
            (Q(sender=user_id) & Q(receiver=current_user))
        )

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









