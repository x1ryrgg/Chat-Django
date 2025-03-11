import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from rest_framework.response import Response

from ChatAPI.tasks import send_message
from Chat_Django import settings
from Chat_Django.settings import DEFAULT_FROM_EMAIL
from .forms import ProfileForm
from .models import *
from ChatAPI.models import *
from ChatAPI.serializers import UserSerializer
from friend_requests.filters import *
from .serializers import *


logger = logging.getLogger(__name__)

@login_required
def search_users_view(request):
    user = request.user
    friend_ids = user.friends.values_list('id', flat=True)
    queryset = User.objects.exclude(id__in=friend_ids).exclude(id=user.id)
    query_filter = UserNameFilter(request.GET, queryset=queryset)

    friend_request_ids = FriendRequest.objects.filter(from_user=user).values_list('to_user_id', flat=True)
    users_with_status = [
        {
            'user': _user,
            'is_subscribed': _user.id in friend_request_ids
        }
        for _user in query_filter.qs
    ]

    return render(request, 'friend_requests/user_search.html', context={
        'filter': query_filter,
        'users': users_with_status,
        'title': 'Пользователи',
    })


@login_required
def send_friend_request(request, user_id):
    if request.method == 'POST':

        from_user = request.user
        to_user = get_object_or_404(User, pk=user_id)

        if to_user == from_user:
            messages.error(request, _('Вы не можете добавлять в друзья себя самого.'))
            return redirect(reverse_lazy('fri_req:search_users'), kwargs={'user_id': user_id})

        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        messages.success(request, f'Ваш запрос к {to_user.username} на добавление в друзья успешно отправлен!')
        return redirect(reverse_lazy('fri_req:search_users'), kwargs={'user_id': user_id})


@login_required
def incoming_friend_requests(request):
    requests = FriendRequest.objects.filter(to_user=request.user)
    return render(request, 'friend_requests/incoming_friend_requests.html', {
        'requests': requests,
        'title': 'Входящие запросы на добавление в друзья'
    })


@login_required
def handle_friend_request(request, request_id, action):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)

    if action == 'accept':
        friend_request.from_user.friends.add(friend_request.to_user)
        friend_request.delete()
        messages.success(request, f"Вы теперь друзья с {friend_request.from_user.username}.")
        return redirect('fri_req:incoming_friend_requests')
    elif action == 'decline':
        friend_request.delete()
        messages.success(request, f"Запрос от {friend_request.from_user.username} отклонен.")
        return redirect('fri_req:incoming_friend_requests')


@login_required
def friends_list(request, ):
    query = request.user.friends.all()
    Serializer = FriendsSerializer(query, many=True).data

    return render(request, 'friend_requests/friends_list.html', {
        'friends': Serializer,
        'title': 'Список друзей',
    })


@login_required
def profile(request, user_id):
    if user_id == request.user.id:
        profile = request.user
    else:
        profile = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные успешно изменены.')
            return redirect(reverse_lazy('fri_req:profile', kwargs={'user_id': request.user.id}))
    else:
        form = ProfileForm(instance=profile)

        serializer = ProfileSerializer(profile, many=False).data

        return render(request, 'friend_requests/profile.html', context={
            'serializer': serializer,
            'form': form,
        })


@login_required
def delete_friend(request, friend_id):
    user = request.user
    friend = get_object_or_404(User, id=friend_id)
    user.friends.remove(friend)
    return redirect('friend_requests:friends')


@login_required
def send_hello_email(request):
    if request.method == 'POST':
        send_message.delay(request.user.username, request.user.email)
        logger.info('celery %s success ', send_message.__name__)
        return redirect('chats')


