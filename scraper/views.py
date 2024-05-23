# scraper/views.py

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job
from .serializers import JobSerializer
from .filters import JobFilter

class JobList(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        limit = request.query_params.get('limit', None)
        offset = request.query_params.get('offset', None)

        if limit is not None:
            try:
                limit = int(limit)
                if limit <= 0:
                    raise ValueError
            except ValueError:
                raise ValidationError({'limit': 'Limit must be a positive integer.'})

        if offset is not None:
            try:
                offset = int(offset)
                if offset < 0:
                    raise ValueError
            except ValueError:
                raise ValidationError({'offset': 'Offset must be a non-negative integer.'})

        if limit is not None and offset is not None:
            queryset = queryset[offset:offset + limit]
        elif limit is not None:
            queryset = queryset[:limit]
        elif offset is not None:
            queryset = queryset[offset:]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class JobDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
