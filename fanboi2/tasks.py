import transaction
from celery import Celery
from sqlalchemy.exc import IntegrityError
from .models import DBSession, Post, Topic, Board
from .utils import akismet

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


class TaskException(Exception):
    pass


class AddTopicException(TaskException):
    pass


@celery.task(throws=(AddTopicException,))
def add_topic(request, board_id, title, body):
    """Insert a topic to the database."""
    if akismet.spam(request, body):
        raise AddTopicException('spam')

    with transaction.manager:
        board = DBSession.query(Board).get(board_id)
        post = Post(body=body, ip_address=request['remote_addr'])
        post.topic = Topic(board=board, title=title)
        DBSession.add(post)
        DBSession.flush()
        return 'topic', post.topic_id


class AddPostException(TaskException):
    pass


@celery.task(bind=True, throws=(AddPostException,), max_retries=4) # 5 total.
def add_post(self, request, topic_id, body, bumped):
    """Insert a post to a topic."""
    if akismet.spam(request, body):
        raise AddPostException('spam')

    with transaction.manager:
        topic = DBSession.query(Topic).get(topic_id)
        post = Post(topic=topic, body=body, bumped=bumped)
        post.ip_address = request['remote_addr']

        if topic.status != "open":
            raise AddPostException(topic.status)

        try:
            DBSession.add(post)
            DBSession.flush()
        except IntegrityError as e:
            raise self.retry(exc=e)

        return 'post', post.id
