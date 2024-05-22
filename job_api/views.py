import requests
from django.http import JsonResponse, HttpResponse
from scraper.models import Job

def get_jobs(request):
    # get param from url
    title = request.GET.get('jobName')
    publication_date = request.GET.get('publicationDate')
    location = request.GET.get('jobLocation')
    company = request.GET.get('company')

    jobs = Job.objects.all()
    # allJobs = Job.objects.all()[:5]

    if title:
        title = title.replace('-',' ')
        print("Ini title " + title)
        jobs = jobs.filter(title__icontains=title)
    if publication_date:
        jobs = jobs.filter(publication_date__icontains=publication_date)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if company:
        jobs = jobs.filter(company__icontains=company)


    jobs_data = []
    for job in jobs:
        jobs_data.append({
            'job_name': job.title,
            'publication_date': job.publication_date.strftime('%Y-%m-%d'),  # Format date as string
            'job_location': job.location,
            'company': job.company,
            'source': job.source,
            'source_url': job.job_link
        })

    return JsonResponse(jobs_data, safe=False)