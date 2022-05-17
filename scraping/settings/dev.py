from scraping.settings.base import *
import os

INSTALLED_APPS += ["django_extensions", "django_celery_results"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DJANGO_POSTGRES_DB", "scraping"),
        "USER": os.environ.get("DJANGO_POSTGRES_USER", "scraping"),
        "PASSWORD": os.environ.get("DJANGO_POSTGRES_PASSWORD", "scraping"),
        "HOST": os.environ.get("DJANGO_POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DJANGO_POSTGRES_PORT", "15432"),
    }
}

CELERY_BROKER_URL = (
    f'redis://{os.environ.get("DJANGO_REDIS_HOST", "127.0.0.1")}'
    f':{os.environ.get("DJANGO_REDIS_PORT", 16379)}'
)
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"