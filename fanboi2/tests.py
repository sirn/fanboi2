# -*- coding: utf-8 -*-
import datetime
import os
import transaction
import unittest
from fanboi2 import DBSession, Base
from pyramid import testing
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from zope.interface.verify import verifyObject


DATABASE_URI = 'postgresql://fanboi2:dev@localhost:5432/fanboi2_test'


class DummyRedis(object):

    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key, None)

    def setnx(self, key, value):
        if not self.get(key):
            self._store[key] = bytes(value.encode('utf-8'))

    def expire(self, key, time):
        pass  # Do nothing.


class _ModelInstanceSetup(object):

    @classmethod
    def tearDownClass(cls):
        Base.metadata.bind = None
        DBSession.remove()

    def setUp(self):
        Base.metadata.drop_all()
        Base.metadata.create_all()
        transaction.begin()
        self.request = self._makeRequest()
        self.registry = self._makeRegistry()
        self.config = testing.setUp(
            request=self.request,
            registry=self.registry)

    def tearDown(self):
        testing.tearDown()
        transaction.abort()

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.redis = DummyRedis()
        return request

    def _makeRegistry(self):
        from pyramid.registry import Registry
        registry = Registry()
        registry.settings = {
            'app.timezone': 'Asia/Bangkok',
            'app.secret': 'Silently test in secret',
        }
        return registry

    def _makeBoard(self, **kwargs):
        from fanboi2.models import Board
        board = Board(**kwargs)
        DBSession.add(board)
        DBSession.flush()
        return board

    def _makeTopic(self, **kwargs):
        from fanboi2.models import Topic
        topic = Topic(**kwargs)
        DBSession.add(topic)
        DBSession.flush()
        return topic

    def _makePost(self, **kwargs):
        from fanboi2.models import Post
        if not kwargs.get('ip_address', None):
            kwargs['ip_address'] = '0.0.0.0'
        post = Post(**kwargs)
        DBSession.add(post)
        DBSession.flush()
        return post


class ModelMixin(_ModelInstanceSetup):

    @classmethod
    def setUpClass(cls):
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


class DummyStaticURLInfo:

    def __init__(self, result):
        self.result = result

    def generate(self, path, request, **kw):
        self.args = path, request, kw
        return self.result


