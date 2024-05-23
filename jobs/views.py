# jobs/views.py
from datetime import datetime, timedelta
from django.shortcuts import render
from scraper.models import Job
from django.http import JsonResponse

def job_search(request):
    return render(request, 'job_search.html')


