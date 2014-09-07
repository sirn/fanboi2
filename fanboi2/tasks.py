import transaction
from celery import Celery
from sqlalchemy.exc import IntegrityError
from .models import DBSession, Post, Topic, Board
from .utils import akismet, dnsbl

celery = Celery()


def configure_celery(settings):  # pragma: no cover
    """Returns a Celery configuration object."""
    return {
        'BROKER_URL': settings['celery.broker'],
        'CELERY_RESULT_BACKEND': settings['celery.broker'],
        'CELERY_ACCEPT_CONTENT': ['json'],
        'CELERY_TASK_SERIALIZER': 'json',
        'CELERY_RESULT_SERIALIZER': 'json',
        'CELERY_EVENT_SERIALIZER': 'json',
        'CELERY_TIMEZONE': settings['app.timezone'],
    }


@celery.task()
def add_topic(request, board_id, title, body):
    """Insert a topic to the database."""
    if akismet.spam(request, body):
        return 'failure', 'spam'

    if dnsbl.listed(request['remote_addr']):
        return 'failure', 'dnsbl'

    with transaction.manager:
        board = DBSession.query(Board).get(board_id)
        post = Post(body=body, ip_address=request['remote_addr'])
        post.topic = Topic(board=board, title=title)
        DBSession.add(post)
        DBSession.flush()
        return 'topic', post.topic_id


@celery.task(bind=True, max_retries=4)  # 5 total.
def add_post(self, request, topic_id, body, bumped):
    """Insert a post to a topic."""
    if akismet.spam(request, body):
        return 'failure', 'spam'

    with transaction.manager:
        topic = DBSession.query(Topic).get(topic_id)
        if topic.status != "open":
            return 'failure', topic.status

        post = Post(topic=topic, body=body, bumped=bumped)
        post.ip_address = request['remote_addr']

        try:
            DBSession.add(post)
            DBSession.flush()
        except IntegrityError as e:
            raise self.retry(exc=e)

        return 'post', post.id
