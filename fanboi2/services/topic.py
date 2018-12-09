import datetime

from sqlalchemy.orm import contains_eager, joinedload
from sqlalchemy.sql import or_, and_, func, desc

from ..errors import StatusRejectedError
from ..models import Board, Topic, TopicMeta, Post
from ..tasks import add_topic


TOPIC_RECENT_DELTA = datetime.timedelta(days=7)


class TopicCreateService(object):
    """Topic create service provides a service for creating a topic."""

    def __init__(self, dbsession, identity_svc, setting_query_svc, user_query_svc):
        self.dbsession = dbsession
        self.identity_svc = identity_svc
        self.setting_query_svc = setting_query_svc
        self.user_query_svc = user_query_svc

    def enqueue(self, board_slug, title, body, ip_address, payload):
        """Enqueues the topic creation to the posting queue. Topics that are
        queued will be processed with pre-posting filters using the given
        :param:`payload`.

        :param board_slug: The slug :type:`str` identifying a board.
        :param title: A :type:`str` topic title.
        :param body: A :type:`str` topic body.
        :param ip_address: An IP address of the topic creator.
        :param payload: A request payload containing request metadata.
        """
        return add_topic.delay(board_slug, title, body, ip_address, payload=payload)

    def _prepare_c(self, board_slug, allowed_board_status):
        """Internal method performing preparatory work to creat a new topic.
        Returns a board.

        :param board_slug: A slug :type:`str` identifying a board.
        """
        board = self.dbsession.query(Board).filter(Board.slug == board_slug).one()

        if board.status not in allowed_board_status:
            raise StatusRejectedError(board.status)

        return board

    def create(self, board_slug, title, body, ip_address):
        """Creates a new topic and associate related metadata. Unlike
        ``enqueue``, this method performs the actual creation of the topic.

        :param board_slug: A slug :type:`str` identifying a board.
        :param title: A :type:`str` topic title.
        :param body: A :type:`str` topic body.
        :param ip_address: An IP address of the topic creator.
        """
        board = self._prepare_c(board_slug, allowed_board_status=("open",))

        # Create topic

        topic = Topic(
            board=board,
            title=title,
            created_at=func.now(),
            updated_at=func.now(),
            status="open",
        )

        self.dbsession.add(topic)

        # Create topic meta

        topic_meta = TopicMeta(
            topic=topic, post_count=1, posted_at=func.now(), bumped_at=func.now()
        )

        self.dbsession.add(topic_meta)

        # Create post

        ident = None
        ident_type = "none"
        if board.settings["use_ident"]:
            ident_type = "ident"
            ident = self.identity_svc.identity_with_tz_for(
                self.setting_query_svc.value_from_key("app.time_zone"),
                board=topic.board.slug,
                ip_address=ip_address,
            )

        post = Post(
            topic=topic,
            number=topic_meta.post_count,
            body=body,
            bumped=True,
            name=board.settings["name"],
            ident=ident,
            ident_type=ident_type,
            ip_address=ip_address,
        )

        self.dbsession.add(post)
        return topic

    def create_with_user(self, board_slug, user_id, title, body, ip_address):
        """Creates a topic similar to :meth:`create` but with user ID
        associated to it.

        This method will make the post delegate ident and name from the user
        as well as allow posting in board or topic that are not archived.

        :param board_slug: A slug :type:`str` identifying a board.
        :param user_id: A user ID :type:`int` to post as.
        :param title: A :type:`str` topic title.
        :param body: A :type:`str` topic body.
        :param ip_address: An IP address of the topic creator.
        """
        user = self.user_query_svc.user_from_id(user_id)
        board = self._prepare_c(
            board_slug, allowed_board_status=("open", "restricted", "locked")
        )

        # Create topic

        topic = Topic(
            board=board,
            title=title,
            created_at=func.now(),
            updated_at=func.now(),
            status="open",
        )

        self.dbsession.add(topic)

        # Create topic meta

        topic_meta = TopicMeta(
            topic=topic, post_count=1, posted_at=func.now(), bumped_at=func.now()
        )

        self.dbsession.add(topic_meta)

        # Create post

        ident = user.ident
        ident_type = user.ident_type
        name = user.name

        post = Post(
            topic=topic,
            number=topic_meta.post_count,
            body=body,
            bumped=True,
            name=name,
            ident=ident,
            ident_type=ident_type,
            ip_address=ip_address,
        )

        self.dbsession.add(post)
        return topic


class TopicDeleteService(object):
    """Topic delete service provides a service for deleting topic and
    associated metadata.
    """

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def delete(self, topic_id):
        """Delete the topic matching the given :param:`topic_id`.

        :param topic_id: An :type:`int` ID of the topic to delete.
        """
        topic = self.dbsession.query(Topic).filter_by(id=topic_id).one()

        self.dbsession.delete(topic)
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
        return (
            self.dbsession.query(Topic)
            .join(Topic.board, Topic.meta)
            .options(contains_eager(Topic.meta))
            .filter(
                and_(
                    Board.slug == board_slug,
                    or_(
                        Topic.status == "open",
                        and_(
                            Topic.status != "open",
                            TopicMeta.bumped_at >= func.now() - TOPIC_RECENT_DELTA,
                        ),
                    ),
                )
            )
            .order_by(desc(func.coalesce(TopicMeta.bumped_at, Topic.created_at)))
        )

    def list_from_board_slug(self, board_slug):
        """Query topics for the given board slug.

        :param board_slug: The slug :type:`str` identifying a board.
        """
        return list(self._list_q(board_slug))

    def list_recent_from_board_slug(self, board_slug, _limit=10):
        """Query recent topics for the given board slug.

        :param board_slug: The slug :type:`str` identifying a board.
        """
        return list(self._list_q(board_slug).limit(_limit))

    def list_recent(self, _limit=100):
        """Query recent topics regardless of the board."""
        return list(
            self.dbsession.query(Topic)
            .join(Topic.meta)
            .options(contains_eager(Topic.meta), joinedload(Topic.board))
            .filter(
                and_(
                    or_(
                        Topic.status == "open",
                        and_(
                            Topic.status != "open",
                            TopicMeta.bumped_at >= func.now() - TOPIC_RECENT_DELTA,
                        ),
                    )
                )
            )
            .order_by(desc(func.coalesce(TopicMeta.bumped_at, Topic.created_at)))
            .limit(_limit)
        )

    def topic_from_id(self, topic_id):
        """Query a topic from the given topic ID.

        :param topic_id: The ID :type:`int` identifying a topic.
        """
        return self.dbsession.query(Topic).filter_by(id=topic_id).one()


class TopicUpdateService(object):
    """Topic update service provides a service for updating topic."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def update(self, topic_id, **kwargs):
        """Update a topic matching the given :param:`topic_id`.

        :param topic_id: The ID :type:`int` of the topic to update.
        :param **kwargs: Attributes to update.
        """
        topic = self.dbsession.query(Topic).filter_by(id=topic_id).one()

        for key in ("status",):
            if key in kwargs:
                setattr(topic, key, kwargs[key])

        self.dbsession.add(topic)
        return topic
