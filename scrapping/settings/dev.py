from scrapping.settings.base import *
import os

INSTALLED_APPS += [
    "django_extensions",
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