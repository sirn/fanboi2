import unittest
import unittest.mock

from sqlalchemy.orm.exc import NoResultFound

from . import ModelSessionMixin


class TestBoardQueryService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import BoardQueryService
        return BoardQueryService

    def test_list_active(self):
        from ..models import Board
        board1 = self._make(Board(slug='foo', title='Foo', status='open'))
        board2 = self._make(Board(
            slug='baz',
            title='Baz',
            status='restricted'))
        board3 = self._make(Board(slug='bax', title='Bax', status='locked'))
        board4 = self._make(Board(slug='wel', title='Wel', status='open'))
        self._make(Board(slug='bar', title='Bar', status='archived'))
        self.dbsession.commit()
        board_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            board_query_svc.list_active(),
            [board3, board2, board1, board4])

    def test_list_active_no_active(self):
        board_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            board_query_svc.list_active(),
            [])

    def test_board_from_slug(self):
        from ..models import Board
        board = self._make(Board(slug='foo', title='Foo'))
        self.dbsession.commit()
        board_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            board_query_svc.board_from_slug('foo'),
            board)

    def test_board_from_slug_not_found(self):
        board_query_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            board_query_svc.board_from_slug('not_found')


class TestFilterService(unittest.TestCase):

    def setUp(self):
        super(TestFilterService, self).setUp()

    def _get_target_class(self):
        from ..services import FilterService
        return FilterService

    def _make_one(self, filters, services={}):
        def _dummy_query_fn(iface=None, name=None):
            for l in (iface, name):
                if l in services:
                    return services[l]

        return self._get_target_class()(
            filters,
            _dummy_query_fn)

    def tearDown(self):
        super(TestFilterService, self).tearDown()

    def test_init(self):
        filter_svc = self._make_one(tuple(), {'cache': 'test'})
        self.assertEqual(filter_svc.filters, tuple())
        self.assertEqual(filter_svc.service_query_fn('cache'), 'test')

    def test_evaluate(self):
        from . import make_cache_region
        from ..interfaces import ISettingQueryService
        _settings = None
        _services = None
        _payload = None

        class _DummyFilter(object):
            __default_settings__ = 'default'
            __use_services__ = ('cache',)

            def __init__(self, settings=None, services={}):
                nonlocal _settings, _services
                self.settings = _settings = settings
                self.services = _services = services

            def should_reject(self, payload):
                nonlocal _payload
                _payload = payload
                return True

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {'ext.filters.dummy': 'overridden'}.get(key, None)

        cache_region = make_cache_region({})
        filter_svc = self._make_one((('dummy', _DummyFilter),), {
            'cache': cache_region,
            ISettingQueryService: _DummySettingQueryService()})

        results = filter_svc.evaluate({'foo': 'bar'})
        self.assertEqual(results.filters, ['dummy'])
        self.assertEqual(results.rejected_by, 'dummy')
        self.assertEqual(_settings, 'overridden')
        self.assertEqual(_services, {'cache': cache_region})
        self.assertEqual(_payload, {'foo': 'bar'})

    def test_evaluate_recently_seen(self):
        from ..interfaces import IPostQueryService
        called_ = False

        class _DummyFilter(object):  # pragma: no cover
            __default_settings__ = 'default'

            def __init__(self, **kwargs):
                pass

            def should_reject(self, payload):
                nonlocal called_
                called_ = True
                return True

        class _DummyPostQueryService(object):
            def was_recently_seen(self, ip_address):
                return True

        filter_svc = self._make_one((('dummy', _DummyFilter),), {
            IPostQueryService: _DummyPostQueryService()})

        results = filter_svc.evaluate({'ip_address': '127.0.0.1'})
        self.assertEqual(results.filters, [])
        self.assertEqual(results.rejected_by, None)
        self.assertFalse(called_)

    def test_evaluate_default_settings(self):
        from . import make_cache_region
        from ..interfaces import ISettingQueryService
        _settings = None

        class _DummyFilter(object):
            __default_settings__ = 'default'

            def __init__(self, settings=None, services={}):
                nonlocal _settings
                self.settings = _settings = settings
                self.services = services

            def should_reject(self, payload):
                return True

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {}.get(key, None)

        cache_region = make_cache_region({})
        filter_svc = self._make_one((('dummy', _DummyFilter),), {
            'cache': cache_region,
            ISettingQueryService: _DummySettingQueryService()})

        filter_svc.evaluate({'foo': 'bar'})
        self.assertEqual(_settings, 'default')

    def test_evaluate_fallback(self):
        from . import make_cache_region
        from ..interfaces import ISettingQueryService

        class _DummyFilterFalse(object):
            def __init__(self, settings=None, services={}):
                self.settings = settings
                self.services = services

            def should_reject(self, payload):
                return False

        class _DummyFilterTrue(_DummyFilterFalse):
            def should_reject(self, payload):
                return True

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {}.get(key, None)

        cache_region = make_cache_region({})
        filter_svc = self._make_one(
            (('dummy1', _DummyFilterFalse), ('dummy2', _DummyFilterTrue)), {
                'cache': cache_region,
                ISettingQueryService: _DummySettingQueryService()})

        results = filter_svc.evaluate({'foo': 'bar'})
        self.assertEqual(results.filters, ['dummy1', 'dummy2'])
        self.assertEqual(results.rejected_by, 'dummy2')

    def test_evaluate_false(self):
        from . import make_cache_region
        from ..interfaces import ISettingQueryService

        class _DummyFilterFalse(object):
            def __init__(self, settings=None, services={}):
                self.settings = settings
                self.services = services

            def should_reject(self, payload):
                return False

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {}.get(key, None)

        cache_region = make_cache_region({})
        filter_svc = self._make_one(
            (('dummy1', _DummyFilterFalse), ('dummy2', _DummyFilterFalse)), {
                'cache': cache_region,
                ISettingQueryService: _DummySettingQueryService()})

        results = filter_svc.evaluate({'foo': 'bar'})
        self.assertEqual(results.filters, ['dummy1', 'dummy2'])
        self.assertIsNone(results.rejected_by)


