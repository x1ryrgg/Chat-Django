import datetime
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
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(), label_suffix='')
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(), label_suffix='')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class CreateChatForm(forms.ModelForm):
    group_name = forms.CharField(widget=forms.TextInput(), label_suffix='')
    members = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False,
        queryset=User.objects.all()
    )

    class Meta:
        model = Chat
        fields = ('group_name', 'members')


class UserGroupForm(forms.ModelForm): #для добавления пользователей в групп чат
    members = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Chat
        fields = ('members', )


class MessageForm(forms.ModelForm):
    body = forms.CharField(widget=forms.TextInput(), label_suffix='')

    class Meta:
        model = Message
        fields = ('body', )

