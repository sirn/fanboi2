import datetime
import transaction
import unittest
from fanboi2 import DBSession, Base
from pyramid import testing
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from webob.multidict import MultiDict
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

    def test_topics(self):
        from fanboi2.models import Topic
        board1 = self._makeOne(title=u"Foobar", slug="foo")
        board2 = self._makeOne(title=u"Lorem", slug="lorem")
        topic1 = Topic(board=board1, title=u"Heavenly Moon")
        topic2 = Topic(board=board1, title=u"Beastie Starter")
        topic3 = Topic(board=board1, title=u"Evans")
        DBSession.add(topic1)
        DBSession.add(topic2)
        DBSession.add(topic3)
        DBSession.flush()
        self.assertItemsEqual([topic3, topic2, topic1], board1.topics)
        self.assertItemsEqual([], board2.topics)


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
        topic = self._makeOne(board=board, title=u"Lorem ipsum dolor")
        self.assertTrue(verifyObject(ITopic, topic))

    def test_relations(self):
        board = self._makeBoard(title=u"Foobar", slug="foo")
        topic = self._makeOne(board=board, title=u"Lorem ipsum dolor")
        self.assertEqual(topic.board, board)
        self.assertItemsEqual([], topic.posts)
        self.assertItemsEqual([topic], board.topics)

    def test_posts(self):
        from fanboi2.models import Post
        board = self._makeBoard(title=u"Foobar", slug="foo")
        topic1 = self._makeOne(board=board, title=u"Lorem ipsum dolor")
        topic2 = self._makeOne(board=board, title=u"Some lonely topic")
        post1 = Post(topic=topic1, body=u"Lorem")
        post2 = Post(topic=topic1, body=u"Ipsum")
        post3 = Post(topic=topic1, body=u"Dolor")
        DBSession.add(post1)
        DBSession.add(post2)
        DBSession.add(post3)
        DBSession.flush()
        self.assertItemsEqual([post1, post2, post3], topic1.posts)
        self.assertItemsEqual([], topic2.posts)

    def test_post_count(self):
        from fanboi2.models import Post
        board = self._makeBoard(title=u"Foobar", slug="foo")
        topic = self._makeOne(board=board, title=u"Lorem ipsum dolor")
        self.assertEqual(topic.post_count, 0)
        for x in xrange(3):
            post = Post(topic=topic, body=u"Hello, world!")
            DBSession.add(post)
        DBSession.flush()
        self.assertEqual(topic.post_count, 3)

    def test_posted_at(self):
        from fanboi2.models import Post
        board = self._makeBoard(title=u"Foobar", slug="foo")
        topic = self._makeOne(board=board, title=u"Lorem ipsum dolor")
        self.assertIsNone(topic.posted_at)
        for x in xrange(2):
            post = Post(topic=topic,
                        body=u"Hello, world!",
                        created_at=datetime.datetime.now() -
                        datetime.timedelta(days=1))
            DBSession.add(post)
        post = Post(topic=topic, body=u"Hello, world!")
        DBSession.add(post)
        DBSession.flush()
        self.assertEqual(topic.created_at, post.created_at)


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
        topic = self._makeTopic(board=board, title=u"Lorem ipsum dolor")
        post = self._makeOne(topic=topic, body=u"Hello, world")
        self.assertTrue(verifyObject(IPost, post))

    def test_relations(self):
        board = self._makeBoard(title=u"Foobar", slug="foo")
        topic = self._makeTopic(board=board, title=u"Lorem ipsum dolor sit")
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

    def test_objs(self):
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
        self.assertItemsEqual([], root['foobar'].objs)

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

    def test_interface(self):
        from fanboi2.interfaces import IBoardResource
        container = self._getTargetClass()({}, None)
        self.assertTrue(verifyObject(IBoardResource, container))

    def test_objs(self):
        board = self._makeOne(title=u"General", slug="general")
        topic1 = self._makeTopic(board=board, title=u"Lorem ipsum dolor sit")
        topic2 = self._makeTopic(board=board, title=u"Hello, world")
        container = self._getTargetClass()({}, board)
        self.assertEqual(container.objs[0].__parent__, container)
        self.assertEqual(container.objs[0].__name__, topic1.id)
        self.assertItemsEqual([topic1, topic2],
                              (t.obj for t in container.objs))

    def test_getitem(self):
        board = self._makeOne(title=u"General", slug="general")
        topic1 = self._makeTopic(board=board, title=u"Lorem ipsum dolor sit")
        topic2 = self._makeTopic(board=board, title=u"Hello, world")
        container = self._getTargetClass()({}, board)
        self.assertEqual(container[topic1.id].obj, topic1)
        self.assertEqual(container[topic2.id].obj, topic2)

    def test_getitem_notfound(self):
        board = self._makeOne(title=u"General", slug="general")
        container = self._getTargetClass()({}, board)
        with self.assertRaises(KeyError):
            assert not container[123456]  # Non-exists.


