from celery import shared_task

from scraper.utils.tasks import BaseTaskWithRetry


@shared_task(bind=True, base=BaseTaskWithRetry)
def scrap():
    pass