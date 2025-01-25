from .models import *
from rest_framework import serializers


class ChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ['group_name', 'pk']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'pk']

class GroupMessageSerializer(serializers.ModelSerializer):
    group = ChatGroupSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    class Meta:
        model = GroupMessage
        fields = ['group', 'sender', 'body', 'date_sent']


class DirectMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = DirectMessage
        fields = ['sender', 'receiver', 'body', 'time_sent']
