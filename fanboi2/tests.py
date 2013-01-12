import transaction
import unittest
from fanboi2 import DBSession, Base
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from zope.interface.verify import verifyObject


class _ModelInstanceSetup(object):

    @classmethod
    def tearDownClass(cls):
        super(_ModelInstanceSetup, cls).tearDownClass()
        Base.metadata.bind = None
        DBSession.remove()

    def setUp(self):
        super(_ModelInstanceSetup, self).setUp()
        transaction.begin()
        Base.metadata.create_all()

    def tearDown(self):
        super(_ModelInstanceSetup, self).tearDown()
        transaction.abort()


class ModelMixin(_ModelInstanceSetup):

    @classmethod
    def setUpClass(cls):
        super(ModelMixin, cls).setUpClass()
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine


class BaseModelTest(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from sqlalchemy import Column, Integer
        from fanboi2.models import BaseModel
        MockBase = declarative_base()

        class MockModel(BaseModel, MockBase):
            y = Column(Integer)
            x = Column(Integer)
        return MockModel

    def test_init(self):
        model_class = self._getTargetClass()
        mock = model_class(x=1, y=2)
        self.assertEqual(mock.x, 1)
        self.assertEqual(mock.y, 2)

    def test_tablename(self):
        model_class = self._getTargetClass()
        self.assertEqual(model_class.__tablename__, 'mock_model')


class BoardModelTest(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.models import Board
        return Board

    def _makeOne(self, *args, **kwargs):
        board = self._getTargetClass()(*args, **kwargs)
        DBSession.add(board)
        DBSession.flush()
        return board

    def test_interface(self):
        from fanboi2.interfaces import IBoard
        board = self._makeOne(title=u"Foobar", slug="foo")
        self.assertTrue(verifyObject(IBoard, board))

    def test_relations(self):
        board = self._makeOne(title=u"Foobar", slug="foo")
        self.assertListEqual(board.topics, [])


class TopicModelTest(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.models import Topic
        return Topic

    def _makeBoard(self, *args, **kwargs):
        from fanboi2.models import Board
        board = Board(*args, **kwargs)
        DBSession.add(board)
        DBSession.flush()
        return board

    def _makeOne(self, *args, **kwargs):
        topic = self._getTargetClass()(*args, **kwargs)
        DBSession.add(topic)
        DBSession.flush()
        return topic

    def test_interface(self):
        from fanboi2.interfaces import ITopic
        board = self._makeBoard(title=u"Foobar", slug="foo")
        topic = self._makeOne(board=board, topic=u"Lorem ipsum dolor")
        self.assertTrue(verifyObject(ITopic, topic))

    def test_relations(self):
        board = self._makeBoard(title=u"Foobar", slug="foo")
        topic = self._makeOne(board=board, topic=u"Lorem ipsum dolor")
        self.assertEqual(topic.board, board)
        self.assertListEqual(topic.posts, [])
        self.assertListEqual(board.topics, [topic])


class PostModelTest(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.models import Post
        return Post

    def _makeBoard(self, *args, **kwargs):
        from fanboi2.models import Board
        board = Board(*args, **kwargs)
        DBSession.add(board)
        DBSession.flush()
        return board

    def _makeTopic(self, *args, **kwargs):
        from fanboi2.models import Topic
        topic = Topic(*args, **kwargs)
        DBSession.add(topic)
        DBSession.flush()
        return topic

    def _makeOne(self, *args, **kwargs):
        post = self._getTargetClass()(*args, **kwargs)
        DBSession.add(post)
        DBSession.flush()
        return post

    def test_interface(self):
        from fanboi2.interfaces import IPost
        board = self._makeBoard(title=u"Foobar", slug="foo")
        topic = self._makeTopic(board=board, topic=u"Lorem ipsum dolor")
        post = self._makeOne(topic=topic, body=u"Hello, world")
        self.assertTrue(verifyObject(IPost, post))

    def test_relations(self):
        board = self._makeBoard(title=u"Foobar", slug="foo")
        topic = self._makeTopic(board=board, topic=u"Lorem ipsum dolor sit")
        post = self._makeOne(topic=topic, body=u"Hello, world")
        self.assertEqual(post.topic, topic)
        self.assertListEqual(topic.posts, [post])
