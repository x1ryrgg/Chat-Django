import datetime
from django import forms
from .models import *


class ProfileForm(forms.ModelForm):
    this_year = datetime.date.today().year
    date_birth = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year - 100, this_year - 5))))

    class Meta:
        model = User
        fields = ('image', 'username', 'first_name', 'last_name', 'date_birth', )