from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=255)
    publication_date = models.DateField()
    location = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    job_link = models.URLField(unique=False)

    def __str__(self):
        return self.title
