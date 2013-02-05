from datetime import timedelta, datetime
import re
from sqlalchemy import or_, and_
from sqlalchemy.orm import undefer
from sqlalchemy.orm.exc import NoResultFound
from zope.interface import implementer
from .interfaces import IBoardResource, ITopicResource, IPostResource
from .models import DBSession, Board, Post, Topic


class BaseContainer(object):
    def __init__(self, request):
        self.__parent__ = None
        self.__name__ = None
        self.request = request

    @property
    def root(self):
        """Returns the topmost object of the traversal tree."""
        return self.__parent__.root

    @property
    def boards(self):
        """Returns a list of all boards."""
        return self.__parent__.boards

    @property
    def board(self):
        """Returns board associated with this container."""
        return self.__parent__.board

    @property
    def topic(self):
        """Returns topic associated with this container."""
        return self.__parent__.topic


class RootFactory(object):
    """A :type:`dict`-like object that return the traversable root."""
    __parent__ = None
    __name__ = None

    def __init__(self, request):
        self.request = request
        self._objs = None

    @property
    def objs(self):
        """Returns a :type:`list` of :class:``BoardContainer`` ordered by
        title. Boards are sorted by its name and has its :attr:`slug` as its
        name. Resolving these object will give out the `/slug` URL.
        """
        if self._objs is None:
            self._objs = []
            for obj in DBSession.query(Board).order_by(Board.title).all():
                board = BoardContainer(self.request, obj)
                board.__parent__ = self
                board.__name__ = obj.slug
                self._objs.append(board)
        return self._objs

    @property
    def root(self):
        return self

    @property
    def boards(self):
        return self.objs

    def __getitem__(self, item):
        """Retrieve a single :class:`Board` from the database using slug. If
        no board could be found, an :exception:`KeyError` exception is raise.
        Row retrieved here will be wrapped with :class:`BoardContainer`.
        """
        try:
            obj = DBSession.query(Board).filter_by(slug=item).one()
        except NoResultFound:
            raise KeyError
        board = BoardContainer(self.request, obj)
        board.__parent__ = self
        board.__name__ = item
        return board


@implementer(IBoardResource)
class BoardContainer(BaseContainer):
    """Container for :class:`Board` object and is used in traversal."""

    def __init__(self, request, board):
        super(BoardContainer, self).__init__(request)
        self.obj = board
        self._objs = {}

    def _query_posts(self, query_fn=lambda n: n):
        if not query_fn in self._objs:
            self._objs[query_fn] = []
            for obj in query_fn(self.obj.topics):
                topic = TopicContainer(self.request, obj)
                topic.__parent__ = self
                topic.__name__ = obj.id
                self._objs[query_fn].append(topic)
        return self._objs[query_fn]

    @property
    def objs(self):
        """Return a :type:`list` of recently updated :class:`TopicContainer`
        associated with this :class:`Board`. Only the top 10 recent topics
        are returned by this method. Deferred columns :attr:`post_count` and
        :attr:`posted_at` are undeferred to prevent N+1 queries when used
        for listing topics. Each object will have this board as its parent
        and will resolve to a `/slug/topic_id` URL.
        """
        # TODO: Optimize me, accessing posts here requires 1+N queries.
        # However we can't eager-loading posts since posts will have to
        # be stored in memory which should be very expensive for large
        # board (maximum of 1000 posts x 10 topics, or 10k rows.)
        return self._query_posts(lambda q: q.limit(10).\
                                             options(undefer('post_count'),
                                                     undefer('posted_at')))

    @property
    def objs_all(self):
        """Return a :type:`list` of all :class:`TopicContainer` associated
        with this :class:`Board`. Unlike :meth:`objs`, this method returns
        all active topics that are not archived or archived but within the
        last 1 week. Like :meth:`objs`, deferred columns are also undeferred.
        """
        def _query(query):
            last_week = datetime.now() - timedelta(days=7)
            return query.options(undefer('post_count'),
                                 undefer('posted_at')). \
                         filter(or_(Topic.status == "open",
                                    and_(Topic.status != "open",
                                         Topic.posted_at >= last_week)))
        return self._query_posts(_query)

    @property
    def board(self):
        return self

    def __getitem__(self, item):
        """Retrieve a single :class:`Topic` scoped to current :class:`Board`.
        If no topic could be found, or not belong to this :class:`Board`, a
        :exception:`KeyError` exception is raise. Row retrieved here will be
        wrapped by :class:`TopicContainer`.
        """
        try:
            obj = self.obj.topics.filter_by(id=int(item)).one()
        except (ValueError, NoResultFound):
            raise KeyError
        topic = TopicContainer(self.request, obj)
        topic.__parent__ = self
        topic.__name__ = item
        return topic


