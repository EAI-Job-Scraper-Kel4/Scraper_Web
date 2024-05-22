from django.db import models

class Job(models.Model):
    job_title = models.CharField(max_length=100)
    publication_date = models.DateField()
    location = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    source_site = models.CharField(max_length=50)
    job_link = models.URLField()

    def __str__(self):
        return self.job_title

