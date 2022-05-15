import celery


# Adopted from: https://testdriven.io/blog/retrying-failed-celery-tasks/
class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_jitter = True