class TopicContainerTest(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.resources import TopicContainer
        return TopicContainer

    def test_interface(self):
        from fanboi2.interfaces import ITopicResource
        container = self._getTargetClass()({}, None)
        self.assertTrue(verifyObject(ITopicResource, container))


class TestViews(ModelMixin, unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        super(TestViews, self).setUp()

    def _getRoot(self, request):
        from fanboi2.resources import RootFactory
        return RootFactory(request)

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

    def test_root_view(self):
        from fanboi2.views import root_view
        board1 = self._makeBoard(title=u"General", slug="general")
        board2 = self._makeBoard(title=u"Foobar", slug="foo")
        request = testing.DummyRequest()
        request.context = self._getRoot(request)
        view = root_view(request)
        self.assertEqual(request.resource_path(view["boards"][0]), "/foo/")
        self.assertItemsEqual([board2, board1],
                              (b.obj for b in view["boards"]))

    def test_board_view(self):
        from fanboi2.views import board_view
        board = self._makeBoard(title=u"General", slug="general")
        topic1 = self._makeTopic(board=board, title=u"Hello, world!")
        topic2 = self._makeTopic(board=board, title=u"Python!!!11one")
        request = testing.DummyRequest()
        request.context = self._getRoot(request)["general"]
        view = board_view(request)
        self.assertItemsEqual([board], (b.obj for b in view["boards"]))
        self.assertEqual(view["board"].obj, board)
        self.assertEqual(request.resource_path(view["topics"][0]),
                         "/general/%s/" % topic1.id)
        self.assertItemsEqual([topic1, topic2],
                              (t.obj for t in view["topics"]))

    def test_new_board_view_get(self):
        from fanboi2.views import new_board_view
        board = self._makeBoard(title=u"General", slug="general")
        request = testing.DummyRequest(MultiDict({}))
        request.context = self._getRoot(request)["general"]
        view = new_board_view(request)
        self.assertItemsEqual([board], (b.obj for b in view["boards"]))
        self.assertEqual(view["board"].obj, board)
        self.assertDictEqual(view["form"].errors, {})

    def test_new_board_view_post(self):
        from fanboi2.views import new_board_view
        self._makeBoard(title=u"General", slug="general")
        request = testing.DummyRequest(MultiDict({
            'title': "One more thing...",
            'body': "And now for something completely different...",
        }), post=True)
        request.context = self._getRoot(request)["general"]
        response = new_board_view(request)
        self.assertEqual(response.location, "http://example.com/general/")

    def test_new_board_view_post_failure(self):
        from fanboi2.views import new_board_view
        self._makeBoard(title=u"General", slug="general")
        request = testing.DummyRequest(MultiDict({
            'title': "One more thing...",
            'body': "",
        }), post=True)
        request.context = self._getRoot(request)["general"]
        view = new_board_view(request)
        self.assertEqual(view["form"].title.data, 'One more thing...')
        self.assertDictEqual(view["form"].errors, {
            'body': [u'This field is required.']
        })