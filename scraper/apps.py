from django.apps import AppConfig
import os

class ScraperConfig(AppConfig):
    name = 'scraper'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true':
            from .scheduler import start
            start()
