# -*- coding: utf-8 -*-
import mock
import os
import transaction
import unittest
from fanboi2 import DBSession, Base, redis_conn
from pyramid import testing
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


DATABASE_URI = os.environ.get(
    'POSTGRESQL_TEST_DATABASE',
    'postgresql://fanboi2:fanboi2@localhost:5432/fanboi2_test')


class DummyRedis(object):

    @classmethod
    def from_url(cls, *args, **kwargs):
        return cls()

    def __init__(self):
        self._store = {}
        self._expire = {}

    def get(self, key):
        return self._store.get(key, None)

    def set(self, key, value):
        try:
            value = bytes(value.encode('utf-8'))
        except AttributeError:
            pass
        self._store[key] = value

    def setnx(self, key, value):
        if not self.get(key):
            self.set(key, value)

    def exists(self, key):
        return key in self._store

    def expire(self, key, time):
        self._expire[key] = time

    def ttl(self, key):
        return self._expire.get(key, 0)

    def ping(self):
        return True


class _ModelInstanceSetup(object):

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
    def tearDownClass(cls):
        Base.metadata.bind = None
        DBSession.remove()

    @classmethod
    def setUpClass(cls):
        engine = create_engine(DATABASE_URI)
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine

    def setUp(self):
        redis_conn._redis = DummyRedis()
        Base.metadata.drop_all()
        Base.metadata.create_all()
        transaction.begin()
        self.request = self._makeRequest()
        self.registry = self._makeRegistry()
        self.config = testing.setUp(
            request=self.request,
            registry=self.registry)

    def tearDown(self):
        redis_conn._redis = None
        testing.tearDown()
        transaction.abort()

    def _makeRequest(self):
        request = testing.DummyRequest()
        return request

    def _makeRegistry(self):
        from pyramid.registry import Registry
        registry = Registry()
        registry.settings = {
            'app.timezone': 'Asia/Bangkok',
            'app.secret': 'Silently test in secret',
        }
        return registry


class ViewMixin(object):

    def _make_csrf(self, request):
        import hmac
        import os
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
        request = self.request
        request.method = 'POST'
        request.remote_addr = "127.0.0.1"
        request.params = MultiDict(data)
        return request

    def _GET(self, data=None):
        from webob.multidict import MultiDict
        request = self.request
        if data is None:
            data = {}
        request.remote_addr = "127.0.0.1"
        request.params = MultiDict(data)
        return request


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


