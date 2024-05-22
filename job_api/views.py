import requests
from django.http import JsonResponse, HttpResponse
from scraper.models import Job

def get_jobs(request):
    # get param from url
    job_name = request.GET.get('jobName')
    publication_date = request.GET.get('publicationDate')
    location = request.GET.get('jobLocation')
    company = request.GET.get('company')

    jobs = Job.objects.all()
    # allJobs = Job.objects.all()[:5]

    if job_name:
        job_name = job_name.replace('-',' ')
        print("Ini job name: " + job_name)
        jobs = jobs.filter(title__icontains=job_name)
    if publication_date:
        jobs = jobs.filter(publication_date__icontains=publication_date)
    if location:
        jobs = jobs.filter(job_location__icontains=location)
    if company:
        jobs = jobs.filter(company__icontains=company)


    jobs_data = []
    for job in jobs:
        jobs_data.append({
            'job_name': job.job_name,
            'publication_date': job.publication_date.strftime('%Y-%m-%d'),  # Format date as string
            'job_location': job.job_location,
            'company': job.company,
            'source': job.source,
            'source_url': job.source_url
        })

    return JsonResponse(jobs_data, safe=False)