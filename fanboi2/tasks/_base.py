import transaction
from celery import Celery, Task as BaseTask


celery = Celery()


class ModelTask(BaseTask):  # pragma: no cover
    """Provides a base class that automatically commit a transaction when
    the task is success, or abort when the task is a failure or will be
    retried.
    """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Task failure handler."""
        transaction.abort()

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Task retry handler."""
        transaction.abort()

    def on_success(self, retval, task_id, args, kwargs):
        """Task success handler."""
        transaction.commit()