class TestRouteName(unittest.TestCase):

    def _getFunction(self):
        from fanboi2 import route_name
        return route_name

    def _makeRequest(self, name):
        request = testing.DummyRequest()
        class MockMatchedRoute(object):
            def __init__(self, name):
                self.name = name
        request.matched_route = MockMatchedRoute(name)
        return request

    def test_route_name(self):
        request = self._makeRequest("foobar")
        self.assertEqual(self._getFunction()(request), "foobar")


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

    def _getHash(self, package, path):
        import hashlib
        from pyramid.path import AssetResolver
        abspath = AssetResolver(package).resolve(path).abspath()
        with open(abspath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()[:8]

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
                '_query': {'h': self._getHash('fanboi2', 'tests.py')}}))

    def test_tagged_static_path_non_exists(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo('foobar')
        request = self._makeRequest()
        request.registry.registerUtility(info, IStaticURLInfo)
        with self.assertRaises(IOError):
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
                '_query': {'h': self._getHash('fanboi2', 'tests.py')}}))

    def test_tagged_static_path_non_package_non_exists(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo('foobar')
        request = self._makeRequest()
        request.registry.registerUtility(info, IStaticURLInfo)
        with self.assertRaises(IOError):
            self._getFunction()(request, 'static/notexists')


class TestRedisProxy(unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.models import RedisProxy
        return RedisProxy

    def test_init(self):
        conn = self._getTargetClass()(cls=DummyRedis)
        self.assertEqual(conn._cls, DummyRedis)
        self.assertEqual(conn._redis, None)

    def test_from_url(self):
        conn = self._getTargetClass()(cls=DummyRedis)
        conn.from_url("redis:///")
        self.assertIsInstance(conn._redis, DummyRedis)

    def test_geattr(self):
        conn = self._getTargetClass()(cls=DummyRedis)
        conn.from_url("redis:///")
        self.assertTrue(conn.ping())

    def test_getattr_not_initialized(self):
        conn = self._getTargetClass()(cls=DummyRedis)
        with self.assertRaises(RuntimeError):
            conn.ping()


class TestIdentity(unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.models import Identity
        return Identity

    def _makeOne(self):
        identity = self._getTargetClass()(redis=DummyRedis())
        return identity

    def test_key(self):
        from pytz import utc
        from datetime import datetime
        identity = self._makeOne()
        self.assertTrue(
            identity._key("127.0.0.1", namespace="foobar"),
            "ident:{}:foobar:f528764d624db129b32c21fbca0cb8d6".format(
                datetime.now(utc).strftime("%Y%m%d")))

    def test_key_timezone(self):
        from pytz import timezone
        from datetime import datetime
        identity = self._makeOne()
        identity.configure_tz("Asia/Bangkok")
        self.assertTrue(
            identity._key("127.0.0.1", namespace="foobar"),
            "ident:{}:foobar:f528764d624db129b32c21fbca0cb8d6".format(
                datetime.now(timezone("Asia/Bangkok")).strftime("%Y%m%d")))

    def test_get(self):
        identity = self._makeOne()
        ident1 = identity.get("127.0.0.1")
        ident2 = identity.get("127.0.0.1", "foobar")
        ident3 = identity.get("192.168.1.1", "foobar")
        self.assertNotEqual(ident1, ident2)
        self.assertNotEqual(ident1, ident3)
        self.assertNotEqual(ident2, ident3)
        self.assertEqual(identity.get("127.0.0.1"), ident1)


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
        post1 = self._makePost(topic=topic1, body='Lorem')
        post2 = self._makePost(topic=topic1, body='Ipsum')
        post3 = self._makePost(topic=topic1, body='Dolor')
        self.assertEqual([post1, post2, post3], list(topic1.posts))
        self.assertEqual([], list(topic2.posts))

    def test_auto_archive(self):
        board = self._makeBoard(title="Foobar", slug="foo", settings={
            'max_posts': 5,
        })
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        for i in range(4):
            self._makePost(topic=topic, body="Post %s" % i)
        self.assertEqual(topic.status, "open")
        self._makePost(topic=topic, body="Post 5")
        self.assertEqual(topic.status, "archived")

    def test_auto_archive_locked(self):
        board = self._makeBoard(title="Foobar", slug="foo", settings={
            'max_posts': 3,
        })
        topic = self._makeTopic(board=board,
                                title="Lorem ipsum dolor",
                                status='locked')
        for i in range(3):
            post = self._makePost(topic=topic, body="Post %s" % i)
        self.assertEqual(topic.status, "locked")

    def test_post_count(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertEqual(topic.post_count, 0)
        for x in range(3):
            self._makePost(topic=topic, body="Hello, world!")
        self.assertEqual(topic.post_count, 3)

    def test_post_count_missing(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertEqual(topic.post_count, 0)
        for x in range(2):
            self._makePost(topic=topic, body="Hello, world!")
        post = self._makePost(topic=topic, body="Hello, world!")
        self._makePost(topic=topic, body="Hello, world!")
        self.assertEqual(topic.post_count, 4)
        DBSession.delete(post)
        DBSession.flush()
        DBSession.expire(topic, ['post_count'])
        self.assertEqual(topic.post_count, 4)

    def test_posted_at(self):
        from datetime import datetime, timezone
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertIsNone(topic.posted_at)
        for x in range(2):
            self._makePost(
                topic=topic,
                body="Hello, world!",
                created_at=datetime(2013, 1, 2, 0, 4, 1, 0, timezone.utc))
        post = self._makePost(topic=topic, body="Hello, world!")
        self.assertEqual(topic.created_at, post.created_at)

    def test_bumped_at(self):
        from datetime import datetime, timezone
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertIsNone(topic.bumped_at)
        post1 = self._makePost(
            topic=topic,
            body="Hello, world",
            created_at=datetime(2013, 1, 2, 0, 4, 1, 0, timezone.utc))
        post2 = self._makePost(topic=topic, body="Spam!", bumped=False)
        self.assertEqual(topic.bumped_at, post1.created_at)
        self.assertNotEqual(topic.bumped_at, post2.created_at)

    def test_scoped_posts(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic = self._makeTopic(board=board, title="Hello, world!")
        post1 = self._makePost(topic=topic, body="Post 1")
        post2 = self._makePost(topic=topic, body="Post 2")
        post3 = self._makePost(topic=topic, body="Post 3")
        self.assertListEqual(topic.scoped_posts(None), [post1, post2, post3])
        self.assertListEqual(topic.scoped_posts("bogus"), [])

    def test_single_post(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another post!!1")
        topic3 = self._makeTopic(board=board, title="Empty topic")
        post1 = self._makePost(topic=topic1, body="Post 1")
        post2 = self._makePost(topic=topic2, body="Post 1")
        post3 = self._makePost(topic=topic1, body="Post 2")
        post4 = self._makePost(topic=topic2, body="Post 2")
        results = topic1.single_post(2)
        self.assertListEqual(results, [post3])
        self.assertListEqual(results, topic1.scoped_posts("2"))
        self.assertListEqual(topic1.single_post(1000), [])
        self.assertListEqual(topic3.single_post(1), [])
        self.assertListEqual(topic3.single_post(), [])

    def test_ranged_posts(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        topic3 = self._makeTopic(board=board, title="Empty topic")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        post3 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 4")
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 1")
        post6 = self._makePost(topic=topic2, body="Topic 2, Post 2")
        post7 = self._makePost(topic=topic1, body="Topic 1, Post 5")
        results = topic1.ranged_posts(2, 5)
        self.assertListEqual(results, [post2, post3, post4, post7])
        self.assertListEqual(results, topic1.scoped_posts("2-5"))
        self.assertListEqual(topic1.ranged_posts(1000, 1005), [])
        self.assertListEqual(topic3.ranged_posts(1, 5), [])
        self.assertListEqual(topic1.ranged_posts(), topic1.posts.all())

    def test_ranged_posts_without_end(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        topic3 = self._makeTopic(board=board, title="Empty topic")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        post3 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 4")
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 1")
        post6 = self._makePost(topic=topic2, body="Topic 2, Post 2")
        post7 = self._makePost(topic=topic1, body="Topic 1, Post 5")
        results = topic1.ranged_posts(3)
        self.assertListEqual(results, [post3, post4, post7])
        self.assertListEqual(results, topic1.scoped_posts("3-"))
        self.assertListEqual(topic1.ranged_posts(1000), [])
        self.assertListEqual(topic3.ranged_posts(3), [])

    def test_range_query_without_start(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        topic3 = self._makeTopic(board=board, title="Empty topic")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        post3 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 4")
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 1")
        post6 = self._makePost(topic=topic2, body="Topic 2, Post 2")
        post7 = self._makePost(topic=topic1, body="Topic 1, Post 5")
        results = topic1.ranged_posts(None, 3)
        self.assertListEqual(results, [post1, post2, post3])
        self.assertListEqual(results, topic1.scoped_posts("-3"))
        self.assertListEqual(topic1.ranged_posts(None, 0), [])
        self.assertListEqual(topic3.ranged_posts(None, 3), [])

    def test_recent_query(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        topic3 = self._makeTopic(board=board, title="Empty topic")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        [self._makePost(topic=topic2, body="Foobar") for i in range(5)]
        post3 = self._makePost(topic=topic2, body="Topic 2, Post 6")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        [self._makePost(topic=topic2, body="Foobar") for i in range(24)]
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 31")
        [self._makePost(topic=topic2, body="Foobar") for i in range(3)]
        post6 = self._makePost(topic=topic2, body="Topic 2, Post 35")

        default_results = topic2.recent_posts()
        self.assertEqual(default_results[0], post3)
        self.assertEqual(default_results[-1], post6)
        self.assertListEqual(default_results, topic2.scoped_posts("recent"))

        numbered_results = topic2.recent_posts(5)
        self.assertEqual(numbered_results[0], post5)
        self.assertEqual(numbered_results[-1], post6)
        self.assertListEqual(numbered_results, topic2.scoped_posts("l5"))

        self.assertListEqual(topic2.recent_posts(0), [])
        self.assertListEqual(topic3.recent_posts(), [])

    def test_recent_query_missing(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic = self._makeTopic(board=board, title="Hello, world!")
        post1 = self._makePost(topic=topic, body="Post 1")
        post2 = self._makePost(topic=topic, body="Post 2")
        post3 = self._makePost(topic=topic, body="Post 3")
        post4 = self._makePost(topic=topic, body="Post 4")
        post5 = self._makePost(topic=topic, body="Post 5")
        post6 = self._makePost(topic=topic, body="Post 6")
        self.assertListEqual(
            [post2, post3, post4, post5, post6],
            topic.scoped_posts("l5"))

        DBSession.delete(post3)
        DBSession.flush()
        self.assertListEqual(
            [post1, post2, post4, post5, post6],
            topic.scoped_posts("l5"))


class PostModelTest(ModelMixin, unittest.TestCase):

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
        import os
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
            'csrf_token': ['CSRF token missing.'],
        })

    def test_csrf_token_invalid(self):
        request = self._makeRequest()
        form = self._makeOne({'csrf_token': 'invalid'}, request)
        self.assertDictEqual(form.errors, {
            'csrf_token': ['CSRF token mismatched.'],
        })

    def test_data(self):
        request = self._makeRequest()
        form = self._makeOne({'csrf_token': 'strip_me'}, request)
        self.assertDictEqual(form.data, {})


class DummyTranslations(object):
    def gettext(self, string):
        return string

    def ngettext(self, singular, plural, n):
        if n == 1:
            return singular
        return plural


class DummyForm(dict):
    pass


class DummyField(object):
    _translations = DummyTranslations()

    def __init__(self, data, errors=(), raw_data=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data

    def gettext(self, string):
        return self._translations.gettext(string)

    def ngettext(self, singular, plural, n):
        return self._translations.ngettext(singular, plural, n)


class TestForm(unittest.TestCase):

    def _grab_error(self, callable, form, field):
        from fanboi2.forms import ValidationError
        try:
            callable(form, field)
        except ValidationError as e:
            return e.args[0]

    def test_length_validator(self):
        from fanboi2.forms import Length, ValidationError
        form = DummyForm()
        field = DummyField('foobar')

        self.assertEqual(Length(min=2, max=6)(form, field), None)
        self.assertEqual(Length(min=6)(form, field), None)
        self.assertEqual(Length(max=6)(form, field), None)
        self.assertRaises(ValidationError, Length(min=7), form, field)
        self.assertRaises(ValidationError, Length(max=5), form, field)
        self.assertRaises(ValidationError, Length(7, 10), form, field)
        self.assertRaises(AssertionError, Length)
        self.assertRaises(AssertionError, Length, min=5, max=2)

        grab = lambda **k: self._grab_error(Length(**k), form, field)
        self.assertIn('at least 8 characters', grab(min=8))
        self.assertIn('longer than 1 character', grab(max=1))
        self.assertIn('longer than 5 characters', grab(max=5))
        self.assertIn('between 2 and 5 characters', grab(min=2, max=5))
        self.assertIn(
            'at least 1 character',
            self._grab_error(Length(min=1), form, DummyField('')))

    def test_length_validator_newline(self):
        from fanboi2.forms import Length
        form = DummyForm()
        self.assertEqual(Length(max=1)(form, DummyField('\r\n')), None)
        self.assertEqual(Length(max=1)(form, DummyField('\n')), None)
        self.assertEqual(Length(max=1)(form, DummyField('\r')), None)


class TestFormatters(unittest.TestCase):

    def _makeRegistry(self):
        from pyramid.registry import Registry
        registry = Registry()
        registry.settings = {'app.timezone': 'Asia/Bangkok'}
        return registry

    def test_url_fix(self):
        from fanboi2.formatters import url_fix
        tests = [
            ('http://example.com/',
             'http://example.com/'),
            ('https://example.com:443/foo/bar',
             'https://example.com:443/foo/bar'),
            ('http://example.com/lots of space',
             'http://example.com/lots%20of%20space'),
            ('http://example.com/search?q=hello world',
             'http://example.com/search?q=hello+world'),
            ('http://example.com/ほげ',
             'http://example.com/%E3%81%BB%E3%81%92'),
            ('http://example.com/"><script></script>',
             'http://example.com/%22%3E%3Cscript%3E%3C/script%3E'),
        ]
        for source, target in tests:
            self.assertEqual(url_fix(source), target)

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
            ('//i.imgur.com/image1s.jpg', '//imgur.com/image1'),
            ('//i.imgur.com/image2s.jpg', '//imgur.com/image2'),
            ('//i.imgur.com/image3s.jpg', '//imgur.com/image3'),
            ('//i.imgur.com/image4s.jpg', '//imgur.com/image4'),
            ('//i.imgur.com/image5s.jpg', '//imgur.com/image5'),
            ('//i.imgur.com/image7s.jpg', '//imgur.com/image7'),
        ))

    def test_post_markup(self):
        from fanboi2.formatters import PostMarkup
        from jinja2 import Markup
        markup = PostMarkup('<p>foo</p>')
        markup.shortened = True
        markup.length = 3
        self.assertEqual(markup, Markup('<p>foo</p>'))
        self.assertEqual(markup.shortened, True)
        self.assertEqual(len(PostMarkup('<p>Hello</p>')), 12)
        self.assertEqual(len(markup), 3)

    def test_format_text(self):
        from fanboi2.formatters import format_text
        from jinja2 import Markup
        tests = [
            ('Hello, world!', '<p>Hello, world!</p>'),
            ('H\n\n\nello\nworld', '<p>H</p>\n<p>ello<br>world</p>'),
            ('Foo\r\n\r\n\r\n\nBar', '<p>Foo</p>\n<p>Bar</p>'),
            ('Newline at the end\n', '<p>Newline at the end</p>'),
            ('STRIP ME!!!1\n\n', '<p>STRIP ME!!!1</p>'),
            ('ほげ\n\nほげ', '<p>ほげ</p>\n<p>ほげ</p>'),
            ('Foo\n \n Bar', '<p>Foo</p>\n<p>Bar</p>'),
            ('ไก่จิกเด็ก\n\nตายบนปากโอ่ง',
             '<p>ไก่จิกเด็ก</p>\n<p>ตายบนปากโอ่ง</p>'),
            ('<script></script>', '<p>&lt;script&gt;&lt;/script&gt;</p>'),
        ]
        for source, target in tests:
            self.assertEqual(format_text(source), Markup(target))

    def test_format_text_autolink(self):
        from fanboi2.formatters import format_text
        from jinja2 import Markup
        text = ('Hello from autolink:\n\n'
                'Boom: http://example.com/"<script>alert("Hi")</script><a\n'
                'http://www.example.com/ほげ\n'
                'http://www.example.com/%E3%81%BB%E3%81%92\n'
                'https://www.example.com/test foobar')
        self.assertEqual(
            format_text(text),
            Markup('<p>Hello from autolink:</p>\n'
                   '<p>Boom: <a href="http://example.com/%22%3Cscript'
                        '%3Ealert%28%22Hi%22%29%3C/script%3E%3Ca" '
                        'class="link" target="_blank" rel="nofollow">'
                        'http://example.com/&quot;&lt;script&gt;alert(&quot;'
                        'Hi&quot;)&lt;/script&gt;&lt;a</a><br>'
                      '<a href="http://www.example.com/%E3%81%BB%E3%81%92" '
                        'class="link" target="_blank" rel="nofollow">'
                        'http://www.example.com/ほげ</a><br>'
                      '<a href="http://www.example.com/%E3%81%BB%E3%81%92" '
                        'class="link" target="_blank" rel="nofollow">'
                        'http://www.example.com/ほげ</a><br>'
                      '<a href="https://www.example.com/test" '
                        'class="link" target="_blank" rel="nofollow">'
                        'https://www.example.com/test</a> foobar</p>'))

    def test_format_text_shorten(self):
        from fanboi2.formatters import format_text
        from fanboi2.formatters import PostMarkup
        from jinja2 import Markup
        tests = (
            ('Hello, world!', '<p>Hello, world!</p>', 13, False),
            ('Hello\nworld!', '<p>Hello</p>', 5, True),
            ('Hello, world!\nFoobar', '<p>Hello, world!</p>', 13, True),
            ('Hello', '<p>Hello</p>', 5, False),
        )
        for source, target, length, shortened in tests:
            result = format_text(source, shorten=5)
            self.assertIsInstance(result, PostMarkup)
            self.assertEqual(result, Markup(target))
            self.assertEqual(result.length, length)
            self.assertEqual(result.shortened, shortened)

    def test_format_text_thumbnail(self):
        from fanboi2.formatters import format_text
        from jinja2 import Markup
        text = ("New product! https://imgur.com/foobar1\n\n"
                "http://i.imgur.com/foobar2.png\n"
                "http://imgur.com/foobar3.jpg\n"
                "Buy today get TWO for FREE!!1")
        self.assertEqual(
            format_text(text),
            Markup('<p>New product! <a href="https://imgur.com/foobar1" '
                      'class="link" target="_blank" rel="nofollow">'
                      'https://imgur.com/foobar1</a></p>\n'
                   '<p><a href="http://i.imgur.com/foobar2.png" '
                      'class="link" target="_blank" rel="nofollow">'
                      'http://i.imgur.com/foobar2.png</a><br>'
                      '<a href="http://imgur.com/foobar3.jpg" class="link" '
                      'target="_blank" rel="nofollow">'
                      'http://imgur.com/foobar3.jpg</a><br>'
                      'Buy today get TWO for FREE!!1</p>\n'
                   '<p class="thumbnails"><a href="//imgur.com/foobar1" '
                         'class="thumbnail" target="_blank">'
                         '<img src="//i.imgur.com/foobar1s.jpg">'
                         '</a>'
                       '<a href="//imgur.com/foobar2" '
                         'class="thumbnail" target="_blank">'
                         '<img src="//i.imgur.com/foobar2s.jpg">'
                         '</a>'
                       '<a href="//imgur.com/foobar3" '
                         'class="thumbnail" target="_blank">'
                         '<img src="//i.imgur.com/foobar3s.jpg">'
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

    def test_format_markdown_empty(self):
        from fanboi2.formatters import format_markdown
        self.assertIsNone(format_markdown(None))

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

    def test_format_post(self):
        from fanboi2.formatters import format_post
        from jinja2 import Markup
        self.config.add_route('topic_scoped', '/{board}/{topic}/{query}')
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic = self._makeTopic(board=board, title="Hogehogehogehogehoge")
        post1 = self._makePost(topic=topic, body="Hogehoge\nHogehoge")
        post2 = self._makePost(topic=topic, body=">>1")
        post3 = self._makePost(topic=topic, body=">>1-2\nHoge")
        tests = [
            (post1, "<p>Hogehoge<br>Hogehoge</p>"),
            (post2, "<p><a data-number=\"1\" " +
                    "href=\"/foobar/1/1\" class=\"anchor\">" +
                    "&gt;&gt;1</a></p>"),
            (post3, "<p><a data-number=\"1-2\" " +
                    "href=\"/foobar/1/1-2\" class=\"anchor\">" +
                    "&gt;&gt;1-2</a><br>Hoge</p>"),
        ]
        for source, target in tests:
            self.assertEqual(format_post(source), Markup(target))

    def test_format_post_shorten(self):
        from fanboi2.formatters import format_post
        from jinja2 import Markup
        self.config.add_route('topic_scoped', '/{board}/{topic}/{query}')
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic = self._makeTopic(board=board, title="Hogehogehogehogehoge")
        post = self._makePost(topic=topic, body="Hello\nworld")
        self.assertEqual(format_post(post, shorten=5),
                         Markup("<p>Hello</p>\n<p class=\"shortened\">"
                                "Post shortened. <a href=\"/foobar/1/1-\">"
                                "See full post</a>.</p>"))


class TestAkismet(unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.utils import Akismet
        return Akismet

    def _makeRequest(self, api_key='hogehoge'):
        from pyramid.registry import Registry
        request = testing.DummyRequest()
        request.remote_addr = '127.0.0.1'
        request.user_agent = 'Mock 1.0'
        request.referrer = 'http://www.example.com/'
        registry = Registry()
        registry.settings = {'akismet.key': api_key}
        testing.setUp(request=request, registry=registry)
        return request

    def _makeResponse(self, content):
        class MockResponse(object):
            def __init__(self, content):
                self.content = content
        return MockResponse(content)

    def test_init(self):
        request = self._makeRequest()
        akismet = self._getTargetClass()(request)
        self.assertEqual(akismet.request, request)
        self.assertEqual(akismet.key, 'hogehoge')

    def test_init_no_key(self):
        request = self._makeRequest(api_key=None)
        akismet = self._getTargetClass()(request)
        self.assertEqual(akismet.request, request)
        self.assertEqual(akismet.key, None)

    @mock.patch('requests.post')
    def test_spam(self, api_call):
        api_call.return_value = self._makeResponse(b'true')
        request = self._makeRequest()
        akismet = self._getTargetClass()(request)
        self.assertEqual(akismet.spam('buy viagra'), True)
        api_call.assert_called_with(
            'https://hogehoge.rest.akismet.com/1.1/comment-check',
            headers=mock.ANY,
            data=mock.ANY,
        )

    @mock.patch('requests.post')
    def test_spam_ham(self, api_call):
        api_call.return_value = self._makeResponse(b'false')
        request = self._makeRequest()
        akismet = self._getTargetClass()(request)
        self.assertEqual(akismet.spam('Hogehogehogehoge!'), False)
        api_call.assert_called_with(
            'https://hogehoge.rest.akismet.com/1.1/comment-check',
            headers=mock.ANY,
            data=mock.ANY,
        )

    @mock.patch('requests.post')
    def test_spam_no_key(self, api_call):
        request = self._makeRequest(api_key=None)
        akismet = self._getTargetClass()(request)
        self.assertEqual(akismet.spam('buy viagra'), False)
        assert not api_call.called


class TestRateLimiter(unittest.TestCase):

    def setUp(self):
        redis_conn._redis = DummyRedis()

    def tearDown(self):
        redis_conn._redis = None

    def _getTargetClass(self):
        from fanboi2.utils import RateLimiter
        return RateLimiter

    def _getHash(self, text):
        import hashlib
        return hashlib.md5(text.encode('utf8')).hexdigest()

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.remote_addr = '127.0.0.1'
        testing.setUp(request=request)
        return request

    def test_init(self):
        request = self._makeRequest()
        ratelimit = self._getTargetClass()(request, namespace='foobar')
        self.assertEqual(ratelimit.key,
                         "rate:foobar:%s" % self._getHash('127.0.0.1'))

    def test_init_no_namespace(self):
        request = self._makeRequest()
        ratelimit = self._getTargetClass()(request)
        self.assertEqual(ratelimit.key,
                         "rate:None:%s" % self._getHash('127.0.0.1'))

    def test_limit(self):
        request = self._makeRequest()
        ratelimit = self._getTargetClass()(request, namespace='foobar')
        self.assertFalse(ratelimit.limited())
        self.assertEqual(ratelimit.timeleft(), 0)
        ratelimit.limit(seconds=30)
        self.assertTrue(ratelimit.limited())
        self.assertEqual(ratelimit.timeleft(), 30)

    def test_limit_no_seconds(self):
        request = self._makeRequest()
        ratelimit = self._getTargetClass()(request, namespace='foobar')
        ratelimit.limit()
        self.assertTrue(ratelimit.limited())
        self.assertEqual(ratelimit.timeleft(), 10)


class TestBaseView(ViewMixin, ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.views import BaseView
        return BaseView

    def test_init(self):
        board1 = self._makeBoard(title="General", slug="general")
        board2 = self._makeBoard(title="Foobar", slug="foo")
        view = self._getTargetClass()(self.request)
        self.assertEqual(view.request, self.request)
        self.assertEqual(view.board, None)
        self.assertEqual(view.topic, None)
        self.assertListEqual(view.boards, [board2, board1])

    def test_board(self):
        board1 = self._makeBoard(title="General", slug="general")
        board2 = self._makeBoard(title="Foobar", slug="foo")
        request = self._GET()
        request.matchdict['board'] = 'foo'
        view = self._getTargetClass()(request)
        self.assertEqual(view.board, board2)

    def test_board_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = self._GET()
        request.matchdict['board'] = 'foo'
        view = self._getTargetClass()(request)
        with self.assertRaises(HTTPNotFound):
            assert not view.board

    def test_topic(self):
        board = self._makeBoard(title="General", slug="general")
        topic1 = self._makeTopic(board=board, title="Foobar")
        topic2 = self._makeTopic(board=board, title="Hello")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic2.id)
        view = self._getTargetClass()(request)
        self.assertEqual(view.board, board)
        self.assertEqual(view.topic, topic2)

    def test_topic_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        board = self._makeBoard(title="General", slug="general")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = '2943'
        view = self._getTargetClass()(request)
        with self.assertRaises(HTTPNotFound):
            assert not view.topic

    def test_topic_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        board1 = self._makeBoard(title="General", slug="general")
        board2 = self._makeBoard(title="Foobar", slug="foo")
        topic1 = self._makeTopic(board=board1, title="Foobar")
        topic2 = self._makeTopic(board=board2, title="Hello")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic2.id)
        view = self._getTargetClass()(request)
        with self.assertRaises(HTTPNotFound):
            assert not view.topic

    def test_topic_no_board(self):
        request = self._GET()
        request.matchdict['topic'] = '2943'
        view = self._getTargetClass()(request)
        self.assertEqual(view.board, None)
        self.assertEqual(view.topic, None)

    def test_call_unimplemented(self):
        request = self._GET()
        view = self._getTargetClass()(request)
        with self.assertRaises(NotImplementedError):
            assert not view()


class TestRootView(ViewMixin, ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.views import RootView
        return RootView

    def test_get(self):
        board1 = self._makeBoard(title="General", slug="general")
        board2 = self._makeBoard(title="Foobar", slug="foo")
        request = self._GET()
        response = self._getTargetClass()(request)()
        self.assertListEqual(response["boards"], [board2, board1])


class TestBoardView(ViewMixin, ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.views import BoardView
        return BoardView

    def test_get(self):
        def _make_topic(days=0, **kwargs):
            from datetime import datetime, timedelta
            topic = self._makeTopic(**kwargs)
            self._makePost(
                topic=topic,
                body="Hello",
                created_at=datetime.now() - timedelta(days=days))
            return topic

        board = self._makeBoard(title="General", slug="general")
        topic1 = _make_topic(0, board=board, title="Foo1")
        topic2 = _make_topic(1, board=board, title="Foo2")
        topic3 = _make_topic(2, board=board, title="Foo3")
        topic4 = _make_topic(3, board=board, title="Foo4")
        topic5 = _make_topic(4, board=board, title="Foo5", status="locked")
        topic6 = _make_topic(5, board=board, title="Foo6", status="archived")
        topic7 = _make_topic(6, board=board, title="Foo7")
        topic8 = _make_topic(7, board=board, title="Foo8")
        topic9 = _make_topic(8, board=board, title="Foo9")
        topic10 = _make_topic(9, board=board, title="Foo10")
        topic11 = _make_topic(10, board=board, title="Foo11")
        request = self._GET()
        request.matchdict['board'] = 'general'
        response = self._getTargetClass()(request)()
        self.assertEqual(response["board"], board)
        self.assertListEqual(response["boards"], [board])
        self.assertListEqual(
            response["topics"], [
                topic1,
                topic2,
                topic3,
                topic4,
                topic5,
                topic6,
                topic7,
                topic8,
                topic9,
                topic10,
            ]
        )

    def test_get_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = self._GET()
        request.matchdict['board'] = 'general'
        with self.assertRaises(HTTPNotFound):
            assert not self._getTargetClass()(request)()


class TestBoardAllView(ViewMixin, ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.views import BoardAllView
        return BoardAllView

    def test_get(self):
        def _make_topic(days=0, **kwargs):
            from datetime import datetime, timedelta
            topic = self._makeTopic(**kwargs)
            self._makePost(
                topic=topic,
                body="Hello",
                created_at=datetime.now() - timedelta(days=days))
            return topic

        board = self._makeBoard(title="General", slug="general")
        topic1 = _make_topic(0, board=board, title="Foo1")
        topic2 = _make_topic(5, board=board, title="Foo2", status="locked")
        topic3 = _make_topic(6, board=board, title="Foo3", status="archived")
        topic4 = _make_topic(7, board=board, title="Foo4", status="locked")
        topic5 = _make_topic(8, board=board, title="Foo5", status="archived")
        request = self._GET()
        request.matchdict['board'] = 'general'
        response = self._getTargetClass()(request)()
        self.assertEqual(response["board"], board)
        self.assertListEqual(response["boards"], [board])
        self.assertListEqual(
            response["topics"], [
                topic1,
                topic2,
                topic3,
            ]
        )

    def test_get_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = self._GET()
        request.matchdict['board'] = 'general'
        with self.assertRaises(HTTPNotFound):
            assert not self._getTargetClass()(request)()


class TestBoardNewView(ViewMixin, ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.views import BoardNewView
        return BoardNewView

    def test_get(self):
        board = self._makeBoard(title="General", slug="general")
        request = self._GET()
        request.matchdict['board'] = 'general'
        response = self._getTargetClass()(request)()
        self.assertListEqual(response["boards"], [board])
        self.assertDictEqual(response["form"].errors, {})
        self.assertEqual(response["board"], board)

    def test_get_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = self._GET()
        request.matchdict['board'] = 'general'
        with self.assertRaises(HTTPNotFound):
            assert not self._getTargetClass()(request)()

    @mock.patch('fanboi2.utils.RateLimiter.limit')
    def test_post(self, limit_call):
        from fanboi2.models import DBSession, Topic
        board = self._makeBoard(title="General", slug="general")
        request = self._make_csrf(self._POST({
            'title': "One more thing...",
            'body': "And now for something completely different...",
        }))
        request.matchdict['board'] = 'general'
        self.config.add_route('board', '/{board}/')
        response = self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Topic).count(), 1)
        self.assertEqual(response.location, "/general/")
        limit_call.assert_called_with(board.settings['post_delay'])

    def test_post_failure(self):
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title="General", slug="general")
        request = self._make_csrf(self._POST({
            'title': "One more thing...",
            'body': "",
        }))
        request.matchdict['board'] = 'general'
        response = self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Topic).count(), 0)
        self.assertEqual(response["form"].title.data, 'One more thing...')
        self.assertDictEqual(response["form"].errors, {
            'body': ['This field is required.']
        })

    @mock.patch('fanboi2.utils.Akismet.spam')
    def test_post_spam(self, spam_call):
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title="General", slug="general")
        request = self._make_csrf(self._POST({
            'title': "Buy viagra",
            'body': "Buy today at http://viagra.example.com/",
        }))
        request.matchdict['board'] = 'general'
        spam_call.return_value = True
        self.config.testing_add_renderer('boards/error_spam.jinja2')
        self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Topic).count(), 0)
        self.assertTrue(spam_call.called)

    @mock.patch('fanboi2.utils.Akismet.spam')
    def test_post_ham(self, spam_call):
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title="General", slug="general")
        request = self._make_csrf(self._POST({
            'title': "Buy viagra",
            'body': "Not really! Just joking!",
        }))
        request.matchdict['board'] = 'general'
        spam_call.return_value = False
        self.config.add_route('board', '/{board}/')
        self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Topic).count(), 1)
        self.assertTrue(spam_call.called)

    @mock.patch('fanboi2.utils.RateLimiter.limited')
    @mock.patch('fanboi2.utils.RateLimiter.timeleft')
    def test_post_limited(self, timeleft_call, limited_call):
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title="General", slug="general")
        request = self._make_csrf(self._POST({
            'title': "Flooding the board!!1",
            'body': "LOLUSUX!!11",
        }))
        request.matchdict['board'] = 'general'
        limited_call.return_value = True
        timeleft_call.return_value = 10
        self.config.testing_add_renderer('boards/error_rate.jinja2')
        self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Topic).count(), 0)
        self.assertTrue(limited_call.called)
        self.assertTrue(timeleft_call.called)


class TestTopicView(ViewMixin, ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.views import TopicView
        return TopicView

    def test_get(self):
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        post1 = self._makePost(topic=topic, body="Hello, world!")
        post2 = self._makePost(topic=topic, body="Boring post is boring!")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        response = self._getTargetClass()(request)()
        self.assertListEqual(response["boards"], [board])
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)
        self.assertDictEqual(response["form"].errors, {})
        self.assertListEqual(response["posts"], [post1, post2])

    def test_get_scoped(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Hello, world!")
        post1 = self._makePost(topic=topic, body="Boring test is boring!")
        post2 = self._makePost(topic=topic, body="Boring post is boring!")
        request = self._GET()
        request.matchdict['board'] = 'foo'
        request.matchdict['topic'] = str(topic.id)
        request.matchdict['query'] = '2'
        response = self._getTargetClass()(request)()
        self.assertListEqual(response["boards"], [board])
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)
        self.assertDictEqual(response["form"].errors, {})
        self.assertListEqual(response["posts"], [post2])

    def test_get_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        board = self._makeBoard(title="General", slug="general")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = '2943'
        with self.assertRaises(HTTPNotFound):
            assert not self._getTargetClass()(request)()

    def test_get_empty_posts(self):
        from pyramid.httpexceptions import HTTPNotFound
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Hello, world!")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        with self.assertRaises(HTTPNotFound):
            assert not self._getTargetClass()(request)()

    @mock.patch('fanboi2.utils.RateLimiter.limit')
    def test_post(self, limit_call):
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        settings = board.settings
        request = self._make_csrf(self._POST({'body': "Boring post..."}))
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        self.config.add_route('topic_scoped', '/{board}/{topic}/{query}')
        response = self._getTargetClass()(request)()
        self.assertEqual(response.location, "/general/%s/l5" % topic.id)
        self.assertEqual(DBSession.query(Post).count(), 1)
        self.assertEqual(DBSession.query(Post).first().name, settings['name'])
        limit_call.assert_called_with(settings['post_delay'])

    def test_post_failure(self):
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        request = self._make_csrf(self._POST({'body': 'x'}))
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        response = self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Post).count(), 0)
        self.assertEqual(response["form"].body.data, 'x')
        self.assertDictEqual(response["form"].errors, {
            'body': ['Field must be between 2 and 4000 characters long.'],
        })

    @mock.patch('fanboi2.utils.Akismet.spam')
    def test_post_spam(self, spam_call):
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        request = self._make_csrf(self._POST({'body': 'Buy viagra'}))
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        spam_call.return_value = True
        self.config.testing_add_renderer('topics/error_spam.jinja2')
        self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Post).count(), 0)
        self.assertTrue(spam_call.called)

    @mock.patch('fanboi2.utils.Akismet.spam')
    def test_post_ham(self, spam_call):
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        request = self._make_csrf(self._POST({'body': 'Yahoo!'}))
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        spam_call.return_value = False
        self.config.add_route('topic_scoped', '/{board}/{topic}/{query}')
        self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Post).count(), 1)
        self.assertTrue(spam_call.called)

    @mock.patch('fanboi2.utils.RateLimiter.limited')
    @mock.patch('fanboi2.utils.RateLimiter.timeleft')
    def test_post_limited(self, timeleft_call, limited_call):
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Spam spam spam")
        request = self._make_csrf(self._POST({'body': 'Blah, blah, blah!'}))
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        limited_call.return_value = True
        timeleft_call.return_value = 10
        self.config.testing_add_renderer('topics/error_rate.jinja2')
        self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Post).count(), 0)
        self.assertTrue(limited_call.called)
        self.assertTrue(timeleft_call.called)

    def test_post_repeatable(self):
        from fanboi2.models import DBSession, Post
        from sqlalchemy.exc import IntegrityError
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        request = self._make_csrf(self._POST({'body': 'Yahoo!'}))
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        with mock.patch('sqlalchemy.orm.scoping.scoped_session.flush') as m:
            m.side_effect = IntegrityError(None, None, None)
            with self.assertRaises(IntegrityError):
                assert not self._getTargetClass()(request)()
            self.assertEqual(m.call_count, 5)
        self.assertEqual(DBSession.query(Post).count(), 0)

    def test_post_archived(self):
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title="Foo", slug="foo")
        topic = self._makeTopic(board=board, title="Hoge", status='archived')
        self.assertEqual(DBSession.query(Post).count(), 0)
        request = self._make_csrf(self._POST({
            'body': "Topic is archived and post shouldn't get through."
        }))
        request.matchdict['board'] = 'foo'
        request.matchdict['topic'] = str(topic.id)
        self.config.testing_add_renderer('topics/error.jinja2')
        self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Post).count(), 0)

    def test_post_locked(self):
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title="Foo", slug="foo")
        topic = self._makeTopic(board=board, title="Hoge", status='locked')
        self.assertEqual(DBSession.query(Post).count(), 0)
        request = self._make_csrf(self._POST({
            'body': "Topic is locked and post shouldn't get through."
        }))
        request.matchdict['board'] = 'foo'
        request.matchdict['topic'] = str(topic.id)
        self.config.testing_add_renderer('topics/error.jinja2')
        self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Post).count(), 0)


