import unittest
from fanboi2.models import DBSession
from fanboi2.tests import DummyRedis, DATABASE_URI, ModelMixin
from sqlalchemy.ext.declarative import declarative_base


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
        topic1 = Topic(board=board, title="First")
        topic2 = Topic(board=board, title="Second")
        topic3 = Topic(board=board, title="Third")
        topic4 = Topic(board=board, title="Fourth")
        topic5 = Topic(
            board=board,
            title="Fifth",
            created_at=datetime.now() + timedelta(seconds=10))
        DBSession.add(topic1)
        DBSession.add(topic2)
        DBSession.add(topic3)
        DBSession.flush()
        DBSession.add(Post(topic=topic1, ip_address="1.1.1.1", body="!!1"))
        DBSession.add(Post(topic=topic4, ip_address="1.1.1.1", body="Baz"))
        mappings = ((topic3, 3, True), (topic2, 5, True), (topic4, 8, False))
        for obj, offset, bump in mappings:
            DBSession.add(Post(
                topic=obj,
                ip_address="1.1.1.1",
                body="Foo",
                created_at=datetime.now() + timedelta(seconds=offset),
                bumped=bump))
        DBSession.add(Post(
            topic=topic5,
            ip_address="1.1.1.1",
            body="Hax",
            bumped=False))
        DBSession.flush()
        DBSession.refresh(board)
        self.assertEqual([topic5, topic2, topic3, topic1, topic4],
                         list(board.topics))


class TopicModelTest(ModelMixin, unittest.TestCase):

    def test_relations(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertEqual(topic.board, board)
        self.assertEqual([], list(topic.posts))
        self.assertEqual([topic], list(board.topics))

    def test_posts(self):
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
