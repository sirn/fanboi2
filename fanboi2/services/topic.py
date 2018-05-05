import datetime

from sqlalchemy.orm import contains_eager
from sqlalchemy.sql import or_, and_, func, desc
import pytz

from ..errors import StatusRejectedError
from ..models import Board, Topic, TopicMeta, Post
from ..tasks import add_topic


class TopicCreateService(object):
    """Topic create service provides a service for creating a topic."""

    def __init__(self, dbsession, identity_svc, setting_query_svc):
        self.dbsession = dbsession
        self.identity_svc = identity_svc
        self.setting_query_svc = setting_query_svc

    def enqueue(self, board_slug, title, body, ip_address, payload={}):
        """Enqueues the topic creation to the posting queue. Topics that are
        queued will be processed with pre-posting filters using the given
        :param:`payload`.

        :param board_slug: The slug :type:`str` identifying a board.
        :param title: A :type:`str` topic title.
        :param body: A :type:`str` topic body.
        :param ip_address: An IP address of the topic creator.
        :param payload: A request payload containing request metadata.
        """
        return add_topic.delay(
            board_slug,
            title,
            body,
            ip_address,
            payload=payload)

    def create(self, board_slug, title, body, ip_address):
        """Creates a topic and associate related metadata. Unlike ``enqueue``,
        this method performs the actual creation of the topic.

        :param board_slug: The slug :type:`str` identifying a board.
        :param title: A :type:`str` topic title.
        :param body: A :type:`str` topic body.
        :param ip_address: An IP address of the topic creator.
        """

        # Preflight

        board = self.dbsession.query(Board).\
            filter(Board.slug == board_slug).\
            one()

        if board.status != 'open':
            raise StatusRejectedError(board.status)

        # Create topic

        topic = Topic(
            board=board,
            title=title,
            created_at=func.now(),
            updated_at=func.now(),
            status='open')

        self.dbsession.add(topic)

        # Create topic meta

        topic_meta = TopicMeta(
            topic=topic,
            post_count=1,
            posted_at=func.now(),
            bumped_at=func.now())

        self.dbsession.add(topic_meta)

        # Create post

        ident = None
        if board.settings['use_ident']:
            time_zone = self.setting_query_svc.value_from_key('app.time_zone')
            tz = pytz.timezone(time_zone)
            timestamp = datetime.datetime.now(tz).strftime("%Y%m%d")
            ident = self.identity_svc.identity_for(
                board=topic.board.slug,
                ip_address=ip_address,
                timestamp=timestamp)

        post = Post(
            topic=topic,
            number=topic_meta.post_count,
            body=body,
            bumped=True,
            name=board.settings['name'],
            ident=ident,
            ip_address=ip_address)

        self.dbsession.add(post)
        return topic


class TopicQueryService(object):
    """Topic query service provides a service for querying a topic or
    a collection of topics from the database.
    """

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def _list_q(self, board_slug):
        """Internal method for querying topic list.

        :param board_slug: The slug :type:`str` identifying a board.
        """
        anchor = datetime.datetime.now() - datetime.timedelta(days=7)
        return self.dbsession.query(Topic).\
            join(Topic.board, Topic.meta).\
            options(contains_eager(Topic.meta)).\
            filter(and_(Board.slug == board_slug,
                        or_(Topic.status == "open",
                            and_(Topic.status != "open",
                                 TopicMeta.bumped_at >= anchor)))).\
            order_by(desc(func.coalesce(
                TopicMeta.bumped_at,
                Topic.created_at)))

    def list_from_board_slug(self, board_slug):
        """Query topics for the given board slug.

        :param board_slug: The slug :type:`str` identifying a board.
        """
        return list(self._list_q(board_slug))

    def list_recent_from_board_slug(self, board_slug):
        """Query recent 10 topics for the given board slug.

        :param board_slug: The slug :type:`str` identifying a board.
        """
        return list(self._list_q(board_slug).limit(10))

    def topic_from_id(self, topic_id):
        """Query a topic from the given topic ID.

        :param topic_id: The ID :type:`int` identifying a topic.
        """
        return self.dbsession.query(Topic).\
            filter_by(id=topic_id).\
            one()