@implementer(ITopicResource)
class TopicContainer(BaseContainer):
    """Container for :class:`Topic` object and is used in traversal."""

    def __init__(self, request, topic):
        super(TopicContainer, self).__init__(request)
        self.obj = topic
        self._objs = None

    @property
    def objs(self):
        """Return a :type:`list` of :class:`PostContainer` associated with
        this :class:`Topic`. Each object will have this topic as its parent
        and will resolve to `/slug/topic_id/post_id` URL.
        """
        if self._objs is None:
            self._objs = []
            for obj in self.obj.posts:
                post = PostContainer(self.request, obj)
                post.__parent__ = self
                post.__name__ = obj.number
                self._objs.append(post)
        return self._objs

    @property
    def topic(self):
        return self

    def __getitem__(self, query):
        """Returns a topic scoped to :data:`query`."""
        topic = ScopedTopicContainer(self.request, self, query)
        topic.__parent__ = self.__parent__  # Inherited for URL generation.
        topic.__name__ = self.__name__  # Inherited for URL generation.
        return topic


@implementer(ITopicResource)
class ScopedTopicContainer(BaseContainer):
    """Container for :class:`Topic` similar to :class:`TopicContainer` but
    only return a list of :class:`Post` that are processed via :data:`query`
    criteria. Unlike :class:`TopicContainer`, this class don't allow any
    further traversal.

    This class should inherits its parent :attr:`TopicContainer.__name__`
    and :attr:`TopicContainer.__parent__` for URL generation.
    """
    QUERY = (
        ("_number", re.compile("^(\d+)$")),
        ("_range",  re.compile("^(\d+)?\-(\d+)?$")),
        ("_recent", re.compile("^recent$")),
    )

    def __init__(self, request, topic, query):
        super(ScopedTopicContainer, self).__init__(request)
        self.request = request
        self.obj = topic.obj
        self._topic = topic
        self._objs = None

        # Need to raise KeyError for __getitem__ in TopicContainer in case
        # query is invalid, so this is fetched here instead of in obj.
        for handler, matcher in self.QUERY:
            match = matcher.match(query)
            if match:
                func = getattr(self, handler)
                self._objs = func(*match.groups())
                break

        if not self._objs:
            raise KeyError

    @property
    def objs(self):
        """Returns a :type:`list` of :class:`PostContainer` associated with
        this :class:`Topic` but also scoped to :data:`query`.
        """
        return self._objs

    def _number(self, number):
        """Returns a single post as specified by :data:`number`."""
        obj = self.obj.posts.filter_by(number=number).first()
        if obj:
            post = PostContainer(self.request, obj)
            post.__parent__ = self._topic
            post.__name__ = obj.number
            return [post]

    def _range(self, start, end):
        """Returns a range of post of :data:`start` and :data:`end`. When
        :data:`start` or :data:`end` is empty, the first and last posts are
        assumed respectively.
        """
        if start is None:
            start = 1
        if end is None:
            query = Post.number >= start
        else:
            query = Post.number.between(start, end)
        posts = []
        for obj in self.obj.posts.filter(query):
            post = PostContainer(self.request, obj)
            post.__parent__ = self._topic
            post.__name__ = obj.number
            posts.append(post)
        return posts

    def _recent(self):
        """Return the last 30 posts."""
        posts = []
        for obj in reversed(DBSession.query(Post).
                            order_by(Post.number.desc()).
                            filter(Post.topic_id == self.obj.id).
                            limit(30).all()):
            post = PostContainer(self.request, obj)
            post.__parent__ = self._topic
            post.__name__ = obj.number
            posts.append(post)
        return posts


@implementer(IPostResource)
class PostContainer(BaseContainer):
    """Container for :class:`Post` object and is used in traversal."""

    def __init__(self, request, post):
        super(PostContainer, self).__init__(request)
        self.obj = post