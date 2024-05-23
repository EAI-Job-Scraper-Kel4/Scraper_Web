import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from scraper.models import Job
from datetime import datetime, timedelta
import json

class Command(BaseCommand):
    help = 'Scrape job listings from JobStreet'

    def handle(self, *args, **kwargs):
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
        max_pages = {}

        # Ambil semua kombinasi yang ada di database
        existing_combinations = set(Job.objects.filter(source='JobStreet').values_list('title', 'publication_date', 'location', 'company'))

        for job_type in job_types:
            self.stdout.write(self.style.SUCCESS(f'Scraping jobs for: {job_type}'))
            striped_type = job_type.replace(" ", "-")
            url = f"https://www.jobstreet.co.id/id/{striped_type}-jobs?createdAt=60d"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            # Get the number of pages
            next_page_anchor = soup.find("a", {"aria-label": "Selanjutnya"})
            previous_page_anchor = next_page_anchor.find_previous("a") if next_page_anchor else None
            current_max_page = int(previous_page_anchor.text.strip()) if previous_page_anchor else 1
            max_pages[job_type] = current_max_page

            page_number = 1
            while page_number <= current_max_page:
                self.stdout.write(self.style.SUCCESS(f'Scraping page {page_number} for {job_type}'))
                url = f"https://www.jobstreet.co.id/id/{striped_type}-jobs?createdAt=60d&page={page_number}"
                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")

                # Find the script tag containing JSON data
                script_tag = soup.find('script', text=lambda text: text and 'window.SEEK_REDUX_DATA =' in text)
                if script_tag:
                    try:
                        script_content = script_tag.string.strip()
                        script_content = '\n'.join([line.strip() for line in script_content.split('\n')])

                        for line in script_content.split('\n'):
                            if line.startswith('window.SEEK_REDUX_DATA ='):
                                script_content = line
                                break

                        if '"jobs":[' in script_content:
                            start_index = script_content.find('"jobs":[')
                            end_index = script_content.find('],"suburbs":') + 1
                            script_content = script_content[start_index:end_index]

                        script_content = '{' + script_content + '}'
                        script_content = script_content.replace('undefined', '"undefined"')
                        json_script = json.loads(script_content)
                        json_data = json_script.get('jobs', [])

                        for job in json_data:
                            title = job.get('title')
                            date_text = job.get('listingDate')
                            publication_date = datetime.strptime(date_text, '%Y-%m-%dT%H:%M:%SZ').date()
                            location = job.get('jobLocation', {}).get('label')
                            company = job.get('companyName')
                            job_id = job.get('id')
                            display_type = job.get('displayType')
                            link = f"https://www.jobstreet.co.id/id/{striped_type}-jobs?jobId={job_id}&type={display_type}"

                            if company is None:
                                company = job.get("advertiser").get("description")

                            job_data = {
                                'title': title,
                                'publication_date': publication_date,
                                'location': location,
                                'company': company,
                                'source': 'JobStreet',
                                'job_link': link
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
                    except (json.JSONDecodeError, IndexError) as e:
                        print(f"Error parsing JSON data: {e}")
                        continue

                page_number += 1

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

        self.stdout.write(self.style.SUCCESS(f'Successfully scraped {len(all_jobs)} jobs from JobStreet'))

        for job_type, count in job_counts.items():
            self.stdout.write(self.style.SUCCESS(f'Total valid jobs for {job_type}: {count}'))
        for job_type, max_page in max_pages.items():
            print(f"Max page for {job_type}: {max_page}")
