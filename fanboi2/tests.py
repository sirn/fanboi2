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
        self.assertItemsEqual([], board.topics)


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
        self.assertItemsEqual([], topic.posts)
        self.assertItemsEqual([topic], board.topics)


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
        self.assertItemsEqual([post], topic.posts)


class RootFactoryTest(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.resources import RootFactory
        return RootFactory

    def _makeBoard(self, *args, **kwargs):
        from fanboi2.models import Board
        board = Board(*args, **kwargs)
        DBSession.add(board)
        DBSession.flush()
        return board

    def test_properties(self):
        root = self._getTargetClass()({})
        self.assertIsNone(root.__parent__)
        self.assertIsNone(root.__name__)

    def test_list_boards(self):
        board1 = self._makeBoard(title=u"Foobar", slug="foobar")
        board2 = self._makeBoard(title=u"Lorem", slug="lorem")
        board3 = self._makeBoard(title=u"Amplifier", slug="amplifier")
        root = self._getTargetClass()({})
        self.assertEqual(root.objs[0].__parent__, root)
        self.assertEqual(root.objs[0].__name__, "amplifier")
        self.assertItemsEqual([board3, board1, board2],
                              (b.obj for b in root.objs))

    def test_get_board(self):
        board = self._makeBoard(title=u"Foobar", slug="foobar")
        root = self._getTargetClass()({})
        self.assertEqual(root['foobar'].__parent__, root)
        self.assertEqual(root['foobar'].__name__, 'foobar')
        self.assertEqual(root['foobar'].obj, board)

    def test_get_board_nonexists(self):
        root = self._getTargetClass()({})
        with self.assertRaises(KeyError):
            assert not root["nonexists"]


class BoardContainerTest(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.resources import BoardContainer
        return BoardContainer

    def _makeTopic(self, *args, **kwargs):
        from fanboi2.models import Topic
        topic = Topic(*args, **kwargs)
        DBSession.add(topic)
        DBSession.flush()
        return topic

    def _makeOne(self, *args, **kwargs):
        from fanboi2.models import Board
        board = Board(*args, **kwargs)
        DBSession.add(board)
        DBSession.flush()
        return board

    def test_objs(self):
        board = self._makeOne(title=u"General", slug="general")
        topic1 = self._makeTopic(board=board, topic=u"Lorem ipsum dolor sit")
        topic2 = self._makeTopic(board=board, topic=u"Hello, world")
        container = self._getTargetClass()({}, board)
        self.assertItemsEqual([topic1, topic2],
                              (t.obj for t in container.objs))

    def test_getitem(self):
        board = self._makeOne(title=u"General", slug="general")
        topic1 = self._makeTopic(board=board, topic=u"Lorem ipsum dolor sit")
        topic2 = self._makeTopic(board=board, topic=u"Hello, world")
        container = self._getTargetClass()({}, board)
        self.assertEqual(container[topic1.id].obj, topic1)
        self.assertEqual(container[topic2.id].obj, topic2)

    def test_getitem_notfound(self):
        board = self._makeOne(title=u"General", slug="general")
        container = self._getTargetClass()({}, board)
        with self.assertRaises(KeyError):
            assert not container[123456]  # Non-exists.