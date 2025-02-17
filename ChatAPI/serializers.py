from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class ChatGroupSerializer(serializers.ModelSerializer):
    group_users = UserSerializer(many=True, read_only=True)
    class Meta:
        model = ChatGroup
        fields = ('group_name', 'group_users', 'pk')


class GroupMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    reply_to = serializers.PrimaryKeyRelatedField(queryset=GroupMessage.objects.all(), allow_null=True, required=False)

    class Meta:
        model = GroupMessage
        fields = ('id', 'group', 'sender', 'body', 'reply_to', 'date_sent')


class DirectMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = DirectMessage
        fields = ('sender', 'receiver', 'body', 'date_sent')


# TEST JWT
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user