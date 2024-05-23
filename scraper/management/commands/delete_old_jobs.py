from django.core.management.base import BaseCommand
from scraper.models import Job
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Delete jobs that are older than 2 months'

    def handle(self, *args, **kwargs):
        # Calculate the date 2 months ago from today
        two_months_ago = datetime.now().date() - timedelta(days=60)

        # Get the jobs that are older than 2 months
        old_jobs = Job.objects.filter(publication_date__lt=two_months_ago)

        # Count the number of jobs to be deleted
        count = old_jobs.count()

        # Delete the old jobs
        old_jobs.delete()

        # Print the result
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} jobs older than 2 months'))
