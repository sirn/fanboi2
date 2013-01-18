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


class TestRemoteAddr(unittest.TestCase):

    def _getFunction(self):
        from fanboi2 import remote_addr
        return remote_addr

    def _makeRequest(self, ipaddr, forwarded=None):
        request = testing.DummyRequest()
        request.environ = {'REMOTE_ADDR': ipaddr}
        if forwarded:
            request.environ['HTTP_X_FORWARDED_FOR'] = forwarded
        return request

    def test_remote_addr(self):
        request = self._makeRequest("171.100.10.1")
        self.assertEqual(self._getFunction()(request), "171.100.10.1")

    def test_private_fallback(self):
        request = self._makeRequest("10.0.1.1", "171.100.10.1")
        self.assertEqual(self._getFunction()(request), "171.100.10.1")

    def test_loopback_fallback(self):
        request = self._makeRequest("127.0.0.1", "171.100.10.1")
        self.assertEqual(self._getFunction()(request), "171.100.10.1")

    def test_private_without_fallback(self):
        request = self._makeRequest("10.0.1.1")
        self.assertEqual(self._getFunction()(request), "10.0.1.1")

    def test_loopback_without_fallback(self):
        request = self._makeRequest("127.0.0.1")
        self.assertEqual(self._getFunction()(request), "127.0.0.1")

    def test_remote_fallback(self):
        request = self._makeRequest("171.100.10.1", "8.8.8.8")
        self.assertEqual(self._getFunction()(request), "171.100.10.1")


class TestJsonType(unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.models import JsonType
        return JsonType

    def _makeOne(self):
        from fanboi2.models import JsonType
        from sqlalchemy import MetaData, Table, Column, Integer, create_engine
        engine = create_engine('sqlite://')
        metadata = MetaData(bind=engine)
        table = Table(
            'foo', metadata,
            Column('baz', Integer),
            Column('bar', JsonType),
        )
        metadata.create_all()
        return table

    def test_compile(self):
        self.assertEqual(str(self._getTargetClass()()), "BLOB")

    def test_field(self):
        table = self._makeOne()
        table.insert().execute(baz=1, bar={"x": 1})
        table.insert().execute(baz=2, bar=None)
        table.insert().execute(baz=3)  # bar should have default {} type.
        self.assertItemsEqual(
            [(1, {u'x': 1}), (2, None), (3, {})],
            table.select().order_by(table.c.baz).execute().fetchall()
        )


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
        post1 = Post(topic=topic1, body=u"Lorem", ip_address="0.0.0.0")
        post2 = Post(topic=topic1, body=u"Ipsum", ip_address="0.0.0.0")
        post3 = Post(topic=topic1, body=u"Dolor", ip_address="0.0.0.0")
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
            post = Post(
                topic=topic,
                body=u"Hello, world!",
                ip_address="0.0.0.0")
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
                        ip_address="0.0.0.0",
                        created_at=datetime.datetime.now() -
                        datetime.timedelta(days=1))
            DBSession.add(post)
        post = Post(topic=topic, body=u"Hello, world!", ip_address="0.0.0.0")
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
        if not kwargs.get('ip_address', None):
            kwargs['ip_address'] = '0.0.0.0'
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

    def _makeOne(self, *args, **kwargs):
        from fanboi2.models import Topic
        topic = Topic(*args, **kwargs)
        DBSession.add(topic)
        DBSession.flush()
        return topic

    def _makeBoard(self, *args, **kwargs):
        from fanboi2.models import Board
        board = Board(*args, **kwargs)
        DBSession.add(board)
        DBSession.flush()
        return board

    def _makePost(self, *args, **kwargs):
        from fanboi2.models import Post
        if not kwargs.get('ip_address', None):
            kwargs['ip_address'] = '0.0.0.0'
        post = Post(*args, **kwargs)
        DBSession.add(post)
        DBSession.flush()
        return post

    def test_interface(self):
        from fanboi2.interfaces import ITopicResource
        container = self._getTargetClass()({}, None)
        self.assertTrue(verifyObject(ITopicResource, container))

    def test_objs(self):
        board = self._makeBoard(title=u"General", slug="general")
        topic = self._makeOne(board=board, title=u"Boring topic is boring")
        post1 = self._makePost(topic=topic, body=u"Hello, world")
        post2 = self._makePost(topic=topic, body=u"Blah blah blah")
        post3 = self._makePost(topic=topic, body=u"Lorem ipsum dolor")
        container = self._getTargetClass()({}, topic)
        self.assertEqual(container.objs[0].__parent__, container)
        self.assertEqual(container.objs[0].__name__, post1.id)
        self.assertItemsEqual([post1, post2, post3],
                              (p.obj for p in container.objs))


