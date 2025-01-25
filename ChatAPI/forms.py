import datetime

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from .models import *


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(), label_suffix='')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(), label_suffix='')

    class Meta:
        model = User
        fields = ('username', 'password')


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


class GroupMessageForm(forms.ModelForm):
    body = forms.CharField(widget=forms.TextInput(), label_suffix='')
    class Meta:
        model = GroupMessage
        fields = ['body']


class DirectMessageForm(forms.ModelForm):
    body = forms.CharField(widget=forms.TextInput(), label_suffix='')

    class Meta:
        model = DirectMessage
        fields = ['body']





