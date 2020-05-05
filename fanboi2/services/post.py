import datetime
import ipaddress

from sqlalchemy.sql import func

from ..errors import StatusRejectedError
from ..models import Post, Topic
from ..tasks import add_post


POSTER_SEEN_DELTA = datetime.timedelta(days=3)


class PostCreateService(object):
    """Post create service provides a service for creating a post."""

    def __init__(self, dbsession, identity_svc, setting_query_svc, user_query_svc):
        self.dbsession = dbsession
        self.identity_svc = identity_svc
        self.setting_query_svc = setting_query_svc
        self.user_query_svc = user_query_svc

    def enqueue(self, topic_id, body, bumped, ip_address, payload):
        """Enqueues the post creation to the posting queue. Posts that are
        queued will be processed with pre-posting filters using the given
        :param:`payload`.

        :param topic_id: A topic ID :type:`int` to lookup the post.
        :param body: A :type:`str` topic body.
        :param bumped: A :type:`bool` whether to bump the topic.
        :param ip_address: An IP address of the topic creator.
        :param payload: A request payload containing request metadata.
        """
        return add_post.delay(topic_id, body, bumped, ip_address, payload=payload)

    def _prepare_c(self, topic_id, bumped, allowed_board_status, allowed_topic_status):
        """Internal method performing preparatory work to create a new post.
        Returns a 3-tuple of ``(board, topic, topic_meta)``.

        :param topic_id: A topic ID :type:`int` to prepare.
        :param bumped: A :type:`bool` whether the topic will be bumped.
        :param allowed_board_status: Tuple of board status to allow posting.
        :param allowed_topic_status: Tuple of topic status to allow posting.
        """
        topic = (
            self.dbsession.query(Topic).with_for_update().filter_by(id=topic_id).one()
        )

        if topic.status not in allowed_topic_status:
            raise StatusRejectedError(topic.status)

        board = topic.board
        if board.status not in allowed_board_status:
            raise StatusRejectedError(board.status)

        # Update topic meta

        topic_meta = topic.meta
        topic_meta.post_count = topic_meta.post_count + 1
        topic_meta.posted_at = func.now()
        if bumped is None or bumped:
            topic_meta.bumped_at = func.now()
        self.dbsession.add(topic_meta)

        # Update topic

        max_posts = board.settings["max_posts"]
        if topic.status == "open" and topic_meta.post_count >= max_posts:
            topic.status = "archived"
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
        board, topic, topic_meta = self._prepare_c(
            topic_id,
            bumped,
            allowed_board_status=("open", "restricted"),
            allowed_topic_status=("open",),
        )

        ident = None
        ident_type = "none"
        if board.settings["use_ident"]:
            ident_type = "ident"
            ident_addr = ip_address

            # Since it's common for IPv6 setup to delegate a /64 from ISP to a home
            # network, it makes more sense here to always generate ident based on
            # /64 network instead of individual address.
            if ipaddress.ip_address(ip_address).version == 6:
                ident_type = "ident_v6"
                ident_addr = str(
                    ipaddress.ip_network("%s/64" % (ip_address,), strict=False)
                )

            ident = self.identity_svc.identity_with_tz_for(
                self.setting_query_svc.value_from_key("app.time_zone"),
                board=topic.board.slug,
                ip_address=ident_addr,
            )

        post = Post(
            topic=topic,
            number=topic_meta.post_count,
            body=body,
            bumped=bumped,
            name=board.settings["name"],
            ident=ident,
            ident_type=ident_type,
            ip_address=ip_address,
        )

        self.dbsession.add(post)
        return post

    def create_with_user(self, topic_id, user_id, body, bumped, ip_address):
        """Creates a new post similar to :meth:`create` but with user ID
        associated to it.

        This method will make the post delegate ident and name from the user
        as well as allow posting in board or topic that are not archived.

        :param topic_id: A topic ID :type:`int` to lookup the post.
        :param user_id: A user ID :type:`int` to post as.
        :param body: A :type:`str` topic body.
        :param bumped: A :type:`bool` whether to bump the topic.
        :param ip_address: An IP address of the topic creator.
        """
        user = self.user_query_svc.user_from_id(user_id)
        board, topic, topic_meta = self._prepare_c(
            topic_id,
            bumped,
            allowed_board_status=("open", "restricted", "locked"),
            allowed_topic_status=("open", "locked"),
        )

        ident = user.ident
        ident_type = user.ident_type
        name = user.name

        post = Post(
            topic=topic,
            number=topic_meta.post_count,
            body=body,
            bumped=bumped,
            name=name,
            ident=ident,
            ident_type=ident_type,
            ip_address=ip_address,
        )

        self.dbsession.add(post)
        return post


class PostDeleteService(object):
    """Post delete service provides a service for deleting a post from
    the database.
    """

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def delete_from_topic_id(self, topic_id, number):
        """Delete post matching the given number from the given topic.

        :param topic_id: A topic ID :type:`int` to delete the post.
        :param number: A post number in the topic.
        """
        post = (
            self.dbsession.query(Post).filter_by(topic_id=topic_id, number=number).one()
        )

        self.dbsession.delete(post)
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
        q = (
            self.dbsession.query(Post)
            .filter(
                Post.created_at >= func.now() - POSTER_SEEN_DELTA,
                Post.ip_address == ip_address,
            )
            .exists()
        )
        return self.dbsession.query(q).scalar()
