from django.db import models

class Job(models.Model):
    job_name = models.CharField(max_length=255)
    publication_date = models.DateField()
    job_location = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    source_url = models.URLField(unique=True)

    def __str__(self):
        return self.title
