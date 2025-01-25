import django_filters
from ChatAPI.models import *

class UserNameFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains', label='Search username')

    class Meta:
        model = User
        fields = ()