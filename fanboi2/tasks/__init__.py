from ._base import celery
from ._result_proxy import ResultProxy
from .post import add_post
from .topic import add_topic, expire_topics
from .board import dispatch_board_tasks


__all__ = [
    "ResultProxy",
    "add_post",
    "add_topic",
    "expire_topics",
    "dispatch_board_tasks",
    "celery",
]


def configure_celery(settings):  # pragma: no cover
    """Configure Celery with the given settings."""
    celery.config_from_object(
        {
            "broker_url": settings["celery.broker"],
            "result_backend": settings["celery.broker"],
        }
    )


def includeme(config):  # pragma: no cover
    configure_celery(config.registry.settings)
