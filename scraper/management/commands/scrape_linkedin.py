# scraper/management/commands/scrape_linkedin.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from django.core.management.base import BaseCommand
from scraper.models import Job
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os
import chromedriver_autoinstaller

class Command(BaseCommand):
    help = 'Scrape job listings from LinkedIn'

    def handle(self, *args, **kwargs):
        # Install chromedriver automatically
        chromedriver_autoinstaller.install()

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.binary_location = '/usr/bin/chromium-browser'  # Lokasi biner Chromium

        driver = webdriver.Chrome(options=chrome_options)

        job_types = ['programmer', 'data', 'network', 'cyber security']
        all_jobs = []

        for job_type in job_types:
            self.stdout.write(self.style.SUCCESS(f'Scraping jobs for: {job_type}'))
            encoded_job_type = job_type.replace(" ", "%20")
            job_url = f"https://www.linkedin.com/jobs/search?keywords={encoded_job_type}&location=Indonesia&trk=public_jobs_jobs-search-bar_search-submit"
            driver.get(job_url)
            time.sleep(2)

            scroll_pause_time = 1
            screen_height = driver.execute_script("return window.screen.height;")
            i = 1

            while True:
                driver.execute_script(f"window.scrollTo(0, {screen_height}*{i});")
                i += 1
                job_src = driver.page_source
                soup = BeautifulSoup(job_src, "html.parser")

                job_listings = soup.find("ul", class_="jobs-search__results-list")
                if job_listings is None:
                    break

                jobs = job_listings.find_all('li')
                for job in jobs:
                    title = job.find('h3', class_="base-search-card__title")
                    date = job.find('time')
                    location = job.find('span', class_="job-search-card__location")
                    company = job.find('h4', class_="base-search-card__subtitle")
                    link = job.find("a", class_="base-card__full-link")

                    if title and date and location and company and link:
                        date_text = date.get('datetime')
                        try:
                            # Attempt to parse full datetime format
                            publication_date = datetime.strptime(date_text, '%Y-%m-%dT%H:%M:%S.%fZ')
                        except ValueError:
                            # Fallback to date-only format
                            publication_date = datetime.strptime(date_text, '%Y-%m-%d')

                        job_data = {
                            'title': title.text.strip(),
                            'publication_date': publication_date,
                            'location': location.text.strip(),
                            'company': company.text.strip(),
                            'source': 'LinkedIn',
                            'job_link': link.get('href')
                        }
                        all_jobs.append(job_data)

                time.sleep(scroll_pause_time)
                scroll_height = driver.execute_script("return document.body.scrollHeight;")
                if (screen_height * i) > scroll_height:
                    break

        driver.quit()

        for job in all_jobs:
            Job.objects.update_or_create(
                job_link=job['job_link'],
                defaults=job
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully scraped {len(all_jobs)} jobs from LinkedIn'))
