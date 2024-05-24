from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from scraper.models import Job
from datetime import datetime, timedelta
from django.db.models import Q


def build_query(param_list, field_name):
    query = Q()
    for item in param_list:
        if item:
            query |= Q(**{f"{field_name}__icontains": item})
    return query


def build_date_query(field_name, date_str, date_format='%Y-%m-%d'):
    try:
        date_value = datetime.strptime(date_str, date_format)
        return Q(**{field_name: date_value})
    except ValueError:
        raise ValueError(f"Invalid format for {field_name}. Use {date_format}.")


def build_date_range_query(field_name, date_str, comparison, date_format='%Y-%m-%d'):
    try:
        date_value = datetime.strptime(date_str, date_format)
        return Q(**{f"{field_name}__{comparison}": date_value})
    except ValueError:
        raise ValueError(f"Invalid format for {field_name}. Use {date_format}.")


def build_publication_date_category_query(category):
    today = datetime.now().date()
    if category == "today":
        return Q(publication_date=today)
    elif category == "two_days_ago":
        date_range = today - timedelta(days=2)
        return Q(publication_date__gte=date_range)
    elif category == "one_week_ago":
        date_range = today - timedelta(days=7)
        return Q(publication_date__gte=date_range)
    elif category == "two_weeks_ago":
        date_range = today - timedelta(days=14)
        return Q(publication_date__gte=date_range)
    elif category == "one_month_ago":
        date_range = today - timedelta(days=30)
        return Q(publication_date__gte=date_range)
    return Q()


@api_view(['GET'])
def get_jobs(request):
    job_names = request.GET.get('jobName', '').split(',')
    publication_date = request.GET.get('publicationDate')
    publication_date_after = request.GET.get('publicationDateAfter')
    publication_date_before = request.GET.get('publicationDateBefore')
    publication_date_category = request.GET.get('publicationDateCategory')
    locations = request.GET.get('jobLocation', '').split(',')
    companies = request.GET.get('company', '').split(',')
    sources = request.GET.get('source', '').split(',')
    limit = request.GET.get('limit')
    page = request.GET.get('page')

    jobs = Job.objects.all()
    query = Q()

    if job_names:
        query &= build_query(job_names, 'title')

    if publication_date:
        try:
            query &= build_date_query('publication_date', publication_date)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)

    if publication_date_after:
        try:
            query &= build_date_range_query('publication_date', publication_date_after, 'gte')
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)

    if publication_date_before:
        try:
            query &= build_date_range_query('publication_date', publication_date_before, 'lte')
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)

    if publication_date_category:
        query &= build_publication_date_category_query(publication_date_category)

    if locations:
        query &= build_query(locations, 'location')

    if companies:
        query &= build_query(companies, 'company')

    if sources:
        query &= build_query(sources, 'source')

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