class TestIdentityService(unittest.TestCase):

    def _get_target_class(self):
        from ..services import IdentityService
        return IdentityService

    def test_init(self):
        from . import DummyRedis
        redis_conn = DummyRedis()
        identity_svc = self._get_target_class()(redis_conn, 10)
        self.assertEqual(identity_svc.redis_conn, redis_conn)
        self.assertEqual(identity_svc.ident_size, 10)

    def test_identity_for(self):
        from . import DummyRedis
        redis_conn = DummyRedis()
        identity_svc = self._get_target_class()(redis_conn, 10)
        ident1 = identity_svc.identity_for(a='1', b='2')
        ident2 = identity_svc.identity_for(b='2', a='1')
        ident3 = identity_svc.identity_for(a='1', b='2', c='3')
        self.assertEqual(ident1, ident2)
        self.assertNotEqual(ident1, ident3)
        self.assertEqual(len(ident1), 10)
        self.assertEqual(len(ident3), 10)
        for k, v in redis_conn._expire.items():
            self.assertEqual(v, 86400)
        redis_conn._reset()
        ident4 = identity_svc.identity_for(a='1', b='2')
        self.assertNotEqual(ident1, ident4)

    def test_identity_for_length(self):
        from . import DummyRedis
        redis_conn = DummyRedis()
        identity_svc = self._get_target_class()(redis_conn, 5)
        self.assertEqual(len(identity_svc.identity_for(a='1', b='2')), 5)


class TestPageQueryService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import PageQueryService
        return PageQueryService

    def test_list_public(self):
        from ..models import Page
        page1 = self._make(Page(
            title='Foo',
            body='Hi',
            slug='test1',
            namespace='public'))
        page2 = self._make(Page(
            title='Bar',
            body='Hi',
            slug='test2',
            formatter='html',
            namespace='public'))
        page3 = self._make(Page(
            title='Baz',
            body='Hi',
            slug='test3',
            formatter='none',
            namespace='public'))
        self._make(Page(
            title='Test',
            body='Hi',
            slug='test4',
            formatter='markdown',
            namespace='internal'))
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            page_query_svc.list_public(),
            [page2, page3, page1])

    def test_public_page_from_slug(self):
        from ..models import Page
        page = self._make(Page(
            title='Test',
            body='Hello',
            slug='test',
            namespace='public'))
        self._make(Page(
            title='Test',
            body='Internal Test',
            slug='test',
            namespace='internal'))
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            page_query_svc.public_page_from_slug('test'),
            page)

    def test_public_page_from_slug_not_found(self):
        page_query_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            page_query_svc.public_page_from_slug('notfound')

    def test_internal_page_from_slug(self):
        from ..models import Page
        self._make(Page(
            title='Test',
            body='Hello',
            slug='test',
            namespace='public'))
        page = self._make(Page(
            title='Test',
            body='Internal Test',
            slug='test',
            namespace='internal'))
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            page_query_svc.internal_page_from_slug('test'),
            page)

    def test_internal_page_from_slug_not_found(self):
        page_query_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            page_query_svc.internal_page_from_slug('notfound')


class TestPostCreateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import PostCreateService
        return PostCreateService

    def _make_one(self):

        class _DummyIdentityService(object):
            def identity_for(self, **kwargs):
                return ','.join(
                    '%s' % (v,) for k, v in sorted(kwargs.items()))

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {'app.time_zone': 'Asia/Bangkok'}.get(key, None)

        return self._get_target_class()(
            self.dbsession,
            _DummyIdentityService(),
            _DummySettingQueryService())

    def test_create(self):
        from datetime import datetime
        from pytz import timezone
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(
            slug='foo',
            title='Foo',
            settings={'name': 'Nameless Foobar'}))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create(
            topic.id,
            'Hello!',
            True,
            '127.0.0.1')
        self.assertEqual(post.number, 1)
        self.assertEqual(post.topic, topic)
        self.assertTrue(post.bumped)
        self.assertEqual(post.name, 'Nameless Foobar')
        self.assertEqual(post.ip_address, '127.0.0.1')
        self.assertEqual(
            post.ident,
            'foo,127.0.0.1,%s' % (
                datetime.now(timezone('Asia/Bangkok')).
                strftime("%Y%m%d"),))
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(topic_meta.post_count, 1)
        self.assertIsNotNone(topic_meta.bumped_at)

    def test_create_without_bumped(self):
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create(
            topic.id,
            'Hello!',
            False,
            '127.0.0.1')
        self.assertFalse(post.bumped)
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertIsNone(topic_meta.bumped_at)

    def test_create_without_ident(self):
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(
            slug='foo',
            title='Foo',
            settings={'use_ident': False}))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create(
            topic.id,
            'Hello!',
            True,
            '127.0.0.1')
        self.assertIsNone(post.ident)

    def test_create_topic_limit(self):
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(
            slug='foo',
            title='Foo',
            settings={'max_posts': 10}))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=9))
        self.dbsession.commit()
        self.assertEqual(topic.status, 'open')
        post_create_svc = self._make_one()
        post = post_create_svc.create(
            topic.id,
            'Hello!',
            True,
            '127.0.0.1')
        topic = self.dbsession.query(Topic).get(topic.id)
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(post.number, 10)
        self.assertEqual(topic_meta.post_count, 10)
        self.assertEqual(topic.status, 'archived')

    def test_create_topic_locked(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(board=board, title='Hello', status='locked'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create(
                topic.id,
                'Hello!',
                True,
                '127.0.0.1')

    def test_create_topic_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(
            board=board,
            title='Hello',
            status='archived'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create(
                topic.id,
                'Hello!',
                True,
                '127.0.0.1')

    def test_create_board_restricted(self):
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(slug='foo', title='Foo', status='restricted'))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create(
            topic.id,
            'Hello!',
            True,
            '127.0.0.1')
        self.assertEqual(post.number, 1)

    def test_create_board_locked(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(slug='foo', title='Foo', status='locked'))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create(
                topic.id,
                'Hello!',
                True,
                '127.0.0.1')

    def test_create_board_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(slug='foo', title='Foo', status='archived'))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create(
                topic.id,
                'Hello!',
                True,
                '127.0.0.1')


class TestPostQueryService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import PostQueryService
        return PostQueryService

    def test_list_from_topic_id(self):
        from ..models import Board, Topic, TopicMeta, Post
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(board=board, title='Foo', status='open'))
        self._make(TopicMeta(topic=topic, post_count=50))
        posts = []
        for i in range(50):
            posts.append(self._make(Post(
                topic=topic,
                number=i + 1,
                name='Nameless Fanboi',
                body='Foobar',
                ip_address='127.0.0.1')))
        topic2 = self._make(Topic(board=board, title='Bar', status='open'))
        self._make(TopicMeta(topic=topic2, post_count=1))
        post2 = self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Fanboi',
            body='Hi',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        post_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id),
            posts)
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic2.id),
            [post2])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, '1'),
            posts[0:1])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, '50'),
            posts[49:50])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, '51'),
            [])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, '1-50'),
            posts)
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, '10-20'),
            posts[9:20])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, '51-99'),
            [])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, '0-51'),
            posts)
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, '-0'),
            [])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, '-5'),
            posts[:5])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, '45-'),
            posts[44:])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, '100-'),
            [])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, 'recent'),
            posts[20:])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, 'l30'),
            posts[20:])

    def test_list_from_topic_id_without_posts(self):
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(board=board, title='Foo', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id),
            [])

    def test_list_from_topic_id_not_found(self):
        post_query_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            post_query_svc.list_from_topic_id(-1)

    def test_was_recently_seen(self):
        from datetime import datetime, timedelta
        from ..models import Board, Topic, TopicMeta, Post
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(board=board, title='Foo', status='open'))
        self._make(TopicMeta(topic=topic, post_count=1))
        self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Fanboi',
            body='Hi',
            ip_address='127.0.0.1',
            created_at=datetime.now() - timedelta(days=2)))
        self.dbsession.commit()
        post_query_svc = self._get_target_class()(self.dbsession)
        self.assertTrue(post_query_svc.was_recently_seen('127.0.0.1'))

    def test_was_recently_seen_not_recent(self):
        from datetime import datetime, timedelta
        from ..models import Board, Topic, TopicMeta, Post
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(board=board, title='Foo', status='open'))
        self._make(TopicMeta(topic=topic, post_count=1))
        self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Fanboi',
            body='Hi',
            ip_address='127.0.0.1',
            created_at=datetime.now() - timedelta(days=4)))
        self.dbsession.commit()
        post_query_svc = self._get_target_class()(self.dbsession)
        self.assertFalse(post_query_svc.was_recently_seen('127.0.0.1'))


