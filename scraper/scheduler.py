from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

def delete_old_jobs():
    call_command('delete_old_jobs')

def scrape_karir():
    call_command('scrape_karir')

def scrape_kalibrr():
    call_command('scrape_kalibrr')

def scrape_linkedin():
    call_command('scrape_linkedin')

def scrape_jobstreet():
    call_command('scrape_jobstreet')

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_old_jobs, 'cron', hour=1, minute=0)
    scheduler.add_job(scrape_karir, 'cron', hour=2, minute=0)
    scheduler.add_job(scrape_kalibrr, 'cron', hour=3, minute=0)
    scheduler.add_job(scrape_linkedin, 'cron', hour=4, minute=0)
    scheduler.add_job(scrape_jobstreet, 'cron', hour=5, minute=0)
    scheduler.start()
    print("Scheduler started!")

if __name__ == "__main__":
    start()
