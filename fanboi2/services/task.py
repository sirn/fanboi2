from ..tasks import celery, ResultProxy


class TaskQueryService(object):
    """Task query service provides a service for querying a task status."""

    def result_from_uid(self, task_uid):
        """Query a task from the given task UID.

        :param task_uid: A UID :type:`str` for a task.
        """
        task = celery.AsyncResult(task_uid)
        return ResultProxy(task)
