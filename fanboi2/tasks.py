from celery import Celery

celery = Celery()

def configure_celery(_celery, settings):
    _celery.conf.update(
        BROKER_URL=settings['celery.broker'],
        CELERY_RESULT_BACKEND=settings['celery.broker'],
        CELERY_TIMEZONE=settings['app.timezone'])
    return _celery
