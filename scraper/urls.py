# scraper/urls.py

from django.urls import path
from .views import JobList, JobDetail

urlpatterns = [
    path('jobs', JobList.as_view(), name='job-list'),
    path('jobs/<int:pk>/', JobDetail.as_view(), name='job-detail'),
]
