import sys

from celery.bin.celery import main as celery_main

from .. import settings_from_env, setup_logger, make_config


def main(argv=sys.argv):
    """Run Celery with application environment."""
    settings = settings_from_env()
    setup_logger(settings)
    config = make_config(settings)
    config.make_wsgi_app()

    celery_main(argv)
