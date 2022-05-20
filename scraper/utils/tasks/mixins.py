from typing import cast
from celery import Task
from django.db import transaction


# Adopted from: https://testdriven.io/blog/retrying-failed-celery-tasks/
class TaskWithRetryMixin:
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 5}
    retry_backoff = True
    retry_jitter = True


# Adopted from: https://browniebroke.com/blog/making-celery-work-nicely-with-django-transactions/
class TransactionAwareTaskMixin:
    def apply_async_on_commit(self, *args, **kwargs):
        transaction.on_commit(lambda: cast(Task, self).apply_async(*args, **kwargs))
