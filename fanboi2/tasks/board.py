import pyramid.scripting
from celery.schedules import crontab

from ..interfaces import IBoardQueryService
from ._base import celery, ModelTask
from .topic import expire_topics


@celery.on_after_configure.connect
def _setup_board_periodic(sender, **kwargs):  # pragma: no cover
    """Sets up periodic tasks."""
    sender.add_periodic_task(
        crontab(minute="0", hour="*"),
        dispatch_board_tasks.s(),
        name="dispatch_periodic_board_tasks",
    )


@celery.task(base=ModelTask, bind=True)
def dispatch_board_tasks(self, _request=None, _registry=None):
    """Dispatch periodic board tasks."""
    with pyramid.scripting.prepare(request=_request, registry=_registry) as env:
        request = env["request"]
        board_query_svc = request.find_service(IBoardQueryService)

        for board in board_query_svc.list_active():
            if board.settings.get("expire_duration"):
                expire_topics.delay(board.slug)
