import datetime
import transaction
import unittest
from fanboi2 import DBSession, Base
from pyramid import testing
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from webob.multidict import MultiDict
from zope.interface.verify import verifyObject


DATABASE_URI = 'postgres://localhost:5432/fanboi2_test'


class _ModelInstanceSetup(object):

    @classmethod
    def tearDownClass(cls):
        super(_ModelInstanceSetup, cls).tearDownClass()
        Base.metadata.bind = None
        DBSession.remove()

    def setUp(self):
        super(_ModelInstanceSetup, self).setUp()
        Base.metadata.drop_all()
        Base.metadata.create_all()
        transaction.begin()

    def tearDown(self):
        super(_ModelInstanceSetup, self).tearDown()
        transaction.abort()


class ModelMixin(_ModelInstanceSetup):

    @classmethod
    def setUpClass(cls):
        super(ModelMixin, cls).setUpClass()
        engine = create_engine(DATABASE_URI)
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
        engine = create_engine(DATABASE_URI)
        metadata = MetaData(bind=engine)
        table = Table(
            'foo', metadata,
            Column('baz', Integer),
            Column('bar', JsonType),
        )
        metadata.drop_all()
        metadata.create_all()
        return table

    def test_compile(self):
        self.assertEqual(str(self._getTargetClass()()), "TEXT")

    def test_field(self):
        table = self._makeOne()
        table.insert().execute(baz=1, bar={"x": 1})
        table.insert().execute(baz=2, bar=None)
        table.insert().execute(baz=3)  # bar should have default {} type.
        self.assertEqual(
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
        board = self._makeOne(title="Foobar", slug="foo")
        self.assertTrue(verifyObject(IBoard, board))

    def test_relations(self):
        board = self._makeOne(title="Foobar", slug="foo")
        self.assertEqual([], list(board.topics))

    def test_topics(self):
        from fanboi2.models import Topic
        board1 = self._makeOne(title="Foobar", slug="foo")
        board2 = self._makeOne(title="Lorem", slug="lorem")
        topic1 = Topic(board=board1, title="Heavenly Moon")
        topic2 = Topic(board=board1, title="Beastie Starter")
        topic3 = Topic(board=board1, title="Evans")
        DBSession.add(topic1)
        DBSession.add(topic2)
        DBSession.add(topic3)
        DBSession.flush()
        self.assertEqual(set([topic3, topic2, topic1]), set(board1.topics))
        self.assertEqual([], list(board2.topics))


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
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeOne(board=board, title="Lorem ipsum dolor")
        self.assertTrue(verifyObject(ITopic, topic))

    def test_relations(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeOne(board=board, title="Lorem ipsum dolor")
        self.assertEqual(topic.board, board)
        self.assertEqual([], list(topic.posts))
        self.assertEqual([topic], list(board.topics))

    def test_posts(self):
        from fanboi2.models import Post
        board = self._makeBoard(title="Foobar", slug="foo")
        topic1 = self._makeOne(board=board, title="Lorem ipsum dolor")
        topic2 = self._makeOne(board=board, title="Some lonely topic")
        post1 = Post(topic=topic1, body="Lorem", ip_address="0.0.0.0")
        post2 = Post(topic=topic1, body="Ipsum", ip_address="0.0.0.0")
        post3 = Post(topic=topic1, body="Dolor", ip_address="0.0.0.0")
        DBSession.add(post1)
        DBSession.add(post2)
        DBSession.add(post3)
        DBSession.flush()
        self.assertEqual([post1, post2, post3], list(topic1.posts))
        self.assertEqual([], list(topic2.posts))

    def test_post_count(self):
        from fanboi2.models import Post
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeOne(board=board, title="Lorem ipsum dolor")
        self.assertEqual(topic.post_count, 0)
        for x in range(3):
            post = Post(
                topic=topic,
                body="Hello, world!",
                ip_address="0.0.0.0")
            DBSession.add(post)
        DBSession.flush()
        self.assertEqual(topic.post_count, 3)

    def test_posted_at(self):
        from fanboi2.models import Post
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeOne(board=board, title="Lorem ipsum dolor")
        self.assertIsNone(topic.posted_at)
        for x in range(2):
            post = Post(topic=topic,
                        body="Hello, world!",
                        ip_address="0.0.0.0",
                        created_at=datetime.datetime.now() -
                        datetime.timedelta(days=1))
            DBSession.add(post)
        post = Post(topic=topic, body="Hello, world!", ip_address="0.0.0.0")
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
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        post = self._makeOne(topic=topic, body="Hello, world")
        self.assertTrue(verifyObject(IPost, post))

    def test_relations(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        post = self._makeOne(topic=topic, body="Hello, world")
        self.assertEqual(post.topic, topic)
        self.assertEqual([post], list(topic.posts))

    def test_number(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic1 = self._makeTopic(board=board, title="Numbering one")
        topic2 = self._makeTopic(board=board, title="Numbering two")
        post1 = self._makeOne(topic=topic1, body="Topic 1, post 1")
        post2 = self._makeOne(topic=topic1, body="Topic 1, post 2")
        post3 = self._makeOne(topic=topic2, body="Topic 2, post 1")
        post4 = self._makeOne(topic=topic1, body="Topic 1, post 3")
        post5 = self._makeOne(topic=topic2, body="Topic 2, post 2")
        # Force update to ensure its number remain the same.
        post4.body = "Topic1, post 3, updated!"
        DBSession.add(post4)
        DBSession.flush()
        self.assertEqual(post1.number, 1)
        self.assertEqual(post2.number, 2)
        self.assertEqual(post3.number, 1)
        self.assertEqual(post4.number, 3)
        self.assertEqual(post5.number, 2)


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
        board1 = self._makeBoard(title="Foobar", slug="foobar")
        board2 = self._makeBoard(title="Lorem", slug="lorem")
        board3 = self._makeBoard(title="Amplifier", slug="amplifier")
        root = self._getTargetClass()({})
        self.assertEqual(root.objs[0].__parent__, root)
        self.assertEqual(root.objs[0].__name__, "amplifier")
        self.assertEqual([board3, board1, board2],
                         [b.obj for b in root.objs])

    def test_get_board(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        root = self._getTargetClass()({})
        self.assertEqual(root['foobar'].__parent__, root)
        self.assertEqual(root['foobar'].__name__, 'foobar')
        self.assertEqual(root['foobar'].obj, board)
        self.assertEqual([], root['foobar'].objs)

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
        board = self._makeOne(title="General", slug="general")
        topic1 = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        topic2 = self._makeTopic(board=board, title="Hello, world")
        container = self._getTargetClass()({}, board)
        self.assertEqual(container.objs[0].__parent__, container)
        self.assertEqual(container.objs[0].__name__, topic1.id)
        self.assertEqual([topic1, topic2],
                         [t.obj for t in container.objs])

    def test_getitem(self):
        board = self._makeOne(title="General", slug="general")
        topic1 = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        topic2 = self._makeTopic(board=board, title="Hello, world")
        container = self._getTargetClass()({}, board)
        self.assertEqual(container[topic1.id].obj, topic1)
        self.assertEqual(container[topic2.id].obj, topic2)

    def test_getitem_notfound(self):
        board = self._makeOne(title="General", slug="general")
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
        board = self._makeBoard(title="General", slug="general")
        topic1 = self._makeOne(board=board, title="Boring topic is boring")
        topic2 = self._makeOne(board=board, title="Yo dawg")
        self._makePost(topic=topic2, body="I heard you like blah blah")
        post1 = self._makePost(topic=topic1, body="Hello, world")
        post2 = self._makePost(topic=topic1, body="Blah blah blah")
        post3 = self._makePost(topic=topic1, body="Lorem ipsum dolor")
        container = self._getTargetClass()({}, topic1)
        self.assertEqual(container.objs[0].__parent__, container)
        self.assertEqual(container.objs[0].__name__, post1.number)
        self.assertEqual([post1, post2, post3],
                         [p.obj for p in container.objs])

    def test_getitem(self):
        from fanboi2.resources import ScopedTopicContainer
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeOne(board=board, title="Lorem ipsum dolor sit")
        self._makePost(topic=topic, body="Hello, world!")
        self._makePost(topic=topic, body="Blah post!")
        container = self._getTargetClass()({}, topic)
        self.assertIsInstance(container["1"], ScopedTopicContainer)
        self.assertIsInstance(container["1-10"], ScopedTopicContainer)
        self.assertIsInstance(container["recent"], ScopedTopicContainer)

    def test_getitem_notfound(self):
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeOne(board=board, title="Lorem ipsum dolor sit")
        self._makePost(topic=topic, body="Hello, world!")
        container = self._getTargetClass()({}, topic)
        self.assertRaises(KeyError, lambda: container["2"])   # Not found
        self.assertRaises(KeyError, lambda: container["2-3"]) # Not found
        self.assertRaises(KeyError, lambda: container["invalid"])


class ScopedTopicContainerTest(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.resources import ScopedTopicContainer
        return ScopedTopicContainer

    def _makeTopic(self, *args, **kwargs):
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
        # Blah, need to pass in the real object since this method will raise
        # KeyError on invalid init.
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic = self._makeTopic(board=board, title="Foo bar foo bar")
        self._makePost(topic=topic, body="Blah, blah, blah")
        container = self._getTargetClass()({}, topic, None, "1")
        self.assertTrue(verifyObject(ITopicResource, container))

    def test_objs(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic = self._makeTopic(board=board, title="Hello, world!")
        post1 = self._makePost(topic=topic, body="Blah, hello, hi")
        container = self._getTargetClass()({}, topic, self, "1")
        self.assertEqual(container.objs[0].__parent__, self)
        self.assertEqual(container.objs[0].__name__, post1.number)

    def test_number_query(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another post!!1")
        post1 = self._makePost(topic=topic1, body="Post 1")
        post2 = self._makePost(topic=topic2, body="Post 1")
        post3 = self._makePost(topic=topic1, body="Post 2")
        post4 = self._makePost(topic=topic2, body="Post 2")
        container = self._getTargetClass()({}, topic1, self, "2")
        self.assertEqual(container.objs[0].__parent__, self)
        self.assertEqual(container.objs[0].__name__, post3.number)
        self.assertEqual([post3], [p.obj for p in container.objs])

    def test_range_query(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        post3 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 4")
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 1")
        post6 = self._makePost(topic=topic2, body="Topic 2, Post 2")
        post7 = self._makePost(topic=topic1, body="Topic 1, Post 5")
        container = self._getTargetClass()({}, topic1, self, "2-5")
        self.assertEqual(container.objs[0].__parent__, self)
        self.assertEqual(container.objs[0].__name__, post2.number)
        self.assertEqual([post2, post3, post4, post7],
                         [p.obj for p in container.objs])

    def test_range_query_without_end(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        post3 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 4")
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 1")
        post6 = self._makePost(topic=topic2, body="Topic 2, Post 2")
        post7 = self._makePost(topic=topic1, body="Topic 1, Post 5")
        container = self._getTargetClass()({}, topic1, self, "3-")
        self.assertEqual(container.objs[0].__parent__, self)
        self.assertEqual(container.objs[0].__name__, post3.number)
        self.assertEqual([post3, post4, post7],
                         [p.obj for p in container.objs])

    def test_range_query_without_start(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        post3 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 4")
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 1")
        post6 = self._makePost(topic=topic2, body="Topic 2, Post 2")
        post7 = self._makePost(topic=topic1, body="Topic 1, Post 5")
        container = self._getTargetClass()({}, topic1, self, "-3")
        self.assertEqual(container.objs[0].__parent__, self)
        self.assertEqual(container.objs[0].__name__, post1.number)
        self.assertEqual([post1, post2, post3],
                         [p.obj for p in container.objs])

    def test_recent_query(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        for i in range(5):
            self._makePost(topic=topic2, body="Dummy post, blah blah.")
        post3 = self._makePost(topic=topic2, body="Topic 2, Post 6")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        for i in range(28):
            self._makePost(topic=topic2, body="Another dummy post, blah.")
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 35")
        container = self._getTargetClass()({}, topic2, self, "recent")
        self.assertEqual(container.objs[0].__parent__, self)
        self.assertEqual(container.objs[0].__name__, post3.number)
        self.assertEqual(container.objs[0].obj, post3)
        self.assertEqual(container.objs[-1].obj, post5)


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
        board1 = self._makeBoard(title="General", slug="general")
        board2 = self._makeBoard(title="Foobar", slug="foo")
        request = testing.DummyRequest()
        request.context = self._getRoot(request)
        view = root_view(request)
        self.assertEqual(request.resource_path(view["boards"][0]), "/foo/")
        self.assertEqual([board2, board1],
                         [b.obj for b in view["boards"]])

    def test_board_view(self):
        from fanboi2.views import board_view
        board = self._makeBoard(title="General", slug="general")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Python!!!11one")
        request = testing.DummyRequest()
        request.context = self._getRoot(request)["general"]
        view = board_view(request)
        self.assertEqual([board], [b.obj for b in view["boards"]])
        self.assertEqual(view["board"].obj, board)
        self.assertEqual(request.resource_path(view["topics"][0]),
                         "/general/%s/" % topic1.id)
        self.assertEqual([topic1, topic2],
                         [t.obj for t in view["topics"]])

    def test_new_board_view_get(self):
        from fanboi2.views import new_board_view
        board = self._makeBoard(title="General", slug="general")
        request = testing.DummyRequest(MultiDict({}))
        request.context = self._getRoot(request)["general"]
        view = new_board_view(request)
        self.assertEqual([board], [b.obj for b in view["boards"]])
        self.assertEqual(view["board"].obj, board)
        self.assertDictEqual(view["form"].errors, {})

    def test_new_board_view_post(self):
        from fanboi2.views import new_board_view
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title="General", slug="general")
        request = testing.DummyRequest(MultiDict({
            'title': "One more thing...",
            'body': "And now for something completely different...",
        }), post=True)
        request.remote_addr = "127.0.0.1"
        request.context = self._getRoot(request)["general"]
        response = new_board_view(request)
        self.assertEqual(DBSession.query(Topic).count(), 1)
        self.assertEqual(response.location, "http://example.com/general/")

    def test_new_board_view_post_failure(self):
        from fanboi2.views import new_board_view
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title="General", slug="general")
        request = testing.DummyRequest(MultiDict({
            'title': "One more thing...",
            'body': "",
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
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        post1 = self._makePost(topic=topic, body="Hello, world!")
        post2 = self._makePost(topic=topic, body="Boring post is boring!")
        request = testing.DummyRequest(MultiDict({}))
        request.context = self._getRoot(request)["general"][str(topic.id)]
        view = topic_view(request)
        self.assertEqual([board], [b.obj for b in view["boards"]])
        self.assertEqual(view["board"].obj, board)
        self.assertEqual(view["topic"].obj, topic)
        self.assertDictEqual(view["form"].errors, {})
        self.assertEqual([post1, post2],
                         [p.obj for p in view["posts"]])

    def test_topic_view_post(self):
        from fanboi2.views import topic_view
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        request = testing.DummyRequest(MultiDict({
            'body': "Boring post..."
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
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        request = testing.DummyRequest(MultiDict({'body': 'x'}), post=True)
        request.remote_addr = "127.0.0.1"
        request.context = self._getRoot(request)["general"][str(topic.id)]
        view = topic_view(request)
        self.assertEqual(DBSession.query(Post).count(), 0)
        self.assertEqual(view["form"].body.data, 'x')
        self.assertDictEqual(view["form"].errors, {
            'body': [u'Field must be between 2 and 4000 characters long.'],
        })

    def test_topic_view_post_repeatable(self):
        from fanboi2.models import DBSession, Post
        from fanboi2.views import topic_view
        from sqlalchemy.exc import IntegrityError
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")

        class InvalidRequest(testing.DummyRequest):
            self.retries = False

            def __init__(self, *args, **kwargs):
                self.retries = 0
                super(InvalidRequest, self).__init__(*args, **kwargs)

            @property
            def remote_addr(self):
                self.retries += 1
                raise IntegrityError("INSERT INTO %(something)",
                                     {"something": "something"},
                                     "duplicate key")

        request = InvalidRequest(MultiDict({'body': 'xyz'}), post=True)
        request.context = self._getRoot(request)["general"][str(topic.id)]
        with self.assertRaises(IntegrityError):
            assert not topic_view(request)
        self.assertEqual(request.retries, 5)
        self.assertEqual(DBSession.query(Post).count(), 0)