class TestTaggedStaticUrl(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeRequest(self):
        from pyramid.url import URLMethodsMixin
        class Request(URLMethodsMixin):
            application_url = 'http://example.com:5432'
            script_name = ''
            def __init__(self, environ):
                self.environ = environ
                self.registry = None
        request = Request({})
        request.registry = self.config.registry
        return request

    def _getFunction(self):
        from fanboi2 import tagged_static_path
        return tagged_static_path

    def _getModified(self, package, path):
        import os
        from pyramid.path import AssetResolver
        abspath = AssetResolver(package).resolve(path).abspath()
        return int(os.path.getmtime(abspath))

    def test_tagged_static_path(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo('foobar')
        request = self._makeRequest()
        request.registry.registerUtility(info, IStaticURLInfo)
        result = self._getFunction()(request, 'fanboi2:tests.py')
        self.assertEqual(result, 'foobar')
        self.assertEqual(
            info.args, ('fanboi2:tests.py', request, {
                '_app_url': '',
                '_query': {'t': self._getModified('fanboi2', 'tests.py')}}))

    def test_tagged_static_path_non_exists(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo('foobar')
        request = self._makeRequest()
        request.registry.registerUtility(info, IStaticURLInfo)
        with self.assertRaises(OSError):
            self._getFunction()(request, 'fanboi2:static/notexists')

    def test_tagged_static_path_non_package(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo('foobar')
        request = self._makeRequest()
        request.registry.registerUtility(info, IStaticURLInfo)
        result = self._getFunction()(request, 'tests.py')
        self.assertEqual(result, 'foobar')
        self.assertEqual(
            info.args, ('fanboi2:tests.py', request, {
                '_app_url': '',
                '_query': {'t': self._getModified('fanboi2', 'tests.py')}}))

    def test_tagged_static_path_non_package_non_exists(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo('foobar')
        request = self._makeRequest()
        request.registry.registerUtility(info, IStaticURLInfo)
        with self.assertRaises(OSError):
            self._getFunction()(request, 'static/notexists')


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
            [(1, {'x': 1}), (2, None), (3, {})],
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

    def test_interface(self):
        from fanboi2.interfaces import IBoard
        board = self._makeBoard(title="Foobar", slug="foo")
        self.assertTrue(verifyObject(IBoard, board))

    def test_relations(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        self.assertEqual([], list(board.topics))

    def test_settings(self):
        from fanboi2.models import DBSession, DEFAULT_BOARD_CONFIG
        board = self._makeBoard(title="Foobar", slug="Foo")
        self.assertEqual(board.settings, DEFAULT_BOARD_CONFIG)
        board.settings = {'name': 'Hamster'}
        new_settings = DEFAULT_BOARD_CONFIG.copy()
        new_settings.update({'name': 'Hamster'})
        DBSession.add(board)
        DBSession.flush()
        self.assertEqual(board.settings, new_settings)

    def test_topics(self):
        from fanboi2.models import Topic
        board1 = self._makeBoard(title="Foobar", slug="foo")
        board2 = self._makeBoard(title="Lorem", slug="lorem")
        topic1 = Topic(board=board1, title="Heavenly Moon")
        topic2 = Topic(board=board1, title="Beastie Starter")
        topic3 = Topic(board=board1, title="Evans")
        DBSession.add(topic1)
        DBSession.add(topic2)
        DBSession.add(topic3)
        DBSession.flush()
        self.assertEqual({topic3, topic2, topic1}, set(board1.topics))
        self.assertEqual([], list(board2.topics))

    def test_topics_sort(self):
        from datetime import datetime, timedelta
        from fanboi2.models import Topic, Post
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = Topic(board=board, title="First!!!111")
        topic2 = Topic(board=board, title="11111111111!!!!!!!!!")
        topic3 = Topic(board=board, title="Third!!!11")
        DBSession.add(topic1)
        DBSession.add(topic2)
        DBSession.add(topic3)
        DBSession.flush()
        DBSession.add(Post(topic=topic1, body="!!1", ip_address="1.1.1.1"))
        DBSession.add(Post(
            topic=topic3,
            body="333",
            ip_address="3.3.3.3",
            created_at=datetime.now() + timedelta(seconds=3)))
        DBSession.add(Post(
            topic=topic2,
            body="LOOK HOW I'M TOTALLY THE FIRST POST!!",
            ip_address="1.1.1.1",
            created_at=datetime.now() + timedelta(seconds=5)))
        DBSession.flush()
        DBSession.refresh(board)
        self.assertEqual([topic2, topic3, topic1], list(board.topics))


class TopicModelTest(ModelMixin, unittest.TestCase):

    def test_interface(self):
        from fanboi2.interfaces import ITopic
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertTrue(verifyObject(ITopic, topic))

    def test_relations(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertEqual(topic.board, board)
        self.assertEqual([], list(topic.posts))
        self.assertEqual([topic], list(board.topics))

    def test_posts(self):
        from fanboi2.models import Post
        board = self._makeBoard(title="Foobar", slug="foo")
        topic1 = self._makeTopic(board=board, title="Lorem ipsum dolor")
        topic2 = self._makeTopic(board=board, title="Some lonely topic")
        post1 = Post(topic=topic1, body="Lorem", ip_address="0.0.0.0")
        post2 = Post(topic=topic1, body="Ipsum", ip_address="0.0.0.0")
        post3 = Post(topic=topic1, body="Dolor", ip_address="0.0.0.0")
        DBSession.add(post1)
        DBSession.add(post2)
        DBSession.add(post3)
        DBSession.flush()
        self.assertEqual([post1, post2, post3], list(topic1.posts))
        self.assertEqual([], list(topic2.posts))

    def test_auto_archive(self):
        from fanboi2.models import Post
        board = self._makeBoard(title="Foobar", slug="foo", settings={
            'max_posts': 5,
        })
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        for i in range(4):
            post = Post(topic=topic, body="Post %s" % i, ip_address="0.0.0.0")
            DBSession.add(post)
        DBSession.flush()
        self.assertEqual(topic.status, "open")
        DBSession.add(Post(topic=topic, body='Post 5', ip_address='0.0.0.0'))
        DBSession.flush()
        self.assertEqual(topic.status, "archived")

    def test_auto_archive_locked(self):
        from fanboi2.models import Post
        board = self._makeBoard(title="Foobar", slug="foo", settings={
            'max_posts': 3,
        })
        topic = self._makeTopic(board=board,
                                title="Lorem ipsum dolor",
                                status='locked')
        for i in range(3):
            post = Post(topic=topic, body="Post %s" % i, ip_address="0.0.0.0")
            DBSession.add(post)
        DBSession.flush()
        self.assertEqual(topic.status, "locked")

    def test_post_count(self):
        from fanboi2.models import Post
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
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
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
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

    def test_interface(self):
        from fanboi2.interfaces import IPost
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        post = self._makePost(topic=topic, body="Hello, world")
        self.assertTrue(verifyObject(IPost, post))

    def test_relations(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        post = self._makePost(topic=topic, body="Hello, world")
        self.assertEqual(post.topic, topic)
        self.assertEqual([post], list(topic.posts))

    def test_number(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic1 = self._makeTopic(board=board, title="Numbering one")
        topic2 = self._makeTopic(board=board, title="Numbering two")
        post1 = self._makePost(topic=topic1, body="Topic 1, post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, post 2")
        post3 = self._makePost(topic=topic2, body="Topic 2, post 1")
        post4 = self._makePost(topic=topic1, body="Topic 1, post 3")
        post5 = self._makePost(topic=topic2, body="Topic 2, post 2")
        # Force update to ensure its number remain the same.
        post4.body = "Topic1, post 3, updated!"
        DBSession.add(post4)
        DBSession.flush()
        self.assertEqual(post1.number, 1)
        self.assertEqual(post2.number, 2)
        self.assertEqual(post3.number, 1)
        self.assertEqual(post4.number, 3)
        self.assertEqual(post5.number, 2)

    def test_name(self):
        board = self._makeBoard(title="Foobar", slug="foo", settings={
            'name': 'Nobody Nowhere',
        })
        topic = self._makeTopic(board=board, title="No name!")
        post1 = self._makePost(topic=topic, body="I'm nameless")
        post2 = self._makePost(topic=topic, body="I have a name", name="John")
        self.assertEqual(post1.name, "Nobody Nowhere")
        self.assertEqual(post2.name, "John")

    def test_ident(self):
        board = self._makeBoard(title="Testbed", slug="test")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        post1 = self._makePost(topic=topic, body="Hi", ip_address="127.0.0.1")
        post2 = self._makePost(topic=topic, body="Yo", ip_address="10.0.1.18")
        post3 = self._makePost(topic=topic, body="Hey", ip_address="10.0.1.1")
        post4 = self._makePost(topic=topic, body="!!", ip_address="127.0.0.1")
        self.assertIsInstance(post1.ident, str)
        self.assertIsInstance(post4.ident, str)
        self.assertNotEqual(post1.ident, post2.ident)
        self.assertNotEqual(post1.ident, post3.ident)
        self.assertNotEqual(post2.ident, post3.ident)
        self.assertEqual(post1.ident, post4.ident)

    def test_ident_disabled(self):
        board = self._makeBoard(title="Testbed", slug="test", settings={
            'use_ident': False,
        })
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        post1 = self._makePost(topic=topic, body="Hi", ip_address="127.0.0.1")
        post2 = self._makePost(topic=topic, body="Yo", ip_address="10.0.2.8")
        self.assertIsNone(post1.ident)
        self.assertIsNone(post2.ident)

    def test_ident_namespaced(self):
        board1 = self._makeBoard(title="Test 1", slug="test1")
        board2 = self._makeBoard(title="Test 2", slug="test2")
        topic1 = self._makeTopic(board=board1, title="First topic")
        topic2 = self._makeTopic(board=board2, title="Second topic")
        p1 = self._makePost(topic=topic1, body="Test", ip_address="10.0.1.1")
        p2 = self._makePost(topic=topic2, body="Test", ip_address="10.0.1.1")
        self.assertNotEqual(p1.ident, p2.ident)


class BaseContainerTest(unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.resources import BaseContainer

        class MockContainer(BaseContainer):
            pass
        return MockContainer

    def test_init(self):
        container = self._getTargetClass()("request")
        self.assertEqual(container.request, "request")
        self.assertEqual(container.__parent__, None)
        self.assertEqual(container.__name__, None)

    def test_root(self):
        class MockRootContainer(object):
            @property
            def root(self):
                return self

        mock = MockRootContainer()
        container = self._getTargetClass()({})
        container.__parent__ = mock
        self.assertEqual(container.root, mock)

    def test_boards(self):
        class MockBoardsContainer(object):
            @property
            def boards(self):
                return self

        mock = MockBoardsContainer()
        container = self._getTargetClass()({})
        container.__parent__ = mock
        self.assertEqual(container.boards, mock)

    def test_board(self):
        class MockBoardContainer(object):
            @property
            def board(self):
                return self

        mock = MockBoardContainer()
        container = self._getTargetClass()({})
        container.__parent__ = mock
        self.assertEqual(container.board, mock)

    def test_topic(self):
        class MockTopicContainer(object):
            @property
            def topic(self):
                return self

        mock = MockTopicContainer()
        container = self._getTargetClass()({})
        container.__parent__ = mock
        self.assertEqual(container.topic, mock)


class RootFactoryTest(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.resources import RootFactory
        return RootFactory

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

    def test_accessors(self):
        root = self._getTargetClass()({})
        self.assertEqual(root.root, root)
        self.assertEqual(root.boards, root.objs)

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

    def test_interface(self):
        from fanboi2.interfaces import IBoardResource
        container = self._getTargetClass()({}, None)
        self.assertTrue(verifyObject(IBoardResource, container))

    def test_objs(self):
        from fanboi2.models import Topic
        board = self._makeBoard(title="General", slug="general")
        topics = []
        for i in range(11):
            topic = Topic(board=board, title="Topic %i" % i)
            topics.append(topic)
            DBSession.add(topic)
        DBSession.flush()
        container = self._getTargetClass()({}, board)
        self.assertEqual(container.objs[0].__parent__, container)
        self.assertEqual(container.objs[0].__name__, topics[0].id)
        self.assertNotIn(topics[-1], [t.obj for t in container.objs])
        self.assertEqual(set(topics[:10]), {t.obj for t in container.objs})

    def test_objs_all(self):
        from fanboi2.models import Topic, Post
        board = self._makeBoard(title="General", slug="general")
        topics = []
        old_topic = self._makeTopic(board=board, title="Really old topic")
        old_topic.status = 'archived'
        old_post = Post(topic=old_topic, body="Hi!", ip_address="0.0.0.0")
        old_post.created_at = datetime.datetime.now() - \
                              datetime.timedelta(days=8)
        DBSession.add(old_topic)
        DBSession.add(old_post)
        newer_topic = self._makeTopic(board=board, title="Newer old topic")
        newer_topic.status = 'locked'
        newer_post = Post(topic=newer_topic, body="Hi!", ip_address="0.0.0.0")
        newer_post.created_at = datetime.datetime.now() - \
                                datetime.timedelta(days=2)
        DBSession.add(newer_topic)
        DBSession.add(newer_post)
        date_start = datetime.datetime.now()
        for i in range(13):
            topic = Topic(board=board, title="Topic %i" % i)
            post = Post(topic=topic, body="Hello!", ip_address="0.0.0.0")
            post.created_at = date_start
            date_start = date_start - datetime.timedelta(days=1)
            topics.append(topic)
            DBSession.add(topic)
            DBSession.add(post)
        DBSession.flush()
        container = self._getTargetClass()({}, board)
        self.assertEqual(14, len(container.objs_all))
        self.assertNotIn(old_topic, [t.obj for t in container.objs_all])
        self.assertEqual(set(topics + [newer_topic]),
                         {t.obj for t in container.objs_all})


    def test_accessors(self):
        from fanboi2.resources import RootFactory
        root = RootFactory({})
        board = self._makeBoard(title="General", slug="general")
        container = self._getTargetClass()({}, board)
        container.__parent__ = root
        self.assertEqual(container.root, root)
        self.assertEqual(container.boards, root.objs)
        self.assertEqual(container.board, container)
        self.assertRaises(AttributeError, lambda: container.topic)

    def test_getitem(self):
        board = self._makeBoard(title="General", slug="general")
        topic1 = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        topic2 = self._makeTopic(board=board, title="Hello, world")
        container = self._getTargetClass()({}, board)
        self.assertEqual(container[topic1.id].obj, topic1)
        self.assertEqual(container[topic2.id].obj, topic2)

    def test_getitem_notfound(self):
        board = self._makeBoard(title="General", slug="general")
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

    def test_objs(self):
        board = self._makeBoard(title="General", slug="general")
        topic1 = self._makeTopic(board=board, title="Boring topic is boring")
        topic2 = self._makeTopic(board=board, title="Yo dawg")
        self._makePost(topic=topic2, body="I heard you like blah blah")
        post1 = self._makePost(topic=topic1, body="Hello, world")
        post2 = self._makePost(topic=topic1, body="Blah blah blah")
        post3 = self._makePost(topic=topic1, body="Lorem ipsum dolor")
        container = self._getTargetClass()({}, topic1)
        self.assertEqual(container.objs[0].__parent__, container)
        self.assertEqual(container.objs[0].__name__, post1.number)
        self.assertEqual([post1, post2, post3],
                         [p.obj for p in container.objs])

    def test_accessors(self):
        from fanboi2.resources import RootFactory, BoardContainer
        root = RootFactory({})
        board = BoardContainer({}, self._makeBoard(title="Foo", slug="foo"))
        board.__parent__ = root
        topic = self._makeTopic(board=board.obj, title="At first I was like...")
        container = self._getTargetClass()({}, topic)
        container.__parent__ = board
        self.assertEqual(container.root, root)
        self.assertEqual(container.boards, root.objs)
        self.assertEqual(container.board, board)
        self.assertEqual(container.topic, container)

    def test_getitem(self):
        from fanboi2.resources import ScopedTopicContainer
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        self._makePost(topic=topic, body="Hello, world!")
        self._makePost(topic=topic, body="Blah post!")
        container = self._getTargetClass()({}, topic)
        container.__parent__ = 'Foo'
        container.__name__ = 'Bar'
        self.assertIsInstance(container["1"], ScopedTopicContainer)
        self.assertIsInstance(container["1-10"], ScopedTopicContainer)
        self.assertIsInstance(container["recent"], ScopedTopicContainer)
        self.assertEqual(container["1"].__parent__, container.__parent__)
        self.assertEqual(container["1"].__name__, container.__name__)

    def test_getitem_notfound(self):
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        self._makePost(topic=topic, body="Hello, world!")
        container = self._getTargetClass()({}, topic)
        self.assertRaises(KeyError, lambda: container["2"])   # Not found
        self.assertRaises(KeyError, lambda: container["2-3"])  # Not found
        self.assertRaises(KeyError, lambda: container["invalid"])


class ScopedTopicContainerTest(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.resources import ScopedTopicContainer
        return ScopedTopicContainer

    def _wrapTopic(self, topic, request={}):
        from fanboi2.resources import TopicContainer
        return TopicContainer(request, topic)

    def test_interface(self):
        from fanboi2.interfaces import ITopicResource
        from fanboi2.resources import TopicContainer
        # Blah, need to pass in the real object since this method will raise
        # KeyError on invalid init.
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic = self._makeTopic(board=board, title="Foo bar foo bar")
        self._makePost(topic=topic, body="Blah, blah, blah")
        topic_container = TopicContainer({}, topic)
        container = self._getTargetClass()({}, topic_container, "1")
        self.assertTrue(verifyObject(ITopicResource, container))

    def test_objs(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic = self._makeTopic(board=board, title="Hello, world!")
        post1 = self._makePost(topic=topic, body="Blah, hello, hi")
        topic_container = self._wrapTopic(topic)
        container = self._getTargetClass()({}, topic_container, "1")
        self.assertEqual(container.objs[0].__parent__, topic_container)
        self.assertEqual(container.objs[0].__name__, post1.number)

    def test_accessors(self):
        from fanboi2.resources import RootFactory, BoardContainer
        root = RootFactory({})
        board = BoardContainer({}, self._makeBoard(title="Foo", slug="foo"))
        board.__parent__ = root
        obj = self._makeTopic(board=board.obj, title="Foobar blah blah")
        self._makePost(topic=obj, body="Hello world foo bar")
        topic = self._wrapTopic(obj)
        topic.__parent__ = board
        container = self._getTargetClass()({}, topic, "1")
        container.__parent__ = topic
        self.assertEqual(container.root, root)
        self.assertEqual(container.boards, root.objs)
        self.assertEqual(container.board, board)
        self.assertEqual(container.topic, topic)

    def test_number_query(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another post!!1")
        post1 = self._makePost(topic=topic1, body="Post 1")
        post2 = self._makePost(topic=topic2, body="Post 1")
        post3 = self._makePost(topic=topic1, body="Post 2")
        post4 = self._makePost(topic=topic2, body="Post 2")
        topic_container = self._wrapTopic(topic1)
        container = self._getTargetClass()({}, topic_container, "2")
        self.assertEqual(container.objs[0].__parent__, topic_container)
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
        topic_container = self._wrapTopic(topic1)
        container = self._getTargetClass()({}, topic_container, "2-5")
        self.assertEqual(container.objs[0].__parent__, topic_container)
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
        topic_container = self._wrapTopic(topic1)
        container = self._getTargetClass()({}, topic_container, "3-")
        self.assertEqual(container.objs[0].__parent__, topic_container)
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
        topic_container = self._wrapTopic(topic1)
        container = self._getTargetClass()({}, topic_container, "-3")
        self.assertEqual(container.objs[0].__parent__, topic_container)
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
        topic_container = self._wrapTopic(topic2)
        container = self._getTargetClass()({}, topic_container, "recent")
        self.assertEqual(container.objs[0].__parent__, topic_container)
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

    def test_accessors(self):
        from fanboi2.resources import RootFactory, BoardContainer, \
            TopicContainer
        root = RootFactory({})
        board = BoardContainer({}, self._makeBoard(title="Foo", slug="foo"))
        board.__parent__ = root
        topic = TopicContainer({}, self._makeTopic(board=board.obj,
                                                   title="Blah blah"))
        topic.__parent__ = board
        container = self._getTargetClass()({}, self._makePost(topic=topic.obj,
                                                              body="Hello"))
        container.__parent__ = topic
        self.assertEqual(container.root, root)
        self.assertEqual(container.boards, root.objs)
        self.assertEqual(container.board, board)
        self.assertEqual(container.topic, topic)


class TestSecureForm(unittest.TestCase):

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.registry.settings = {'app.secret': 'TESTME'}
        return request

    def _makeForm(self, data):
        from webob.multidict import MultiDict
        return MultiDict(data)

    def _makeOne(self, form, request):
        from fanboi2.forms import SecureForm
        form = SecureForm(self._makeForm(form), request=request)
        form.validate()
        return form

    def test_csrf_token(self):
        import hmac
        from hashlib import sha1
        request = self._makeRequest()
        request.session['csrf'] = sha1(os.urandom(64)).hexdigest()
        token = hmac.new(
            bytes(request.registry.settings['app.secret'].encode('utf8')),
            bytes(request.session['csrf'].encode('utf8')),
            digestmod=sha1,
        ).hexdigest()
        form = self._makeOne({'csrf_token': token}, request)
        self.assertTrue(form.validate())
        self.assertEqual(form.errors, {})

    def test_csrf_token_empty(self):
        request = self._makeRequest()
        form = self._makeOne({}, request)
        self.assertDictEqual(form.errors, {
            'csrf_token': ['CSRF token missing'],
        })

    def test_csrf_token_invalid(self):
        request = self._makeRequest()
        form = self._makeOne({'csrf_token': 'invalid'}, request)
        self.assertDictEqual(form.errors, {
            'csrf_token': ['CSRF token mismatched'],
        })

    def test_data(self):
        request = self._makeRequest()
        form = self._makeOne({'csrf_token': 'strip_me'}, request)
        self.assertDictEqual(form.data, {})


class TestFormatters(unittest.TestCase):

    def _makeRegistry(self):
        from pyramid.registry import Registry
        registry = Registry()
        registry.settings = {'app.timezone': 'Asia/Bangkok'}
        return registry

    def test_extract_thumbnail(self):
        from fanboi2.formatters import extract_thumbnail
        text = """
        Inline page: http://imgur.com/image1
        Inline image: http://i.imgur.com/image2.jpg
        Subdomain image: http://fanboi2.imgur.com/image3.png

        http://i.imgur.com/image4.jpeg
        http://i.imgur.com/image5.gif
        http://imgur.com/<script>alert("haxx0red!!")</script>.jpg
        http://<script></script>.imgur.com/image6.gif
        http://imgur.com/ほげ

        Lorem ipsum dolor sit amet.

        https://imgur.com/image5
        https://i.imgur.com/image7.jpg
        """
        self.assertTupleEqual(tuple(extract_thumbnail(text)), (
            ('http://i.imgur.com/image1s.jpg', 'http://imgur.com/image1'),
            ('http://i.imgur.com/image2s.jpg', 'http://imgur.com/image2'),
            ('http://i.imgur.com/image3s.jpg', 'http://imgur.com/image3'),
            ('http://i.imgur.com/image4s.jpg', 'http://imgur.com/image4'),
            ('http://i.imgur.com/image5s.jpg', 'http://imgur.com/image5'),
            ('http://i.imgur.com/image7s.jpg', 'http://imgur.com/image7'),
        ))

    def test_format_text(self):
        from fanboi2.formatters import format_text
        from jinja2 import Markup
        tests = [
            ('Hello, world!', '<p>Hello, world!</p>'),
            ('H\n\n\nello\nworld', '<p>H</p>\n<p>ello<br>world</p>'),
            ('Foo\r\n\r\n\r\n\nBar', '<p>Foo</p>\n<p><br>Bar</p>'),
            ('Newline at the end\n', '<p>Newline at the end</p>'),
            ('STRIP ME!!!1\n\n', '<p>STRIP ME!!!1</p>'),
            ('ほげ\n\nほげ', '<p>ほげ</p>\n<p>ほげ</p>'),
            ('ไก่จิกเด็ก\n\nตายบนปากโอ่ง',
             '<p>ไก่จิกเด็ก</p>\n<p>ตายบนปากโอ่ง</p>'),
            ('<script></script>', '<p>&lt;script&gt;&lt;/script&gt;</p>'),
        ]
        for source, target in tests:
            self.assertEqual(format_text(source), Markup(target))

    def test_format_text_thumbnail(self):
        from fanboi2.formatters import format_text
        from jinja2 import Markup
        text = ("New product! https://imgur.com/foobar1\n\n"
                "http://i.imgur.com/foobar2.png\n"
                "http://imgur.com/foobar3.jpg\n"
                "Buy today get TWO for FREE!!1")
        self.assertEqual(
            format_text(text),
            Markup('<p>New product! https://imgur.com/foobar1</p>\n'
                   '<p>http://i.imgur.com/foobar2.png<br>'
                      'http://imgur.com/foobar3.jpg<br>'
                      'Buy today get TWO for FREE!!1</p>\n'
                   '<p><a href="http://imgur.com/foobar1" '
                         'class="thumbnail" target="_blank">'
                         '<img src="http://i.imgur.com/foobar1s.jpg">'
                         '</a>'
                       '<a href="http://imgur.com/foobar2" '
                         'class="thumbnail" target="_blank">'
                         '<img src="http://i.imgur.com/foobar2s.jpg">'
                         '</a>'
                       '<a href="http://imgur.com/foobar3" '
                         'class="thumbnail" target="_blank">'
                         '<img src="http://i.imgur.com/foobar3s.jpg">'
                         '</a>'
                       '</p>'))

    def test_format_markdown(self):
        from fanboi2.formatters import format_markdown
        from jinja2 import Markup
        tests = [
            ('**Hello, world!**', '<p><strong>Hello, world!</strong></p>\n'),
            ('<b>Foobar</b>', '<p><b>Foobar</b></p>\n'),
            ('Split\n\nParagraph', '<p>Split</p>\n\n<p>Paragraph</p>\n'),
            ('Split\nlines', '<p>Split\nlines</p>\n'),
        ]
        for source, target in tests:
            self.assertEqual(format_markdown(source), Markup(target))

    def test_format_datetime(self):
        from datetime import datetime, timezone
        from fanboi2.formatters import format_datetime
        testing.setUp(registry=self._makeRegistry())
        d1 = datetime(2013, 1, 2, 0, 4, 1, 0, timezone.utc)
        d2 = datetime(2012, 12, 31, 16, 59, 59, 0, timezone.utc)
        self.assertEqual(format_datetime(d1), "Jan 02, 2013 at 07:04:01")
        self.assertEqual(format_datetime(d2), "Dec 31, 2012 at 23:59:59")

    def test_format_isotime(self):
        from datetime import datetime, timezone, timedelta
        from fanboi2.formatters import format_isotime
        ict = timezone(timedelta(hours=7))
        testing.setUp(registry=self._makeRegistry())
        d1 = datetime(2013, 1, 2, 7, 4, 1, 0, ict)
        d2 = datetime(2012, 12, 31, 23, 59, 59, 0, ict)
        self.assertEqual(format_isotime(d1), "2013-01-02T00:04:01Z")
        self.assertEqual(format_isotime(d2), "2012-12-31T16:59:59Z")


class TestFormattersWithModel(ModelMixin, unittest.TestCase):

    def _wrapBoard(self, **kwargs):
        from fanboi2.resources import RootFactory, BoardContainer
        board = self._makeBoard(**kwargs)
        container = BoardContainer({}, board)
        container.__name__ = board.slug
        container.__parent__ = RootFactory({})
        return container

    def _wrapTopic(self, board_container, **kwargs):
        from fanboi2.resources import TopicContainer
        kwargs['board'] = board_container.obj
        topic = self._makeTopic(**kwargs)
        container = TopicContainer({}, topic)
        container.__name__ = topic.id
        container.__parent__ = board_container
        return container

    def _wrapPost(self, topic_container, **kwargs):
        from fanboi2.resources import PostContainer
        kwargs['topic'] = topic_container.obj
        post = self._makePost(**kwargs)
        container = PostContainer({}, post)
        container.__parent__ = topic_container
        container.__name__ = post.number
        return container

    def test_format_post(self):
        from fanboi2.formatters import format_post
        from jinja2 import Markup
        board = self._wrapBoard(title="Foobar", slug="foobar")
        topic = self._wrapTopic(board, title="Hogehogehogehogehoge")
        post1 = self._wrapPost(topic, body="Hogehoge\nHogehoge")
        post2 = self._wrapPost(topic, body=">>1")
        post3 = self._wrapPost(topic, body=">>1-2\nHoge")
        tests = [
            (post1, "<p>Hogehoge<br>Hogehoge</p>"),
            (post2, "<p><a href=\"/foobar/1/1\" class=\"anchor\">" +
                    "&gt;&gt;1</a></p>"),
            (post3, "<p><a href=\"/foobar/1/1-2\" class=\"anchor\">" +
                    "&gt;&gt;1-2</a><br>Hoge</p>"),
        ]
        for source, target in tests:
            self.assertEqual(format_post(source), Markup(target))


class TestViews(ModelMixin, unittest.TestCase):

    def _getRoot(self, request=None):
        from fanboi2.resources import RootFactory
        if request is None:
            request = self.request
        return RootFactory(request)

    def _make_csrf(self, request):
        import hmac
        from hashlib import sha1
        request.session['csrf'] = sha1(os.urandom(64)).hexdigest()
        request.params['csrf_token'] = hmac.new(
            bytes(request.registry.settings['app.secret'].encode('utf8')),
            bytes(request.session['csrf'].encode('utf8')),
            digestmod=sha1,
        ).hexdigest()
        return request

    def _POST(self, data=None):
        from webob.multidict import MultiDict
        self.request.method = 'POST'
        self.request.remote_addr = "127.0.0.1"
        self.request.params = MultiDict(data)
        return self.request

    def _GET(self, data=None):
        from webob.multidict import MultiDict
        if data is None:
            data = {}
        self.request.remote_addr = "127.0.0.1"
        self.request.params = MultiDict(data)
        return self.request

    def test_root_view(self):
        from fanboi2.views import root_view
        board1 = self._makeBoard(title="General", slug="general")
        board2 = self._makeBoard(title="Foobar", slug="foo")
        request = self._GET()
        request.context = self._getRoot()
        view = root_view(request)
        self.assertEqual(request.resource_path(view["boards"][0]), "/foo/")
        self.assertEqual([board2, board1],
                         [b.obj for b in view["boards"]])

    def test_board_view(self):
        from fanboi2.views import board_view
        board = self._makeBoard(title="General", slug="general")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Python!!!11one")
        request = self._GET()
        request.context = self._getRoot()["general"]
        view = board_view(request)
        self.assertEqual([board], [b.obj for b in view["boards"]])
        self.assertEqual(view["board"].obj, board)
        self.assertEqual(request.resource_path(view["topics"][0]),
                         "/general/%s/" % topic1.id)
        self.assertEqual({topic1, topic2},
                         {t.obj for t in view["topics"]})

    def test_all_board_view(self):
        from fanboi2.views import all_board_view
        board = self._makeBoard(title="General", slug="general")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Foobar")
        request = self._GET()
        request.context = self._getRoot()["general"]
        view = all_board_view(request)
        self.assertEqual([board], [b.obj for b in view["boards"]])
        self.assertEqual(view["board"].obj, board)
        self.assertEqual(request.resource_path(view["topics"][0]),
                         "/general/%s/" % topic1.id)
        self.assertEqual({topic1, topic2},
                         {t.obj for t in view["topics"]})

    def test_new_board_view_get(self):
        from fanboi2.views import new_board_view
        board = self._makeBoard(title="General", slug="general")
        request = self._GET()
        request.context = self._getRoot()["general"]
        view = new_board_view(request)
        self.assertEqual([board], [b.obj for b in view["boards"]])
        self.assertEqual(view["board"].obj, board)
        self.assertDictEqual(view["form"].errors, {})

    def test_new_board_view_post(self):
        from fanboi2.views import new_board_view
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title="General", slug="general")
        request = self._make_csrf(self._POST({
            'title': "One more thing...",
            'body': "And now for something completely different...",
        }))
        request.context = self._getRoot()["general"]
        response = new_board_view(request)
        self.assertEqual(DBSession.query(Topic).count(), 1)
        self.assertEqual(response.location, "/general/")

    def test_new_board_view_post_failure(self):
        from fanboi2.views import new_board_view
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title="General", slug="general")
        request = self._make_csrf(self._POST({
            'title': "One more thing...",
            'body': "",
        }))
        request.context = self._getRoot()["general"]
        view = new_board_view(request)
        self.assertEqual(DBSession.query(Topic).count(), 0)
        self.assertEqual(view["form"].title.data, 'One more thing...')
        self.assertDictEqual(view["form"].errors, {
            'body': ['This field is required.']
        })

    def test_topic_view_get(self):
        from fanboi2.views import topic_view
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        post1 = self._makePost(topic=topic, body="Hello, world!")
        post2 = self._makePost(topic=topic, body="Boring post is boring!")
        request = self._GET()
        request.context = self._getRoot()["general"][str(topic.id)]
        view = topic_view(request)
        self.assertEqual([board], [b.obj for b in view["boards"]])
        self.assertEqual(view["board"].obj, board)
        self.assertEqual(view["topic"].obj, topic)
        self.assertDictEqual(view["form"].errors, {})
        self.assertEqual([post1, post2],
                         [p.obj for p in view["posts"]])

    def test_topic_view_get_scoped(self):
        from fanboi2.views import topic_view
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Hello, world!")
        post1 = self._makePost(topic=topic, body="Boring test is boring!")
        post2 = self._makePost(topic=topic, body="Boring post is boring!")
        request = self._GET()
        request.context = self._getRoot()["foo"][str(topic.id)]["2"]
        view = topic_view(request)
        self.assertEqual([board], [b.obj for b in view["boards"]])
        self.assertEqual(view["board"].obj, board)
        self.assertEqual(view["topic"].obj, topic)
        self.assertDictEqual(view["form"].errors, {})
        self.assertEqual([post2], [p.obj for p in view["posts"]])

    def test_topic_view_post(self):
        from fanboi2.views import topic_view
        from fanboi2.models import DBSession, Post, DEFAULT_BOARD_CONFIG
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        request = self._make_csrf(self._POST({'body': "Boring post..."}))
        request.context = self._getRoot()["general"][str(topic.id)]
        response = topic_view(request)
        self.assertEqual(DBSession.query(Post).count(), 1)
        self.assertEqual(response.location, "/general/%s/" % topic.id)
        self.assertEqual(DBSession.query(Post).first().name,
                         DEFAULT_BOARD_CONFIG['name'])

    def test_topic_view_post_failure(self):
        from fanboi2.views import topic_view
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        request = self._make_csrf(self._POST({'body': 'x'}))
        request.context = self._getRoot()["general"][str(topic.id)]
        view = topic_view(request)
        self.assertEqual(DBSession.query(Post).count(), 0)
        self.assertEqual(view["form"].body.data, 'x')
        self.assertDictEqual(view["form"].errors, {
            'body': ['Field must be between 2 and 4000 characters long.'],
        })

    def test_topic_view_post_repeatable(self):
        from fanboi2.models import DBSession, Post
        from fanboi2.views import topic_view
        from sqlalchemy.exc import IntegrityError
        from webob.multidict import MultiDict
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
        request = self._make_csrf(request)
        request.context = self._getRoot(request)["general"][str(topic.id)]
        with self.assertRaises(IntegrityError):
            assert not topic_view(request)
        self.assertEqual(request.retries, 5)
        self.assertEqual(DBSession.query(Post).count(), 0)

    def test_topic_view_post_archived(self):
        from fanboi2.models import DBSession, Post
        from fanboi2.views import topic_view
        board = self._makeBoard(title="Foo", slug="foo")
        topic = self._makeTopic(board=board, title="Hoge", status='archived')
        self.assertEqual(DBSession.query(Post).count(), 0)
        request = self._make_csrf(self._POST({
            'body': "Topic is archived and post shouldn't get through."
        }))
        request.context = self._getRoot()["foo"][str(topic.id)]
        self.config.testing_add_renderer('topics/error.jinja2')
        topic_view(request)
        self.assertEqual(DBSession.query(Post).count(), 0)

    def test_topic_view_post_locked(self):
        from fanboi2.models import DBSession, Post
        from fanboi2.views import topic_view
        board = self._makeBoard(title="Foo", slug="foo")
        topic = self._makeTopic(board=board, title="Hoge", status='locked')
        self.assertEqual(DBSession.query(Post).count(), 0)
        request = self._make_csrf(self._POST({
            'body': "Topic is locked and post shouldn't get through."
        }))
        request.context = self._getRoot()["foo"][str(topic.id)]
        self.config.testing_add_renderer('topics/error.jinja2')
        topic_view(request)
        self.assertEqual(DBSession.query(Post).count(), 0)