class TestRateLimiterService(unittest.TestCase):

    def _get_target_class(self):
        from ..services import RateLimiterService
        return RateLimiterService

    def test_init(self):
        from . import DummyRedis
        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        self.assertEqual(rate_limiter_svc.redis_conn, redis_conn)

    def test_limit_for(self):
        from . import DummyRedis
        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        rate_limiter_svc.limit_for(10, foo='bar', baz='bax')
        self.assertIn(
            'services.rate_limiter:baz=bax,foo=bar',
            redis_conn._store)

    def test_is_limited(self):
        from . import DummyRedis
        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        rate_limiter_svc.limit_for(10, foo='bar')
        self.assertTrue(rate_limiter_svc.is_limited(foo='bar'))

    def test_is_limited_not_limited(self):
        from . import DummyRedis
        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        self.assertFalse(rate_limiter_svc.is_limited(foo='bar'))

    def test_time_left(self):
        from . import DummyRedis
        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        rate_limiter_svc.limit_for(10, foo='bar')
        self.assertEqual(
            rate_limiter_svc.time_left(foo='bar'),
            10)

    def test_time_left_not_limited(self):
        from . import DummyRedis
        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        self.assertEqual(
            rate_limiter_svc.time_left(foo='bar'),
            0)


class TestRuleBanQueryService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import RuleBanQueryService
        return RuleBanQueryService

    def test_is_banned(self):
        from ..models import RuleBan
        self._make(RuleBan(ip_address='10.0.1.0/24'))
        rule_ban_query_svc = self._get_target_class()(self.dbsession)
        self.dbsession.commit()
        self.assertTrue(rule_ban_query_svc.is_banned('10.0.1.1'))
        self.assertTrue(rule_ban_query_svc.is_banned('10.0.1.255'))
        self.assertTrue(rule_ban_query_svc.is_banned(
            '10.0.1.1',
            scopes=['foo:bar']))
        self.assertTrue(rule_ban_query_svc.is_banned(
            '10.0.1.255',
            scopes=['foo:bar']))
        self.assertFalse(rule_ban_query_svc.is_banned('10.0.2.1'))

    def test_is_banned_scoped(self):
        from ..models import RuleBan
        self._make(RuleBan(ip_address='10.0.4.0/24', scope='foo:bar'))
        self.dbsession.commit()
        rule_ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertTrue(rule_ban_query_svc.is_banned(
            '10.0.4.1',
            scopes=['foo:bar']))
        self.assertTrue(rule_ban_query_svc.is_banned(
            '10.0.4.255',
            scopes=['foo:bar']))
        self.assertFalse(rule_ban_query_svc.is_banned('10.0.4.1'))
        self.assertFalse(rule_ban_query_svc.is_banned('10.0.4.255'))
        self.assertFalse(rule_ban_query_svc.is_banned('10.0.5.1'))

    def test_is_banned_inactive(self):
        from ..models import RuleBan
        self._make(RuleBan(ip_address='10.0.6.0/24', active=False))
        self.dbsession.commit()
        rule_ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertFalse(rule_ban_query_svc.is_banned('10.0.6.1'))
        self.assertFalse(rule_ban_query_svc.is_banned('10.0.6.255'))
        self.assertFalse(rule_ban_query_svc.is_banned('10.0.7.1'))

    def test_is_banned_expired(self):
        from datetime import datetime, timedelta
        from ..models import RuleBan
        self._make(RuleBan(
            ip_address='10.0.7.0/24',
            active_until=datetime.now() - timedelta(days=1)))
        self.dbsession.commit()
        rule_ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertFalse(rule_ban_query_svc.is_banned('10.0.7.1'))
        self.assertFalse(rule_ban_query_svc.is_banned('10.0.7.255'))
        self.assertFalse(rule_ban_query_svc.is_banned('10.0.8.1'))


