from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from scraper.models import Job
from datetime import datetime, timedelta


@api_view(['GET'])
def get_jobs(request):
    job_name = request.GET.get('jobName')
    publication_date = request.GET.get('publicationDate')
    publication_date_after = request.GET.get('publicationDateAfter')
    publication_date_before = request.GET.get('publicationDateBefore')
    publication_date_category = request.GET.get('publicationDateCategory')
    location = request.GET.get('jobLocation')
    company = request.GET.get('company')
    limit = request.GET.get('limit')
    page = request.GET.get('page')

    jobs = Job.objects.all()

    if job_name:
        job_name = job_name.replace('-', ' ')
        jobs = jobs.filter(title__icontains=job_name)
    if publication_date:
        jobs = jobs.filter(publication_date=publication_date)
    if publication_date_after:
        try:
            date_after = datetime.strptime(publication_date_after, '%Y-%m-%d')
            jobs = jobs.filter(publication_date__gte=date_after)
        except ValueError:
            return JsonResponse({"error": "Invalid format for publicationDateAfter. Use YYYY-MM-DD."}, status=400)
    if publication_date_before:
        try:
            date_before = datetime.strptime(publication_date_before, '%Y-%m-%d')
            jobs = jobs.filter(publication_date__lte=date_before)
        except ValueError:
            return JsonResponse({"error": "Invalid format for publicationDateBefore. Use YYYY-MM-DD."}, status=400)
    if publication_date_category:
        today = datetime.now().date()
        if publication_date_category == "today":
            jobs = jobs.filter(publication_date=today)
        elif publication_date_category == "two_days_ago":
            date_range = today - timedelta(days=2)
            jobs = jobs.filter(publication_date__gte=date_range)
        elif publication_date_category == "one_week_ago":
            date_range = today - timedelta(days=7)
            jobs = jobs.filter(publication_date__gte=date_range)
        elif publication_date_category == "two_weeks_ago":
            date_range = today - timedelta(days=14)
            jobs = jobs.filter(publication_date__gte=date_range)
        elif publication_date_category == "one_month_ago":
            date_range = today - timedelta(days=30)
            jobs = jobs.filter(publication_date__gte=date_range)

    if location:
        jobs = jobs.filter(location__icontains=location)
    if company:
        jobs = jobs.filter(company__icontains=company)

    total_jobs = jobs.count()

    if limit and limit != 'all':
        try:
            limit = int(limit)
        except ValueError:
            return JsonResponse({"error": "Invalid format for limit. Use an integer or 'all'."}, status=400)

        if page:
            try:
                page = int(page)
                if page < 1:
                    raise ValueError
            except ValueError:
                return JsonResponse({"error": "Invalid format for page. Use a positive integer."}, status=400)

            offset = (page - 1) * limit
            jobs = jobs[offset:offset + limit]
        else:
            jobs = jobs[:limit]

    jobs_data = []
    for job in jobs:
        jobs_data.append({
            'id': job.id,
            'job_name': job.title,
            'publication_date': job.publication_date.strftime('%Y-%m-%d'),
            'job_location': job.location,
            'company': job.company,
            'source': job.source,
            'source_url': job.job_link
        })

    return Response({'total': total_jobs, 'results': jobs_data})