class PostContainerTest(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.resources import PostContainer
        return PostContainer

    def test_interface(self):
        from fanboi2.interfaces import IPostResource
        container = self._getTargetClass()({}, None)
        self.assertTrue(verifyObject(IPostResource, container))


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

    def _makePost(selfself, *args, **kwargs):
        from fanboi2.models import Post
        if not kwargs.get('ip_address', None):
            kwargs['ip_address'] = '0.0.0.0'
        post = Post(*args, **kwargs)
        DBSession.add(post)
        DBSession.flush()
        return post

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
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title=u"General", slug="general")
        request = testing.DummyRequest(MultiDict({
            'title': u"One more thing...",
            'body': u"And now for something completely different...",
        }), post=True)
        request.remote_addr = "127.0.0.1"
        request.context = self._getRoot(request)["general"]
        response = new_board_view(request)
        self.assertEqual(DBSession.query(Topic).count(), 1)
        self.assertEqual(response.location, "http://example.com/general/")

    def test_new_board_view_post_failure(self):
        from fanboi2.views import new_board_view
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title=u"General", slug="general")
        request = testing.DummyRequest(MultiDict({
            'title': u"One more thing...",
            'body': u"",
        }), post=True)
        request.context = self._getRoot(request)["general"]
        view = new_board_view(request)
        self.assertEqual(DBSession.query(Topic).count(), 0)
        self.assertEqual(view["form"].title.data, 'One more thing...')
        self.assertDictEqual(view["form"].errors, {
            'body': [u'This field is required.']
        })

    def test_topic_view_get(self):
        from fanboi2.views import topic_view
        board = self._makeBoard(title=u"General", slug="general")
        topic = self._makeTopic(board=board, title=u"Lorem ipsum dolor sit")
        post1 = self._makePost(topic=topic, body=u"Hello, world!")
        post2 = self._makePost(topic=topic, body=u"Boring post is boring!")
        request = testing.DummyRequest(MultiDict({}))
        request.context = self._getRoot(request)["general"][str(topic.id)]
        view = topic_view(request)
        self.assertItemsEqual([board], (b.obj for b in view["boards"]))
        self.assertEqual(view["board"].obj, board)
        self.assertEqual(view["topic"].obj, topic)
        self.assertDictEqual(view["form"].errors, {})
        self.assertItemsEqual([post1, post2],
                              (p.obj for p in view["posts"]))

    def test_topic_view_post(self):
        from fanboi2.views import topic_view
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title=u"General", slug="general")
        topic = self._makeTopic(board=board, title=u"Lorem ipsum dolor sit")
        request = testing.DummyRequest(MultiDict({
            'body': u"Boring post..."
        }), post=True)
        request.remote_addr = "127.0.0.1"
        request.context = self._getRoot(request)["general"][str(topic.id)]
        response = topic_view(request)
        self.assertEqual(DBSession.query(Post).count(), 1)
        self.assertEqual(response.location,
                         "http://example.com/general/%s/" % topic.id)

    def test_topic_view_post_failure(self):
        from fanboi2.views import topic_view
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title=u"General", slug="general")
        topic = self._makeTopic(board=board, title=u"Lorem ipsum dolor sit")
        request = testing.DummyRequest(MultiDict({'body': 'x'}), post=True)
        request.context = self._getRoot(request)["general"][str(topic.id)]
        view = topic_view(request)
        self.assertEqual(DBSession.query(Post).count(), 0)
        self.assertEqual(view["form"].body.data, 'x')
        self.assertDictEqual(view["form"].errors, {
            'body': [u'Field must be between 2 and 4000 characters long.'],
        })