# scraper/filters.py

import django_filters
from .models import Job

class JobFilter(django_filters.FilterSet):
    job_name = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    publication_date = django_filters.DateFromToRangeFilter(field_name='publication_date')
    job_location = django_filters.CharFilter(field_name='location', lookup_expr='icontains')
    company = django_filters.CharFilter(field_name='company', lookup_expr='icontains')

    class Meta:
        model = Job
        fields = ['job_name', 'publication_date', 'job_location', 'company']
