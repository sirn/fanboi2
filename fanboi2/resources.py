from sqlalchemy.orm import undefer
from sqlalchemy.orm.exc import NoResultFound
from zope.interface import implementer
from .interfaces import IBoardResource, ITopicResource, IPostResource
from .models import DBSession, Board


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
class BoardContainer(object):
    """Container for :class:`Board` object and is used in traversal."""

    def __init__(self, request, board):
        self.request = request
        self.obj = board
        self._objs = None

    @property
    def objs(self):
        """Return a :type:`list` of :class:`TopicContainer` associated with
        this :class:`Board`. Deferred columns :attr:`post_count` and
        :attr:`posted_at` are undeferred to prevent N+1 queries when used
        for listing topics. Each object will have this board as its parent
        and will resolve to a `/slug/topic_id` URL.
        """
        if self._objs is None:
            self._objs = []
            for obj in self.obj.topics.options(undefer('post_count'),
                                               undefer('posted_at')):
                topic = TopicContainer(self.request, obj)
                topic.__parent__ = self
                topic.__name__ = obj.id
                self._objs.append(topic)
        return self._objs

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
class TopicContainer(object):
    """Container for :class:`Topic` object and is used in traversal."""

    def __init__(self, request, topic):
        self.request = request
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
                post.__name__ = obj.id
                self._objs.append(post)
        return self._objs


@implementer(IPostResource)
class PostContainer(object):
    """Container for :class:`Post` object and is used in traversal."""

    def __init__(self, request, post):
        self.request = request
        self.obj = post