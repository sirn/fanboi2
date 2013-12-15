from sqlalchemy.exc import IntegrityError
import transaction
from celery import Celery
from .models import DBSession, Post, Topic
from .utils import akismet

celery = Celery()

def configure_celery(_celery, settings):
    _celery.conf.update(
        BROKER_URL=settings['celery.broker'],
        CELERY_RESULT_BACKEND=settings['celery.broker'],
        CELERY_TIMEZONE=settings['app.timezone'])
    return _celery


@celery.task()
def add_topic(request, board, title, body):
    """Insert a topic to the database."""

    if akismet.spam(request, body):
        return {'error': 'spam'}

    with transaction.manager:
        post = Post(body=body, ip_address=request['remote_addr'])
        post.topic = Topic(board=board, title=title)
        DBSession.add(post)
        return {'success': post.topic}


@celery.task()
def add_post(request, topic, body):
    """Insert a post to a topic."""

    if akismet.spam(request, body):
        return {'error': 'spam'}

    with transaction.manager:
        # INSERT a post will issue a SELECT subquery and may cause race
        # condition. In such case, UNIQUE constraint on (topic, number)
        # will cause the driver to raise IntegrityError.
        max_attempts = 5
        while True:
            # Prevent posting to locked topic. It is handled here inside
            # retry to ensure post don't get through even the topic is
            # locked by another process while this retry is still running.
            #
            # Reload because topic passed here belongs to different session
            # and we want to ensure status is reloaded on every retry.
            topic = DBSession.query(Topic).filter_by(id=topic.id).one()
            if topic.status != "open":
                return {'error': topic.status}

            # Using SAVEPOINT to handle ROLLBACK in case of constraint
            # error so we don't have to abort transaction. Transaction
            # COMMIT (or abort) is already handled at the end of request
            # by :module:`zope.transaction`.
            sp = transaction.savepoint()
            try:
                post = Post(body=body)
                post.topic = topic
                post.ip_address = request['remote_addr']
                DBSession.add(post)
                DBSession.flush()
            except IntegrityError:
                sp.rollback()
                max_attempts -= 1
                if not max_attempts:
                    return {'error': 'transactional'}
            else:
                return {'success': post}