class TestSettingQueryService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import SettingQueryService
        return SettingQueryService

    def test_init(self):
        from . import make_cache_region
        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertEqual(
            setting_query_svc.dbsession,
            self.dbsession)
        self.assertEqual(
            setting_query_svc.cache_region,
            cache_region)

    def test_value_from_key(self):
        from . import make_cache_region
        from ..models import Setting
        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self._make(Setting(key='app.test', value='test'))
        self.dbsession.commit()
        self.assertEqual(
            setting_query_svc.value_from_key('app.test', _default={}),
            'test')

    def test_value_from_key_not_found(self):
        from . import make_cache_region
        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertIsNone(setting_query_svc.value_from_key(
            'app.test',
            _default={}))

    def test_reload(self):
        from . import make_cache_region
        from ..models import Setting
        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self._make(Setting(key='app.test', value='test'))
        self.dbsession.commit()
        self.assertEqual(
            setting_query_svc.value_from_key('app.test', _default={}),
            'test')
        setting = self.dbsession.query(Setting).get('app.test')
        setting.value = 'foobar'
        self.dbsession.add(setting)
        self.dbsession.commit()
        self.assertEqual(
            setting_query_svc.value_from_key('app.test', _default={}),
            'test')
        setting_query_svc.reload('app.test')
        self.assertEqual(
            setting_query_svc.value_from_key('app.test', _default={}),
            'foobar')


class TestSettingUpdateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import SettingUpdateService
        return SettingUpdateService

    def test_update(self):
        from . import make_cache_region
        from ..models import Setting
        from ..services import SettingQueryService
        self._make(Setting(key='app.test', value='test'))
        self.dbsession.commit()
        cache_region = make_cache_region()
        setting_query_svc = SettingQueryService(
            self.dbsession,
            cache_region)
        setting_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertEqual(
            setting_query_svc.value_from_key('app.test'),
            'test')
        setting = setting_update_svc.update('app.test', 'test2')
        self.assertEqual(setting.key, 'app.test')
        self.assertEqual(setting.value, 'test2')
        self.assertEqual(
            setting_query_svc.value_from_key('app.test'),
            'test2')

    def test_update_insert(self):
        from . import make_cache_region
        from ..services import SettingQueryService
        cache_region = make_cache_region()
        setting_query_svc = SettingQueryService(
            self.dbsession,
            cache_region)
        setting_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertIsNone(setting_query_svc.value_from_key('app.test'))
        setting = setting_update_svc.update('app.test', 'test')
        self.assertEqual(setting.key, 'app.test')
        self.assertEqual(setting.value, 'test')
        self.assertEqual(
            setting_query_svc.value_from_key('app.test'),
            'test')

    def test_update_data_structure(self):
        from . import make_cache_region
        cache_region = make_cache_region()
        setting_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        setting = setting_update_svc.update('app.test', {'foo': 'bar'})
        self.assertEqual(setting.key, 'app.test')
        self.assertEqual(setting.value, {'foo': 'bar'})


class TestTaskQueryService(unittest.TestCase):

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_result_from_uid(self, result_):
        from ..services import TaskQueryService
        from . import DummyAsyncResult
        result_.return_value = async_result = DummyAsyncResult(
            'dummy',
            'success',
            'yo')
        task_query_svc = TaskQueryService()
        self.assertEqual(
            task_query_svc.result_from_uid('dummy')._result,
            async_result)


class TestTopicCreateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import TopicCreateService
        return TopicCreateService

    def _make_one(self):
        class _DummyIdentityService(object):
            def identity_for(self, **kwargs):
                return ','.join(
                    '%s' % (v,) for k, v in sorted(kwargs.items()))

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {'app.time_zone': 'Asia/Bangkok'}.get(key, None)

        return self._get_target_class()(
            self.dbsession,
            _DummyIdentityService(),
            _DummySettingQueryService())

    def test_create(self):
        from datetime import datetime
        from pytz import timezone
        from ..models import Board
        board = self._make(Board(
            slug='foo',
            title='Foo',
            settings={'name': 'Nameless Foobar'}))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create(
            board.slug,
            'Hello, world!',
            'Hello Eartians',
            '127.0.0.1')
        self.assertEqual(topic.board, board)
        self.assertEqual(topic.title, 'Hello, world!')
        self.assertEqual(topic.meta.post_count, 1)
        self.assertIsNotNone(topic.meta.bumped_at)
        self.assertEqual(topic.posts[0].number, 1)
        self.assertEqual(topic.posts[0].bumped, True)
        self.assertEqual(topic.posts[0].name, 'Nameless Foobar')
        self.assertEqual(topic.posts[0].ip_address, '127.0.0.1')
        self.assertEqual(
            topic.posts[0].ident,
            'foo,127.0.0.1,%s' % (
                datetime.now(timezone('Asia/Bangkok')).
                strftime("%Y%m%d"),))

    def test_create_without_ident(self):
        from ..models import Board
        board = self._make(Board(
            slug='foo',
            title='Foo',
            settings={'use_ident': False}))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create(
            board.slug,
            'Hello, world!',
            'Hello Eartians',
            '127.0.0.1')
        self.assertIsNone(topic.posts[0].ident)

    def test_create_board_restricted(self):
        from ..errors import StatusRejectedError
        from ..models import Board
        board = self._make(Board(slug='foo', title='Foo', status='restricted'))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            topic_create_svc.create(
                board.slug,
                'Hello, world!',
                'Hello Eartians',
                '127.0.0.1')

    def test_create_board_locked(self):
        from ..errors import StatusRejectedError
        from ..models import Board
        board = self._make(Board(slug='foo', title='Foo', status='locked'))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            topic_create_svc.create(
                board.slug,
                'Hello, world!',
                'Hello Eartians',
                '127.0.0.1')

    def test_create_board_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board
        board = self._make(Board(slug='foo', title='Foo', status='archived'))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            topic_create_svc.create(
                board.slug,
                'Hello, world!',
                'Hello Eartians',
                '127.0.0.1')


