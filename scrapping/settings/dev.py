from scrapping.settings.base import *
import os

INSTALLED_APPS += [
    "django_extensions",
    "django_celery_results"
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DJANGO_POSTGRES_DB", "scrapping"),
        "USER": os.environ.get("DJANGO_POSTGRES_USER", "scrapping"),
        "PASSWORD": os.environ.get("DJANGO_POSTGRES_PASSWORD", "scrapping"),
        "HOST": os.environ.get("DJANGO_POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DJANGO_POSTGRES_PORT", "15432"),
    }
}

CELERY_BROKER_URL = (
    f'redis://{os.environ.get("DJANGO_REDIS_HOST", "127.0.0.1")}'
    f':{os.environ.get("DJANGO_REDIS_PORT", 16379)}'
)
CELERY_RESULT_BACKEND = (
    f'redis://{os.environ.get("DJANGO_REDIS_HOST", "127.0.0.1")}'
    f':{os.environ.get("DJANGO_REDIS_PORT", 16379)}'
)
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
