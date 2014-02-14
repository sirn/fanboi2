import transaction
from celery import Celery
from sqlalchemy.exc import IntegrityError
from .models import DBSession, Post, Topic, Board
from .utils import akismet

celery = Celery()


def configure_celery(settings):  # pragma: no cover
    """Returns a Celery configuration object.

    :param settings: A settings :type:`dict`.

    :type settings: dict
    :rtype: dict
    """
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
    """Insert a topic to the database.

    :param request: A serialized request :type:`dict` returned from
                    :meth:`fanboi2.utils.serialize_request`.
    :param board_id: An :type:`int` referencing board ID.
    :param title: A :type:`str` topic title.
    :param body: A :type:`str` topic body.

    :type request: dict
    :type board_id: int
    :type title: str
    :type body: str
    :rtype: tuple
    """
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


@celery.task(bind=True, throws=(AddPostException,), max_retries=4)  # 5 total.
def add_post(self, request, topic_id, body, bumped):
    """Insert a post to a topic.

    :param self: A :class:`celery.Task` object.
    :param request: A serialized request :type:`dict` returned from
                    :meth:`fanboi2.utils.serialize_request`.
    :param topic_id: An :type:`int` referencing topic ID.
    :param body: A :type:`str` post body.
    :param bumped: A :type:`bool` specifying bump status.

    :type self: celery.Task
    :type request: dict
    :type topic_id: int
    :type body: str
    :type bumped: bool
    :rtype: tuple
    """
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
