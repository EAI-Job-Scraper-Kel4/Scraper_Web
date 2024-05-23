# jobs/urls.py


from django.urls import path
from .views import job_search

urlpatterns = [
    path('', job_search, name='job-search'),
]
