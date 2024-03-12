from django_filters import rest_framework as filters
from authentication.models import Company


class CompanyFilter(filters.FilterSet):
    brand = filters.CharFilter(field_name='brand', lookup_expr='icontains')
    is_startup = filters.BooleanFilter(field_name='is_startup')
    contact_phone = filters.CharFilter(field_name='contact_phone', lookup_expr='icontains')
    contact_email = filters.CharFilter(field_name='contact_email', lookup_expr='icontains')
    edrpou = filters.NumberFilter(field_name='edrpou')
    address = filters.CharFilter(field_name='address', lookup_expr='icontains')
    tags = filters.CharFilter(field_name='tags', lookup_expr='icontains')

    class Meta:
        model = Company
        fields = ['brand', 'is_startup', 'contact_phone', 'contact_email', 'edrpou', 'address', 'tags']
