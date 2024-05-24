from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from scraper.models import Job
from datetime import datetime, timedelta
from django.db.models import Q


@api_view(['GET'])
def get_jobs(request):
    job_names = request.GET.get('jobName', '').split(',')
    publication_date = request.GET.get('publicationDate')
    publication_date_after = request.GET.get('publicationDateAfter')
    publication_date_before = request.GET.get('publicationDateBefore')
    publication_date_category = request.GET.get('publicationDateCategory')
    locations = request.GET.get('jobLocation', '').split(',')
    companies = request.GET.get('company', '').split(',')
    limit = request.GET.get('limit')
    page = request.GET.get('page')

    jobs = Job.objects.all()

    query = Q()

    if job_names:
        job_name_query = Q()
        for name in job_names:
            name = name.replace('-', ' ')
            job_name_query |= Q(title__icontains=name)
        query &= job_name_query

    if publication_date:
        query &= Q(publication_date=publication_date)

    if publication_date_after:
        try:
            date_after = datetime.strptime(publication_date_after, '%Y-%m-%d')
            query &= Q(publication_date__gte=date_after)
        except ValueError:
            return JsonResponse({"error": "Invalid format for publicationDateAfter. Use YYYY-MM-DD."}, status=400)

    if publication_date_before:
        try:
            date_before = datetime.strptime(publication_date_before, '%Y-%m-%d')
            query &= Q(publication_date__lte=date_before)
        except ValueError:
            return JsonResponse({"error": "Invalid format for publicationDateBefore. Use YYYY-MM-DD."}, status=400)

    if publication_date_category:
        today = datetime.now().date()
        if publication_date_category == "today":
            query &= Q(publication_date=today)
        elif publication_date_category == "two_days_ago":
            date_range = today - timedelta(days=2)
            query &= Q(publication_date__gte=date_range)
        elif publication_date_category == "one_week_ago":
            date_range = today - timedelta(days=7)
            query &= Q(publication_date__gte=date_range)
        elif publication_date_category == "two_weeks_ago":
            date_range = today - timedelta(days=14)
            query &= Q(publication_date__gte=date_range)
        elif publication_date_category == "one_month_ago":
            date_range = today - timedelta(days=30)
            query &= Q(publication_date__gte=date_range)

    if locations:
        location_query = Q()
        for loc in locations:
            location_query |= Q(location__icontains=loc)
        query &= location_query

    if companies:
        company_query = Q()
        for comp in companies:
            company_query |= Q(company__icontains=comp)
        query &= company_query

    jobs = jobs.filter(query)

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
