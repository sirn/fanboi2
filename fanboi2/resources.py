from sqlalchemy.orm.exc import NoResultFound
from zope.interface import implementer
from .interfaces import IBoard, ITopic
from .models import DBSession, Board


class RootFactory(object):
    __parent__ = None
    __name__ = None

    def __init__(self, request):
        self.request = request
        self._objs = None

    @property
    def objs(self):
        if self._objs is None:
            self._objs = []
            for obj in DBSession.query(Board).order_by(Board.title).all():
                board = BoardContainer(self.request, obj)
                board.__parent__ = self
                board.__name__ = obj.slug
                self._objs.append(board)
        return self._objs

    def __getitem__(self, item):
        try:
            obj = DBSession.query(Board).filter_by(slug=item).one()
        except NoResultFound:
            raise KeyError
        board = BoardContainer(self.request, obj)
        board.__parent__ = self
        board.__name__ = item
        return board


@implementer(IBoard)
class BoardContainer(object):
    def __init__(self, request, board):
        self.request = request
        self.obj = board
        self._objs = None

    @property
    def objs(self):
        if self._objs is None:
            self._objs = []
            for obj in self.obj.topics:
                topic = TopicContainer(self.request, obj)
                topic.__parent__ = self
                topic.__name__ = obj.id
                self._objs.append(topic)
        return self._objs

    def __getitem__(self, item):
        try:
            obj = self.obj.topics.filter_by(id=item).one()
        except NoResultFound:
            raise KeyError
        topic = TopicContainer(self.request, obj)
        topic.__parent__ = self
        topic.__name__ = item
        return topic


@implementer(ITopic)
class TopicContainer(object):
    def __init__(self, request, topic):
        self.request = request
        self.obj = topic