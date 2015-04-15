import transaction
from celery import Celery, states
from sqlalchemy.exc import IntegrityError
from fanboi2.errors import serialize_error
from fanboi2.models import DBSession, Post, Topic, Board, serialize_model
from fanboi2.utils import akismet, dnsbl

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


class ResultProxy(object):
    """A proxy class for :class:`celery.result.AsyncResult` that provide
    results serialization using :func:`fanboi2.errors.serialize_error` and
    :func:`fanboi2.models.serialize_model`.

    :param result: A result of :class:`celery.AsyncResult`.
    :type result: celery.result.AsyncResult
    """

    def __init__(self, result):
        self._result = result
        self._object = None

    @property
    def object(self):
        """Serializing the result into Python object.

        :rtype: object
        """
        if self._object is None:
            obj, id_, *args = self._result.get()
            if obj == 'failure':
                self._object = serialize_error(id_, *args)
            else:
                class_ = serialize_model(obj)
                if class_ is not None:
                    self._object = DBSession.query(class_).\
                        filter_by(id=id_).\
                        one()
        return self._object

    def success(self):
        """Returns true if result was successfully processed.

        :rtype: bool
        """
        return self._result.state == states.SUCCESS

    def __getattr__(self, name):
        return self._result.__getattribute__(name)


@celery.task()
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
        return 'failure', 'spam_blocked'

    if dnsbl.listed(request['remote_addr']):
        return 'failure', 'dnsbl_blocked'

    with transaction.manager:
        board = DBSession.query(Board).get(board_id)
        post = Post(body=body, ip_address=request['remote_addr'])
        post.topic = Topic(board=board, title=title)
        DBSession.add(post)
        DBSession.flush()
        return 'topic', post.topic_id


@celery.task(bind=True, max_retries=4)  # 5 total.
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
        return 'failure', 'spam_blocked'

    with transaction.manager:
        topic = DBSession.query(Topic).get(topic_id)
        if topic.status != 'open':
            return 'failure', 'status_blocked', topic.status

        post = Post(topic=topic, body=body, bumped=bumped)
        post.ip_address = request['remote_addr']

        try:
            DBSession.add(post)
            DBSession.flush()
        except IntegrityError as e:
            raise self.retry(exc=e)

        return 'post', post.id