class CacheMixin(object):

    def _getRegion(self, store=None):
        from dogpile.cache import make_region
        return make_region().configure('dogpile.cache.memory', arguments={
            'cache_dict': store if store is not None else {},
        })


class TestCache(CacheMixin, unittest.TestCase):

    def test_key_mangler(self):
        from fanboi2.cache import _key_mangler
        store = {}
        region = self._getRegion(store)
        region.key_mangler = _key_mangler
        region.set("Foobar", 1)
        self.assertIn("89d5739baabbbe65be35cbe61c88e06d", store)


class TestJinja2CacheExtension(CacheMixin, unittest.TestCase):

    def _getJinja2(self, region):
        from jinja2 import Environment
        from fanboi2.cache import Jinja2CacheExtension
        env = Environment(extensions=[Jinja2CacheExtension])
        env.cache_region = region
        return env

    def test_cache(self):
        store = {}
        region = self._getRegion(store)
        jinja2 = self._getJinja2(region)
        jinja2.from_string('{% cache "a", "b" %}Baz{% endcache %}').render()
        self.assertIn('jinja2:None:a:b', store)
        self.assertEqual(region.get('jinja2:None:a:b'), 'Baz')

    def test_cache_not_setup(self):
        store = {}
        region = self._getRegion(store)
        jinja2 = self._getJinja2(None)
        jinja2.from_string('{% cache "a", "b" %}Baz{% endcache %}').render()
        self.assertEqual({}, store)
