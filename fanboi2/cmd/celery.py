import sys

from celery.bin.celery import main as celery_main  # type: ignore

from .. import setup_logger, make_configurator
from ..settings import settings_from_env


def main(argv=sys.argv):
    """Run Celery with application environment."""
    settings = settings_from_env()
    setup_logger(settings)
    config = make_configurator(settings)
    config.make_wsgi_app()
    celery_main(argv)
