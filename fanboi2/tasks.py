from sqlalchemy.exc import IntegrityError
import transaction
from celery import Celery
from .models import DBSession, Post, Topic, Board
from .utils import akismet

celery = Celery()

def configure_celery(_celery, settings):
    _celery.conf.update(
        BROKER_URL=settings['celery.broker'],
        CELERY_RESULT_BACKEND=settings['celery.broker'],
        CELERY_TIMEZONE=settings['app.timezone'])
    return _celery


class TaskException(Exception):
    pass


class AddTopicException(TaskException):
    pass


@celery.task(throws=(AddTopicException,))
def add_topic(request, board_id, title, body):
    """Insert a topic to the database."""
    if akismet.spam(request, body):
        raise AddTopicException('spam', ('board', board_id))

    with transaction.manager:
        board = DBSession.query(Board).get(board_id)
        post = Post(body=body, ip_address=request['remote_addr'])
        post.topic = Topic(board=board, title=title)
        DBSession.add(post)
        return 'topic', post.topic_id


class AddPostException(TaskException):
    pass


@celery.task(bind=True, throws=(AddPostException,))
def add_post(self, request, topic_id, body):
    """Insert a post to a topic."""
    if akismet.spam(request, body):
        raise AddPostException('spam', ('topic', topic_id))

    with transaction.manager:
        topic = DBSession.query(Topic).get(topic_id)
        post = Post(body=body)
        post.topic = topic
        post.ip_address = request['remote_addr']

        if topic.status != "open":
            raise AddPostException(topic.status, ('topic', topic.id))

        try:
            DBSession.add(post)
            DBSession.flush()
        except IntegrityError as e:
            raise self.retry(exc=e)

        return 'post', post.id
