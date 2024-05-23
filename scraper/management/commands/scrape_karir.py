from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from django.core.management.base import BaseCommand
from scraper.models import Job
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import os
import chromedriver_autoinstaller

class Command(BaseCommand):
    help = 'Scrape job listings from Karir.com'

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
            'machine learning engineer', 'cloud engineer',
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
            'threat intelligence analyst', 'digital forensics analyst', 'identity and access management specialist',
            'it risk manager', 'vulnerability analyst', 'data mining specialist', 'data visualization specialist',
            'data governance specialist', 'business intelligence', 'chief data officer',
            'cybersecurity architect',
            'incident response specialist', 'cybersecurity forensics analyst', 'cybersecurity trainer',
            'chief information security officer',
            'network architect', 'network operations center technician', 'wireless network engineer',
            'cloud network engineer',
            'network support technician', 'application developer', 'software architect', 'systems programmer',
            'embedded software developer', 'middleware developer', 'it infrastructure engineer',
            'cloud solutions architect',
            'technical support engineer', 'it systems analyst', 'it asset manager'
        ]


        all_jobs = []
        job_counts = {job_type: 0 for job_type in job_types}

        existing_combinations = set(Job.objects.filter(source='Karir').values_list('title', 'publication_date', 'location', 'company'))

        for job_type in job_types:
            self.stdout.write(self.style.SUCCESS(f'Scraping jobs for: {job_type}'))
            job_url = f"https://karir.com/search-lowongan?keyword={job_type}"
            driver.get(job_url)
            time.sleep(5)  # Wait for JavaScript to load the content

            page_number = 1

            while True:
                self.stdout.write(self.style.SUCCESS(f'Scraping page {page_number} for {job_type}'))
                job_src = driver.page_source
                soup = BeautifulSoup(job_src, "html.parser")

                job_containers = soup.find_all("div", class_="jsx-4093401097 container")

                if not job_containers:
                    print(f"No job listings found on page {page_number}.")
                    break

                for container in job_containers:
                    info_stack = container.find("div", class_="jsx-4093401097 info-company-stack")
                    if not info_stack:
                        continue

                    title = info_stack.find('p', class_="MuiTypography-root MuiTypography-body1 text-ellipsis css-au5tz6")
                    company = info_stack.find('p', class_="MuiTypography-root MuiTypography-body1 css-rd4nzp")
                    salary = info_stack.find('p', class_="MuiTypography-root MuiTypography-body1 css-1kw12l8")
                    location = info_stack.find('p', class_="MuiTypography-root MuiTypography-body1 css-xl10kd")

                    bottom_stack = container.find("div", class_="jsx-4093401097 bottom-stack")
                    if bottom_stack:
                        date_element = bottom_stack.find('p', class_="MuiTypography-root MuiTypography-body1 css-1cyztla")

                    if title and company and location and date_element:
                        date_text = date_element.text.strip()
                        try:
                            publication_date = datetime.strptime(date_text, '%d %b %Y').date()
                        except ValueError:
                            publication_date = datetime.now().date()

                        job_data = {
                            'title': title.text.strip(),
                            'publication_date': publication_date,
                            'location': location.text.strip(),
                            'company': company.text.strip(),
                            'source': 'Karir',
                            'job_link': job_url
                        }

                        combination = (
                            job_data['title'], job_data['publication_date'], job_data['location'], job_data['company']
                        )

                        if publication_date >= datetime.now().date() - timedelta(days=60):
                            if combination not in existing_combinations:
                                all_jobs.append(job_data)
                                job_counts[job_type] += 1
                                print(
                                    f"Scraped job (Valid): Title: {job_data['title']}, Company: {job_data['company']}, Date: {job_data['publication_date']}")
                                existing_combinations.add(combination)
                            else:
                                print(
                                    f"Scraped job (Duplicate): Title: {job_data['title']}, Company: {job_data['company']}, Date: {job_data['publication_date']}")
                        else:
                            print(
                                f"Scraped job (Invalid): Title: {job_data['title']}, Company: {job_data['company']}, Date: {job_data['publication_date']}")

                try:
                    next_button = driver.find_element(By.XPATH, "//div[@class='jsx-2806892642 pagination']//div[text()='{}']".format(page_number + 1))
                    next_button.click()
                    time.sleep(5)
                    page_number += 1
                except:
                    break

        driver.quit()

        for job in all_jobs:
            try:
                job_instance, created = Job.objects.update_or_create(
                    title=job['title'],
                    publication_date=job['publication_date'],
                    location=job['location'],
                    company=job['company'],
                    defaults=job
                )
                if created:
                    print(f"Saved job: Title: {job['title']}, Company: {job['company']}, Date: {job['publication_date']}")
                else:
                    print(f"Updated job: Title: {job['title']}, Company: {job['company']}, Date: {job['publication_date']}")
            except Exception as e:
                print(f"Error saving job: {job['title']}, Company: {job['company']}, Error: {e}")

        self.stdout.write(self.style.SUCCESS(f'Successfully scraped {len(all_jobs)} jobs from Karir.com'))

        for job_type, count in job_counts.items():
            self.stdout.write(self.style.SUCCESS(f'Total valid jobs for {job_type}: {count}'))
