from rest_framework import serializers
from scraper.models import Job

class JobSerializer(serializers.ModelSerializer):
    job_name = serializers.CharField(source='title')
    job_location = serializers.CharField(source='location')
    source_url = serializers.URLField(source='job_link')

    class Meta:
        model = Job
        fields = ['job_name', 'publication_date', 'job_location', 'company', 'source', 'source_url']
