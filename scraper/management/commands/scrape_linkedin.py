# scraper/management/commands/scrape_linkedin.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from django.core.management.base import BaseCommand
from scraper.models import Job
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
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

        job_types = [
            'programmer', 'data', 'network', 'cyber security',
            'software developer', 'data scientist', 'data analyst', 'data engineer',
            'system administrator', 'network engineer', 'cybersecurity analyst',
            'full stack developer', 'backend developer', 'frontend developer',
            'machine learning engineer', 'IT support', 'cloud engineer',
            'devops engineer', 'database administrator', 'AI engineer', 'QA engineer',
            'IT consultant', 'IT project manager', 'IT business analyst',
            'IT security specialist', 'IT auditor', 'IT compliance officer', 'back end', 'front end',
            'web developer', 'mobile developer', 'mobile app developer', 'android developer', 'ios developer',
            'game developer', 'game programmer', 'full stack', 'fullstack', 'penetration tester',
            'ethical hacker', 'security consultant', 'security analyst', 'security engineer', 'security architect',
            'security specialist', 'security administrator', 'security auditor', 'security compliance officer',
            'network security engineer', 'network administrator', 'data architect', 'big data engineer',
            'data warehouse developer', 'embedded systems engineer', 'firmware engineer', 'iot developer',
            'it operations manager', 'site reliability engineer', 'systems engineer', 'blockchain developer',
            'ai research scientist', 'robotics engineer', 'security operations center analyst',
            'threat intelligence analyst',
            'digital forensics analyst', 'identity and access management specialist', 'it risk manager',
            'vulnerability analyst'
        ]

        all_jobs = []
        job_counts = {job_type: 0 for job_type in job_types}  # Dictionary to count valid jobs for each job type

        # Ambil semua kombinasi yang ada di database
        existing_combinations = set(
            Job.objects.filter(source='LinkedIn').values_list('title', 'publication_date', 'location', 'company'))

        for job_type in job_types:
            self.stdout.write(self.style.SUCCESS(f'Scraping jobs for: {job_type}'))
            encoded_job_type = job_type.replace(" ", "%20")
            job_url = f"https://www.linkedin.com/jobs/search?keywords={encoded_job_type}&location=Indonesia&trk=public_jobs_jobs-search-bar_search-submit"
            driver.get(job_url)
            time.sleep(2)

            scroll_pause_time = 0.5
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
                    date_element = job.find('time')
                    location = job.find('span', class_="job-search-card__location")
                    company = job.find('h4', class_="base-search-card__subtitle")
                    link = job.find("a", class_="base-card__full-link")

                    if title and date_element and location and company and link:
                        date_text = date_element.get('datetime')
                        try:
                            # Attempt to parse full datetime format
                            publication_date = datetime.strptime(date_text, '%Y-%m-%dT%H:%M:%S.%fZ').date()
                        except ValueError:
                            # Fallback to date-only format
                            publication_date = datetime.strptime(date_text, '%Y-%m-%d').date()

                        job_data = {
                            'title': title.text.strip(),
                            'publication_date': publication_date,
                            'location': location.text.strip(),
                            'company': company.text.strip(),
                            'source': 'LinkedIn',
                            'job_link': link.get('href')
                        }

                        combination = (
                        job_data['title'], job_data['publication_date'], job_data['location'], job_data['company'])

                        # Validasi apakah tanggal publikasi masih dalam 2 bulan terakhir
                        if publication_date >= datetime.now().date() - timedelta(days=60):
                            # Periksa apakah kombinasi sudah ada di database
                            if combination not in existing_combinations:
                                all_jobs.append(job_data)
                                job_counts[job_type] += 1
                                print(
                                    f"Scraped job (Valid): Title: {job_data['title']}, Company: {job_data['company']}, Date: {job_data['publication_date']}")
                                # Tambahkan kombinasi ke set
                                existing_combinations.add(combination)
                            else:
                                print(
                                    f"Scraped job (Duplicate): Title: {job_data['title']}, Company: {job_data['company']}, Date: {job_data['publication_date']}")
                        else:
                            print(
                                f"Scraped job (Invalid): Title: {job_data['title']}, Company: {job_data['company']}, Date: {job_data['publication_date']}")

                # Check if "See more jobs" button is visible and click it
                try:
                    see_more_button = driver.find_element(By.CLASS_NAME, 'infinite-scroller__show-more-button')
                    if see_more_button.is_displayed():
                        see_more_button.click()
                        time.sleep(scroll_pause_time)
                except Exception as e:
                    print("No 'See more jobs' button found or couldn't click it.")

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
            print(f"Saved job: Title: {job['title']}, Company: {job['company']}, Date: {job['publication_date']}")

        self.stdout.write(self.style.SUCCESS(f'Successfully scraped {len(all_jobs)} jobs from LinkedIn'))

        for job_type, count in job_counts.items():
            self.stdout.write(self.style.SUCCESS(f'Total valid jobs for {job_type}: {count}'))

