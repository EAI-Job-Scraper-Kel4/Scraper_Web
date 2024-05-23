import requests
from django.core.management.base import BaseCommand
from scraper.models import Job
from datetime import datetime, timedelta
import json


class Command(BaseCommand):
    help = 'Scrape job listings from Kalibrr'

    def handle(self, *args, **kwargs):
        job_types = [
            'programmer', 'data', 'network', 'cyber-security',
            'software-developer', 'data-scientist', 'data-analyst', 'data-engineer',
            'system-administrator', 'network-engineer', 'cybersecurity-analyst',
            'full-stack-developer', 'backend-developer', 'frontend-developer',
            'machine-learning-engineer', 'cloud-engineer',
            'devops-engineer', 'database-administrator', 'AI-engineer', 'QA-engineer',
            'IT-consultant', 'IT-project-manager', 'IT-business-analyst',
            'IT-security-specialist', 'IT-auditor', 'IT-compliance-officer', 'back-end', 'front-end',
            'web-developer', 'mobile-developer', 'mobile-app-developer', 'android-developer', 'ios-developer',
            'game-developer', 'game-programmer', 'full-stack', 'fullstack', 'penetration-tester',
            'ethical-hacker', 'security-consultant', 'security-analyst', 'security-engineer', 'security-architect',
            'security-specialist', 'security-administrator', 'security-auditor', 'security-compliance-officer',
            'network-security-engineer', 'network-administrator', 'data-architect', 'big-data-engineer',
            'data-warehouse-developer', 'embedded-systems-engineer', 'firmware-engineer', 'iot-developer',
            'it-operations-manager', 'site-reliability-engineer', 'systems-engineer', 'blockchain-developer',
            'ai-research-scientist', 'robotics-engineer', 'security-operations-center-analyst',
            'threat-intelligence-analyst', 'digital-forensics-analyst', 'identity-and-access-management-specialist',
            'it-risk-manager', 'vulnerability-analyst', 'data-mining-specialist', 'data-visualization-specialist',
            'data-governance-specialist', 'business-intelligence', 'chief-data-officer',
            'cybersecurity-architect',
            'incident-response-specialist', 'cybersecurity-forensics-analyst', 'cybersecurity-trainer',
            'chief-information-security-officer',
            'network-architect', 'network-operations-center-technician', 'wireless-network-engineer',
            'cloud-network-engineer',
            'network-support-technician', 'application-developer', 'software-architect', 'systems-programmer',
            'embedded-software-developer', 'middleware-developer', 'it-infrastructure-engineer',
            'cloud-solutions-architect',
            'technical-support-engineer', 'it-systems-analyst', 'it-asset-manager'
        ]

        all_jobs = []
        job_counts = {job_type: 0 for job_type in job_types}

        # Ambil semua kombinasi yang ada di database
        existing_combinations = set(
            Job.objects.filter(source='Kalibrr').values_list('title', 'publication_date', 'location', 'company'))

        for job_type in job_types:
            self.stdout.write(self.style.SUCCESS(f'Scraping jobs for: {job_type}'))
            url = f"https://www.kalibrr.com/kjs/job_board/search?limit=10000&offset=0&text={job_type}&country=Indonesia"
            response = requests.get(url)

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch data for {job_type}"))
                continue

            try:
                data = response.json()
                jobs = data.get("jobs", [])

                for job in jobs:
                    title = job.get('name')
                    date_text = job.get('activation_date')

                    # Ganti +00:00 dengan Z
                    if '+' in date_text:
                        date_text = date_text.replace('+00:00', 'Z')
                    publication_date = datetime.strptime(date_text, '%Y-%m-%dT%H:%M:%S.%fZ').date()

                    location = job.get('google_location', {}).get('address_components', {}).get('city')
                    company = job.get('company_name')
                    job_id = job.get('id')
                    link = f"https://www.kalibrr.com/job-board/te/{job_type}/{job_id}"

                    job_data = {
                        'title': title,
                        'publication_date': publication_date,
                        'location': location,
                        'company': company,
                        'source': 'Kalibrr',
                        'job_link': link
                    }

                    combination = (
                        job_data['title'], job_data['publication_date'], job_data['location'], job_data['company']
                    )

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
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON data for {job_type}: {e}")
                continue

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

        self.stdout.write(self.style.SUCCESS(f'Successfully scraped {len(all_jobs)} jobs from Kalibrr'))

        for job_type, count in job_counts.items():
            self.stdout.write(self.style.SUCCESS(f'Total valid jobs for {job_type}: {count}'))
