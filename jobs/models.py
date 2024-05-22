from django.db import models

class Job(models.Model):
    job_name = models.CharField(max_length=100)
    publication_date = models.DateField()
    job_location = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    source = models.CharField(max_length=50)
    source_url = models.URLField()

    def __str__(self):
        return self.job_name

