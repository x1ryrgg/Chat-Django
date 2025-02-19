import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from .models import *


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(), label_suffix='')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(), label_suffix='')

    class Meta:
        model = User
        fields = ('username', 'password', )


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(), label_suffix='')
    email = forms.EmailField(label='Почта', widget=forms.EmailInput(), label_suffix='')
    this_year = datetime.date.today().year
    date_birth = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year - 100, this_year - 5))))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(), label_suffix='')
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(), label_suffix='')
    class Meta:
        model = User
        fields = ('username', 'email', 'date_birth', 'password1', 'password2', )


class ChatForm(forms.ModelForm):
    group_name = forms.CharField(widget=forms.TextInput(), label_suffix='')
    group_users = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False,
        queryset=User.objects.all()
    )

    class Meta:
        model = ChatGroup
        fields = ('group_name', 'group_users')

class UserGroupForm(forms.ModelForm): #для удаления и добавления пользователей в групп чат
    group_users = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = ChatGroup
        fields = ('group_users', )


class GroupMessageForm(forms.ModelForm):
    body = forms.CharField(widget=forms.TextInput(), label_suffix='')
    reply_to = forms.ModelChoiceField(
        queryset=GroupMessage.objects.all(),
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = GroupMessage
        fields = ['body', 'reply_to']


class DirectMessageForm(forms.ModelForm):
    body = forms.CharField(widget=forms.TextInput(), label_suffix='')

    class Meta:
        model = DirectMessage
        fields = ['body']