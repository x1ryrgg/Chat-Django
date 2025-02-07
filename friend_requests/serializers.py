from .models import *
from friend_requests.models import *
from rest_framework import serializers


class FriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')