class TestTopicQueryService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import TopicQueryService
        return TopicQueryService

    def test_list_from_board_slug(self):
        from ..models import Board, Topic, TopicMeta
        from datetime import datetime, timedelta

        def _make_topic(days=0, **kwargs):
            topic = self._make(Topic(**kwargs))
            self._make(TopicMeta(
                topic=topic,
                post_count=0,
                posted_at=datetime.now(),
                bumped_at=datetime.now() - timedelta(days=days)))
            return topic

        board1 = self._make(Board(title='Foo', slug='foo'))
        board2 = self._make(Board(title='Bar', slug='bar'))
        topic1 = _make_topic(0, board=board1, title='Foo')
        topic2 = _make_topic(1, board=board1, title='Foo')
        topic3 = _make_topic(2, board=board1, title='Foo')
        topic4 = _make_topic(3, board=board1, title='Foo')
        topic5 = _make_topic(4, board=board1, title='Foo')
        topic6 = _make_topic(5, board=board1, title='Foo')
        topic7 = _make_topic(6, board=board1, title='Foo')
        topic8 = _make_topic(6.1, board=board1, title='Foo', status='locked')
        topic9 = _make_topic(6.5, board=board1, title='Foo', status='archived')
        topic10 = _make_topic(7, board=board1, title='Foo')
        topic11 = _make_topic(8, board=board1, title='Foo')
        topic12 = _make_topic(9, board=board1, title='Foo')
        _make_topic(0, board=board2, title='Foo')
        _make_topic(7, board=board1, title='Foo', status='archived')
        _make_topic(7, board=board1, title='Foo', status='locked')
        self.dbsession.commit()
        topic_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            topic_query_svc.list_from_board_slug('foo'),
            [
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
                topic11,
                topic12,
            ])

    def test_list_from_board_slug_not_found(self):
        topic_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            topic_query_svc.list_from_board_slug('notfound'),
            [])

    def test_list_recent_from_board_slug(self):
        from ..models import Board, Topic, TopicMeta
        from datetime import datetime, timedelta

        def _make_topic(days=0, **kwargs):
            topic = self._make(Topic(**kwargs))
            self._make(TopicMeta(
                topic=topic,
                post_count=0,
                posted_at=datetime.now(),
                bumped_at=datetime.now() - timedelta(days=days)))
            return topic

        board1 = self._make(Board(title='Foo', slug='foo'))
        board2 = self._make(Board(title='Bar', slug='bar'))
        topic1 = _make_topic(0, board=board1, title='Foo')
        topic2 = _make_topic(1, board=board1, title='Foo')
        topic3 = _make_topic(2, board=board1, title='Foo')
        topic4 = _make_topic(3, board=board1, title='Foo')
        topic5 = _make_topic(4, board=board1, title='Foo')
        topic6 = _make_topic(5, board=board1, title='Foo')
        topic7 = _make_topic(6, board=board1, title='Foo')
        topic8 = _make_topic(6.1, board=board1, title='Foo', status='locked')
        topic9 = _make_topic(6.2, board=board1, title='Foo', status='archived')
        topic10 = _make_topic(7, board=board1, title='Foo')
        _make_topic(8, board=board1, title='Foo')
        _make_topic(9, board=board1, title='Foo')
        _make_topic(0, board=board2, title='Foo')
        _make_topic(7, board=board1, title='Foo', status='archived')
        _make_topic(7, board=board1, title='Foo', status='locked')
        self.dbsession.commit()
        topic_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            topic_query_svc.list_recent_from_board_slug('foo'),
            [
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
            ])

    def test_list_recent_from_board_slug_not_found(self):
        topic_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            topic_query_svc.list_recent_from_board_slug('notfound'),
            [])

    def test_topic_from_id(self):
        from ..models import Board, Topic
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self.dbsession.commit()
        topic_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            topic_query_svc.topic_from_id(topic.id),
            topic)

    def test_topic_from_id_not_found(self):
        topic_query_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            topic_query_svc.topic_from_id(-1)


class TestUserCreateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import UserCreateService
        return UserCreateService

    def test_create(self):
        from passlib.hash import argon2
        from ..models import User
        user1 = self._make(User(
            username='root',
            encrypted_password='none'))
        self.dbsession.commit()
        user_create_svc = self._get_target_class()(self.dbsession)
        user2 = user_create_svc.create('child', 'passw0rd', user1.id)
        self.assertEqual(user2.parent, user1)
        self.assertEqual(user2.username, 'child')
        self.assertTrue(argon2.verify(
            'passw0rd',
            user2.encrypted_password))

    def test_create_root(self):
        user_create_svc = self._get_target_class()(self.dbsession)
        user = user_create_svc.create('root', 'passw0rd', None)
        self.assertEqual(user.parent, None)
        self.assertEqual(user.username, 'root')


class TestUserLoginService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import UserLoginService
        return UserLoginService

    def test_authenticate(self):
        from passlib.hash import argon2
        from ..models import User
        self._make(User(
            username='foo',
            encrypted_password=argon2.hash('passw0rd')))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertTrue(user_login_svc.authenticate('foo', 'passw0rd'))
        self.assertFalse(user_login_svc.authenticate('foo', 'password'))

    def test_authenticate_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertFalse(user_login_svc.authenticate('foo', 'passw0rd'))

    def test_authenticate_deactivated(self):
        from passlib.hash import argon2
        from ..models import User
        self._make(User(
            username='foo',
            encrypted_password=argon2.hash('passw0rd'),
            deactivated=True))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertFalse(user_login_svc.authenticate('foo', 'passw0rd'))

    def test_authenticate_upgrade(self):
        from passlib.hash import argon2
        from ..models import User
        password = argon2.using(rounds=2).hash('passw0rd')
        user = self._make(User(
            username='foo',
            encrypted_password=password))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertTrue(user_login_svc.authenticate('foo', 'passw0rd'))
        self.dbsession.commit()
        user_new = self.dbsession.query(User).get(user.id)
        password_new = user_new.encrypted_password
        self.assertNotEqual(password, password_new)
        self.assertTrue(user_login_svc.authenticate('foo', 'passw0rd'))
        self.dbsession.commit()
        user_new2 = self.dbsession.query(User).get(user.id)
        self.assertEqual(password_new, user_new2.encrypted_password)

    def test_user_from_token(self):
        from ..models import User, UserSession
        user1 = self._make(User(username='foo', encrypted_password='none'))
        user2 = self._make(User(username='bar', encrypted_password='none'))
        self._make(UserSession(
            user=user1,
            token='foo_token1',
            ip_address='127.0.0.1'))
        self._make(UserSession(
            user=user1,
            token='foo_token2',
            ip_address='127.0.0.1'))
        self._make(UserSession(
            user=user2,
            token='bar_token1',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_login_svc.user_from_token('foo_token1', '127.0.0.1'),
            user1)
        self.assertEqual(
            user_login_svc.user_from_token('foo_token2', '127.0.0.1'),
            user1)
        self.assertEqual(
            user_login_svc.user_from_token('bar_token1', '127.0.0.1'),
            user2)

    def test_user_from_token_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(
            user_login_svc.user_from_token('notexists', '127.0.0.1'))

    def test_user_from_token_deactivated(self):
        from ..models import User, UserSession
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            deactivated=True))
        self._make(UserSession(
            user=user,
            token='foo_token1',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(
            user_login_svc.user_from_token('foo_token', '127.0.0.1'))

    def test_user_from_token_wrong_ip(self):
        from ..models import User, UserSession
        user = self._make(User(
            username='foo',
            encrypted_password='none'))
        self._make(UserSession(
            user=user,
            token='foo_token1',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(
            user_login_svc.user_from_token('foo_token', '127.0.0.2'))

    def test_user_from_token_revoked(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession
        user = self._make(User(username='foo', encrypted_password='none'))
        self._make(UserSession(
            user=user,
            token='foo_token1',
            ip_address='127.0.0.1',
            revoked_at=datetime.now() + timedelta(hours=1)))
        self._make(UserSession(
            user=user,
            token='foo_token2',
            ip_address='127.0.0.1',
            revoked_at=datetime.now() - timedelta(hours=1)))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_login_svc.user_from_token('foo_token1', '127.0.0.1'),
            user)
        self.assertIsNone(
            user_login_svc.user_from_token('foo_token2', '127.0.0.1'))

    def test_groups_from_token(self):
        from ..models import User, UserSession, Group
        group1 = self._make(Group(name='foo'))
        group2 = self._make(Group(name='bar'))
        user1 = self._make(User(
            username='foo',
            encrypted_password='none',
            groups=[group1, group2]))
        user2 = self._make(User(
            username='bar',
            encrypted_password='none',
            groups=[group2]))
        user3 = self._make(User(
            username='baz',
            encrypted_password='none',
            groups=[]))
        self._make(UserSession(
            user=user1,
            token='foo_token',
            ip_address='127.0.0.1'))
        self._make(UserSession(
            user=user2,
            token='bar_token',
            ip_address='127.0.0.1'))
        self._make(UserSession(
            user=user3,
            token='baz_token',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_login_svc.groups_from_token('foo_token', '127.0.0.1'),
            ['bar', 'foo'])
        self.assertEqual(
            user_login_svc.groups_from_token('bar_token', '127.0.0.1'),
            ['bar'])
        self.assertEqual(
            user_login_svc.groups_from_token('baz_token', '127.0.0.1'),
            [])

    def test_groups_from_token_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(
            user_login_svc.groups_from_token('notexists', '127.0.0.1'))

    def test_groups_from_token_wrong_ip(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession, Group
        group1 = self._make(Group(name='foo'))
        group2 = self._make(Group(name='bar'))
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            groups=[group1, group2]))
        self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1',
            revoked_at=datetime.now() + timedelta(hours=1)))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(
            user_login_svc.groups_from_token('foo_token', '127.0.0.2'))

    def test_groups_from_token_deactivated(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession, Group
        group1 = self._make(Group(name='foo'))
        group2 = self._make(Group(name='bar'))
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            groups=[group1, group2],
            deactivated=True))
        self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1',
            revoked_at=datetime.now() + timedelta(hours=1)))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(
            user_login_svc.groups_from_token('foo_token', '127.0.0.1'))

    def test_groups_from_token_revoked(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession, Group
        group1 = self._make(Group(name='foo'))
        group2 = self._make(Group(name='bar'))
        user1 = self._make(User(
            username='foo',
            encrypted_password='none',
            groups=[group1, group2]))
        user2 = self._make(User(
            username='bar',
            encrypted_password='none',
            groups=[group2]))
        self._make(UserSession(
            user=user1,
            token='foo_token',
            ip_address='127.0.0.1',
            revoked_at=datetime.now() + timedelta(hours=1)))
        self._make(UserSession(
            user=user2,
            token='bar_token',
            ip_address='127.0.0.1',
            revoked_at=datetime.now() - timedelta(hours=1)))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_login_svc.groups_from_token('foo_token', '127.0.0.1'),
            ['bar', 'foo'])
        self.assertIsNone(
            user_login_svc.groups_from_token('bar_token', '127.0.0.1'))

    def test_revoke_token(self):
        from ..models import User, UserSession
        user = self._make(User(username='foo', encrypted_password='none'))
        user_session = self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        revoked_at = user_session.revoked_at
        user_login_svc = self._get_target_class()(self.dbsession)
        user_session_new = user_login_svc.revoke_token('foo_token')
        self.assertNotEqual(revoked_at, user_session_new.revoked_at)

    def test_revoke_token_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.revoke_token('notexists'))

    def test_revoke_token_revoked(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession
        user = self._make(User(username='foo', encrypted_password='none'))
        self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1',
            revoked_at=datetime.now() - timedelta(hours=1)))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.revoke_token('foo_token'))

    def test_mark_seen(self):
        from ..models import User, UserSession
        user = self._make(User(username='foo', encrypted_password='none'))
        user_session = self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        last_seen_at = user_session.last_seen_at
        revoked_at = user_session.revoked_at
        user_login_svc = self._get_target_class()(self.dbsession)
        user_session_new = user_login_svc.mark_seen(
            'foo_token',
            '127.0.0.1',
            3600)
        self.assertNotEqual(last_seen_at, user_session_new.last_seen_at)
        self.assertNotEqual(revoked_at, user_session_new.revoked_at)

    def test_mark_seen_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.mark_seen(
            'notexists',
            '127.0.0.1',
            3600))

    def test_mark_seen_wrong_ip(self):
        from ..models import User, UserSession
        user = self._make(User(username='foo', encrypted_password='none'))
        self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.mark_seen(
            'foo_token',
            '127.0.0.2',
            3600))

    def test_mark_seen_deactivated(self):
        from ..models import User, UserSession
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            deactivated=True))
        self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.mark_seen(
            'foo_token',
            '127.0.0.1',
            3600))

    def test_mark_seen_revoked(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession
        user = self._make(User(username='foo', encrypted_password='none'))
        self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1',
            revoked_at=datetime.now() - timedelta(hours=1)))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.mark_seen(
            'foo_token',
            '127.0.0.1',
            3600))

    def test_token_for(self):
        from ..models import User
        user = self._make(User(username='foo', encrypted_password='none'))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        user_token = user_login_svc.token_for('foo', '127.0.0.1')
        self.assertEqual(
            user_login_svc.user_from_token(user_token, '127.0.0.1'),
            user)

    def test_token_for_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            user_login_svc.token_for('notexists', '127.0.0.1')

    def test_token_for_deactivated(self):
        from ..models import User
        self._make(User(
            username='foo',
            encrypted_password='none',
            deactivated=True))
        user_login_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            user_login_svc.token_for('foo', '127.0.0.1')
