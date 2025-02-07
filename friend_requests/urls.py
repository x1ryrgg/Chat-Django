from django.urls import path, re_path

from friend_requests.views import *


app_name = 'friend_requests'

urlpatterns = [
    path('search_user/', search_users_view, name='search_users'),
    path('send_friend_request/<int:user_id>/', send_friend_request, name='send_friend'),

    path('incoming_friend_requests/', incoming_friend_requests_view, name='incoming_friend_requests'),
    path('handle_friend_request/<int:request_id>/<str:action>/', handle_friend_request, name='handle_friend_request'),

    path('friends/', friends_list, name='friends'),


]