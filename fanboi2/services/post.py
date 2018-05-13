import datetime

from sqlalchemy.sql import func
import pytz

from ..errors import StatusRejectedError
from ..models import Post, Topic
from ..tasks import add_post


class PostCreateService(object):
    """Post create service provides a service for creating a post."""

    def __init__(self, dbsession, identity_svc, setting_query_svc):
        self.dbsession = dbsession
        self.identity_svc = identity_svc
        self.setting_query_svc = setting_query_svc

    def enqueue(self, topic_id, body, bumped, ip_address, payload={}):
        """Enqueues the post creation to the posting queue. Posts that are
        queued will be processed with pre-posting filters using the given
        :param:`payload`.

        :param topic_id: A topic ID :type:`int` to lookup the post.
        :param body: A :type:`str` topic body.
        :param bumped: A :type:`bool` whether to bump the topic.
        :param ip_address: An IP address of the topic creator.
        :param payload: A request payload containing request metadata.
        """
        return add_post.delay(
            topic_id,
            body,
            bumped,
            ip_address,
            payload=payload)

    def create(self, topic_id, body, bumped, ip_address):
        """Creates a post and associate related metadata. Unlike ``enqueue``,
        this method performs the actual creation of the topic.

        :param topic_id: A topic ID :type:`int` to lookup the post.
        :param body: A :type:`str` topic body.
        :param bumped: A :type:`bool` whether to bump the topic.
        :param ip_address: An IP address of the topic creator.
        """

        # Preflight

        topic = self.dbsession.query(Topic).\
            with_for_update().\
            get(topic_id)

        topic_meta = topic.meta
        board = topic.board

        if topic.status != 'open':
            raise StatusRejectedError(topic.status)

        if board.status not in ('open', 'restricted'):
            raise StatusRejectedError(board.status)

        # Update topic meta

        topic_meta.post_count = topic_meta.post_count + 1
        topic_meta.posted_at = func.now()
        if bumped is None or bumped:
            topic_meta.bumped_at = func.now()

        self.dbsession.add(topic_meta)

        # Update topic

        max_posts = board.settings['max_posts']

        if topic.status == 'open' and topic_meta.post_count >= max_posts:
            topic.status = 'archived'
            self.dbsession.add(topic)

        return board, topic, topic_meta

    def create(self, topic_id, body, bumped, ip_address):
        """Creates a new post and associate related metadata. Unlike
        ``enqueue``, this method performs the actual creation of the topic.

        :param topic_id: A topic ID :type:`int` to lookup the post.
        :param body: A :type:`str` topic body.
        :param bumped: A :type:`bool` whether to bump the topic.
        :param ip_address: An IP address of the topic creator.
        """
        board, topic, topic_meta = self._prepare_c(topic_id, bumped)

        ident = None
        ident_type = 'none'
        if board.settings['use_ident']:
            time_zone = self.setting_query_svc.value_from_key('app.time_zone')
            tz = pytz.timezone(time_zone)
            timestamp = datetime.datetime.now(tz).strftime("%Y%m%d")
            ident_type = 'ident'
            ident = self.identity_svc.identity_for(
                board=board.slug,
                ip_address=ip_address,
                timestamp=timestamp)

        post = Post(
            topic=topic,
            number=topic_meta.post_count,
            body=body,
            bumped=bumped,
            name=board.settings['name'],
            ident=ident,
            ident_type=ident_type,
            ip_address=ip_address)

        self.dbsession.add(post)
        return post


class PostQueryService(object):
    """Post query service provides a service for querying a collection
    of posts from the database.
    """

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def list_from_topic_id(self, topic_id, query=None):
        """Query posts for the given topic matching query.

        :param topic_id: A topic ID :type:`int` to lookup the post.
        :param query: A query :type:`string` for scoping the post.
        """
        topic = self.dbsession.query(Topic).filter_by(id=topic_id).one()
        return list(topic.scoped_posts(query))

    def was_recently_seen(self, ip_address):
        """Returns whether the given IP address was recently seen.

        :param ip_address: An :type:`str` IP address to lookup.
        """
        anchor = datetime.datetime.now() - datetime.timedelta(days=3)
        q = self.dbsession.query(Post).\
            filter(
                Post.created_at >= anchor,
                Post.ip_address == ip_address).\
            exists()
        return self.dbsession.query(q).scalar()
