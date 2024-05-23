# job_scraper/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include ('jobs.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('scraper.urls')),
    path('api/joblist/', include ('job_api.urls'))
]
