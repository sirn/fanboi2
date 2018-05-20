import unittest
import unittest.mock

from sqlalchemy.orm.exc import NoResultFound

from . import ModelSessionMixin


class TestBoardCreateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import BoardCreateService
        return BoardCreateService

    def test_create(self):
        board_create_svc = self._get_target_class()(self.dbsession)
        board = board_create_svc.create(
            'foobar',
            title='Foobar',
            description='Board about foobar',
            status='open',
            agreements='Nope',
            settings={'foo': 'bar'})
        self.assertEqual(board.slug, 'foobar')
        self.assertEqual(board.title, 'Foobar')
        self.assertEqual(board.description, 'Board about foobar')
        self.assertEqual(board.status, 'open')
        self.assertEqual(board.agreements, 'Nope')
        self.assertEqual(board.settings['foo'], 'bar')


class TestBoardQueryService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import BoardQueryService
        return BoardQueryService

    def test_list_all(self):
        from ..models import Board
        board1 = self._make(Board(slug='foo', title='Foo', status='open'))
        board2 = self._make(Board(
            slug='baz',
            title='Baz',
            status='restricted'))
        board3 = self._make(Board(slug='bax', title='Bax', status='locked'))
        board4 = self._make(Board(slug='wel', title='Wel', status='open'))
        board5 = self._make(Board(slug='bar', title='Bar', status='archived'))
        self.dbsession.commit()
        board_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            board_query_svc.list_all(),
            [board5, board3, board2, board1, board4])

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


class TestBoardUpdateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import BoardUpdateService
        return BoardUpdateService

    def test_update(self):
        from ..models import Board
        board = self._make(Board(
            slug='baz',
            title='Baz',
            description='Baz baz baz',
            status='open',
            agreements='Yes',
            settings={'baz': 'baz'}))
        self.dbsession.commit()
        board_update_svc = self._get_target_class()(self.dbsession)
        board_update_svc.update(
            board.slug,
            title='Foobar',
            description='Foo foo foo',
            status='locked',
            agreements='Nope',
            settings={'baz': 'bar'})
        self.assertEqual(board.title, 'Foobar')
        self.assertEqual(board.description, 'Foo foo foo')
        self.assertEqual(board.status, 'locked')
        self.assertEqual(board.agreements, 'Nope')
        self.assertEqual(board.settings['baz'], 'bar')

    def test_update_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        board_update_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            board_update_svc.update(
                'notexists',
                title='Foobar',
                description='Foo foo foo',
                status='locked',
                agreements='Nope',
                settings={'baz': 'bar'})


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
            def value_from_key(self, key, **kwargs):
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
            def value_from_key(self, key, **kwargs):
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
            def value_from_key(self, key, **kwargs):
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


class TestPageCreateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import PageCreateService
        return PageCreateService

    def test_create(self):
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_create_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page = page_create_svc.create(
            'foobar',
            title='Foobar',
            body='**Hello, world!**')
        self.assertEqual(page.slug, 'foobar')
        self.assertEqual(page.title, 'Foobar')
        self.assertEqual(page.body, '**Hello, world!**')
        self.assertEqual(page.namespace, 'public')
        self.assertEqual(page.formatter, 'markdown')

    def test_create_internal(self):
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_create_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page = page_create_svc.create_internal(
            'global/foo',
            body='<em>Hello, world!</em>',
            _internal_pages=(('global/foo', 'html'),))
        self.assertEqual(page.slug, 'global/foo')
        self.assertEqual(page.title, 'global/foo')
        self.assertEqual(page.body, '<em>Hello, world!</em>')
        self.assertEqual(page.namespace, 'internal')
        self.assertEqual(page.formatter, 'html')

    def test_create_internal_not_allowed(self):
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_create_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(ValueError):
            page_create_svc.create_internal(
                'global/foo',
                body='<em>Hello, world!</em>',
                _internal_pages=tuple())

    def test_create_internal_cache(self):
        from ..models import Page
        from ..services import PageQueryService
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_query_svc = PageQueryService(self.dbsession, cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                'global/foo',
                _internal_pages=(('global/foo', 'html'),)),
            None)
        page_create_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page_create_svc.create_internal(
            'global/foo',
            body='<em>Hello, world!</em>',
            _internal_pages=(('global/foo', 'html'),))
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                'global/foo',
                _internal_pages=(('global/foo', 'html'),)),
            '<em>Hello, world!</em>')


class TestPageDeleteService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import PageDeleteService
        return PageDeleteService

    def test_delete(self):
        from sqlalchemy import inspect
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        page1 = self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Foobar**',
            namespace='public',
            formatter='markdown'))
        page2 = self._make(Page(
            slug='foobar2',
            title='Foobar2',
            body='**Foobar2**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        page_delete_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page_delete_svc.delete('foobar')
        self.dbsession.flush()
        self.assertTrue(inspect(page1).was_deleted)
        self.assertFalse(inspect(page2).was_deleted)

    def test_delete_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_delete_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(NoResultFound):
            page_delete_svc.delete('notexists')

    def test_delete_wrong_namespace(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='global/foo',
            title='global/foo',
            body='<em>Foobar</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        page_delete_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(NoResultFound):
            page_delete_svc.delete('global/foo')

    def test_delete_internal(self):
        from sqlalchemy import inspect
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        page1 = self._make(Page(
            slug='global/foo',
            title='global/foo',
            body='<em>Foobar</em>',
            namespace='internal',
            formatter='html'))
        page2 = self._make(Page(
            slug='global/bar',
            title='global/bar',
            body='<em>Baz</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        page_delete_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page_delete_svc.delete_internal('global/foo')
        self.dbsession.flush()
        self.assertTrue(inspect(page1).was_deleted)
        self.assertFalse(inspect(page2).was_deleted)

    def test_delete_internal_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_delete_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(NoResultFound):
            page_delete_svc.delete_internal('global/notexists')

    def test_delete_internal_wrong_namespace(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Foobar**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        page_delete_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(NoResultFound):
            page_delete_svc.delete_internal('foobar')

    def test_delete_internal_cache(self):
        from sqlalchemy import inspect
        from ..models import Page
        from ..services import PageQueryService
        from . import make_cache_region
        cache_region = make_cache_region({})
        page = self._make(Page(
            slug='global/foo',
            title='global/foo',
            body='<em>Foobar</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        page_query_svc = PageQueryService(self.dbsession, cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                'global/foo',
                _internal_pages=(('global/foo', 'html'),)),
            '<em>Foobar</em>')
        page_delete_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page_delete_svc.delete_internal('global/foo')
        self.dbsession.flush()
        self.assertTrue(inspect(page).was_deleted)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                'global/foo',
                _internal_pages=(('global/foo', 'html'),)),
            None)


class TestPageQueryService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import PageQueryService
        return PageQueryService

    def test_list_public(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
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
        page_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertEqual(
            page_query_svc.list_public(),
            [page2, page3, page1])

    def test_list_internal(self):
        from sqlalchemy import inspect
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        internal_pages = (
            ('foo', 'none'),
            ('bar', 'markdown'),
            ('baz', 'html'))
        self._make(Page(
            title='bar',
            slug='bar',
            body='Hello',
            namespace='internal'))
        self._make(Page(
            title='hoge',
            slug='hoge',
            body='Hoge',
            namespace='internal'))
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        pages = page_query_svc.list_internal(_internal_pages=internal_pages)
        self.assertEqual(pages[0].slug, 'bar')
        self.assertTrue(inspect(pages[0]).persistent)
        self.assertEqual(pages[1].slug, 'baz')
        self.assertFalse(inspect(pages[1]).persistent)
        self.assertEqual(pages[2].slug, 'foo')
        self.assertFalse(inspect(pages[2]).persistent)
        self.assertEqual(pages[3].slug, 'hoge')
        self.assertTrue(inspect(pages[3]).persistent)

    def test_public_page_from_slug(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
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
        page_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertEqual(
            page_query_svc.public_page_from_slug('test'),
            page)

    def test_public_page_from_slug_not_found(self):
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(NoResultFound):
            page_query_svc.public_page_from_slug('notfound')

    def test_internal_page_from_slug(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
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
        page_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertEqual(
            page_query_svc.internal_page_from_slug(
                'test',
                _internal_pages=(('test', 'none'),)),
            page)

    def test_internal_page_from_slug_not_found(self):
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(NoResultFound):
            page_query_svc.internal_page_from_slug(
                'notfound',
                _internal_pages=(('notfound', 'none'),))

    def test_internal_page_from_slug_not_allowed(self):
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(ValueError):
            page_query_svc.internal_page_from_slug(
                'notallowed',
                _internal_pages=tuple())

    def test_internal_body_from_slug(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='foo/test',
            title='foo/test',
            body='<em>Test</em>',
            formatter='html',
            namespace='internal'))
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                'foo/test',
                _internal_pages=(('foo/test', 'html'),)),
            '<em>Test</em>')

    def test_internal_body_from_slug_not_found(self):
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertIsNone(page_query_svc.internal_body_from_slug(
            'foo/test',
            _internal_pages=(('foo/test', 'none'),)))

    def test_internal_body_from_slug_not_allowed(self):
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(ValueError):
            page_query_svc.internal_body_from_slug(
                'foo/test',
                _internal_pages=tuple())

    def test_internal_body_from_slug_cache(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        page = self._make(Page(
            slug='foo/test',
            title='foo/test',
            body='<em>Test</em>',
            formatter='html',
            namespace='internal'))
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                'foo/test',
                _internal_pages=(('foo/test', 'html'),)),
            '<em>Test</em>')
        self.dbsession.delete(page)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                'foo/test',
                _internal_pages=(('foo/test', 'html'),)),
            '<em>Test</em>')


class TestPageUpdateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import PageUpdateService
        return PageUpdateService

    def test_update(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Foobar**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page = page_update_svc.update(
            'foobar',
            title='Baz',
            body='*Baz*')
        self.assertEqual(page.slug, 'foobar')
        self.assertEqual(page.title, 'Baz')
        self.assertEqual(page.body, '*Baz*')
        self.assertEqual(page.namespace, 'public')
        self.assertEqual(page.formatter, 'markdown')

    def test_update_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(NoResultFound):
            page_update_svc.update(
                'notexists',
                title='Baz',
                body='*Baz*')

    def test_update_wrong_namespace(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='global/foo',
            title='global/foo',
            body='<em>Foobar</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(NoResultFound):
            page_update_svc.update(
                'global/foo',
                title='Baz',
                body='*Baz*')

    def test_update_none(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Foobar**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page = page_update_svc.update('foobar')
        self.assertEqual(page.slug, 'foobar')
        self.assertEqual(page.title, 'Foobar')
        self.assertEqual(page.body, '**Foobar**')
        self.assertEqual(page.namespace, 'public')
        self.assertEqual(page.formatter, 'markdown')

    def test_update_not_whitelisted(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Foobar**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page = page_update_svc.update(
            'foobar',
            namespace='internal',
            formatter='html')
        self.assertEqual(page.namespace, 'public')
        self.assertEqual(page.formatter, 'markdown')

    def test_update_internal(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='global/foobar',
            title='global/foobar',
            body='<em>Foobar</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page = page_update_svc.update_internal(
            'global/foobar',
            body='<em>Baz</em>')
        self.assertEqual(page.slug, 'global/foobar')
        self.assertEqual(page.title, 'global/foobar')
        self.assertEqual(page.body, '<em>Baz</em>')
        self.assertEqual(page.namespace, 'internal')
        self.assertEqual(page.formatter, 'html')

    def test_update_internal_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from . import make_cache_region
        cache_region = make_cache_region({})
        page_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(NoResultFound):
            page_update_svc.update_internal(
                'global/notexists',
                body='<em>Baz</em>')

    def test_update_internal_wrong_namespace(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Foobar**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(NoResultFound):
            page_update_svc.update_internal(
                'global/foobar',
                body='<em>Baz</em>')

    def test_update_internal_none(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='global/foobar',
            title='global/foobar',
            body='<em>Foobar</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page = page_update_svc.update_internal('global/foobar')
        self.assertEqual(page.slug, 'global/foobar')
        self.assertEqual(page.title, 'global/foobar')
        self.assertEqual(page.body, '<em>Foobar</em>')
        self.assertEqual(page.namespace, 'internal')
        self.assertEqual(page.formatter, 'html')

    def test_update_internal_not_whitelisted(self):
        from ..models import Page
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='global/foobar',
            title='global/foobar',
            body='<em>Foobar</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        page = page_update_svc.update_internal(
            'global/foobar',
            title='Foobar',
            namespace='public',
            formatter='markdown')
        self.assertEqual(page.slug, 'global/foobar')
        self.assertEqual(page.title, 'global/foobar')
        self.assertEqual(page.body, '<em>Foobar</em>')
        self.assertEqual(page.namespace, 'internal')
        self.assertEqual(page.formatter, 'html')

    def test_update_internal_cache(self):
        from ..models import Page
        from ..services import PageQueryService
        from . import make_cache_region
        cache_region = make_cache_region({})
        self._make(Page(
            slug='global/foobar',
            title='global/foobar',
            body='<em>Foobar</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        page_query_svc = PageQueryService(self.dbsession, cache_region)
        page_update_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                'global/foobar',
                _internal_pages=(('global/foobar', 'html'),)),
            '<em>Foobar</em>')
        page_update_svc.update_internal(
            'global/foobar',
            body='<em>Baz</em>')
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                'global/foobar',
                _internal_pages=(('global/foobar', 'html'),)),
            '<em>Baz</em>')


class TestPostCreateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import PostCreateService
        return PostCreateService

    def _make_one(self):
        from ..services import UserQueryService

        class _DummyIdentityService(object):
            def identity_for(self, **kwargs):
                return ','.join(
                    '%s' % (v,) for k, v in sorted(kwargs.items()))

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {'app.time_zone': 'Asia/Bangkok'}.get(key, None)

        return self._get_target_class()(
            self.dbsession,
            _DummyIdentityService(),
            _DummySettingQueryService(),
            UserQueryService(self.dbsession))

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
        self.assertEqual(post.ident_type, 'ident')
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
        self.assertEqual(post.ident_type, 'none')

    def test_create_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        post_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            post_create_svc.create(
                -1,
                'Hello!',
                True,
                '127.0.0.1')

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

    def test_create_with_user(self):
        from ..models import Board, Topic, TopicMeta, User
        board = self._make(Board(
            slug='foo',
            title='Foo',
            settings={'name': 'Nameless Foobar'}))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id,
            user.id,
            'Hello!',
            True,
            '127.0.0.1')
        self.assertEqual(post.number, 1)
        self.assertEqual(post.topic, topic)
        self.assertTrue(post.bumped)
        self.assertEqual(post.name, 'Root')
        self.assertEqual(post.ip_address, '127.0.0.1')
        self.assertEqual(post.ident, 'fooident')
        self.assertEqual(post.ident_type, 'ident_admin')
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(topic_meta.post_count, 1)
        self.assertIsNotNone(topic_meta.bumped_at)

    def test_create_with_user_without_bumped(self):
        from ..models import Board, Topic, TopicMeta, User
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id,
            user.id,
            'Hello!',
            False,
            '127.0.0.1')
        self.assertFalse(post.bumped)
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertIsNone(topic_meta.bumped_at)

    def test_create_with_user_without_ident(self):
        from ..models import Board, Topic, TopicMeta, User
        board = self._make(Board(
            slug='foo',
            title='Foo',
            settings={
                'name': 'Nameless Foobar',
                'use_ident': False}))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id,
            user.id,
            'Hello!',
            True,
            '127.0.0.1')
        self.assertEqual(post.ident, 'fooident')
        self.assertEqual(post.ident_type, 'ident_admin')

    def test_create_with_user_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import User
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            post_create_svc.create_with_user(
                -1,
                user.id,
                'Hello!',
                True,
                '127.0.0.1')

    def test_create_with_user_not_found_user(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            post_create_svc.create_with_user(
                topic.id,
                -1,
                'Hello!',
                True,
                '127.0.0.1')

    def test_create_with_user_topic_limit(self):
        from ..models import Board, Topic, TopicMeta, User
        board = self._make(Board(
            slug='foo',
            title='Foo',
            settings={'max_posts': 10}))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=9))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        self.assertEqual(topic.status, 'open')
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id,
            user.id,
            'Hello!',
            True,
            '127.0.0.1')
        topic = self.dbsession.query(Topic).get(topic.id)
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(post.number, 10)
        self.assertEqual(topic_meta.post_count, 10)
        self.assertEqual(topic.status, 'archived')

    def test_create_with_user_topic_locked(self):
        from ..models import Board, Topic, TopicMeta, User
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(board=board, title='Hello', status='locked'))
        self._make(TopicMeta(topic=topic, post_count=0))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id,
            user.id,
            'Hello!',
            True,
            '127.0.0.1')
        self.assertEqual(post.number, 1)

    def test_create_with_user_topic_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta, User
        board = self._make(Board(slug='foo', title='Foo'))
        topic = self._make(Topic(
            board=board,
            title='Hello',
            status='archived'))
        self._make(TopicMeta(topic=topic, post_count=0))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create_with_user(
                topic.id,
                user.id,
                'Hello!',
                True,
                '127.0.0.1')

    def test_create_with_user_board_restricted(self):
        from ..models import Board, Topic, TopicMeta, User
        board = self._make(Board(slug='foo', title='Foo', status='restricted'))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id,
            user.id,
            'Hello!',
            True,
            '127.0.0.1')
        self.assertEqual(post.number, 1)

    def test_create_with_user_board_locked(self):
        from ..models import Board, Topic, TopicMeta, User
        board = self._make(Board(slug='foo', title='Foo', status='locked'))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id,
            user.id,
            'Hello!',
            True,
            '127.0.0.1')
        self.assertEqual(post.number, 1)

    def test_create_with_user_board_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta, User
        board = self._make(Board(slug='foo', title='Foo', status='archived'))
        topic = self._make(Topic(board=board, title='Hello', status='open'))
        self._make(TopicMeta(topic=topic, post_count=0))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create_with_user(
                topic.id,
                user.id,
                'Hello!',
                True,
                '127.0.0.1')


class TestPostDeleteService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import PostDeleteService
        return PostDeleteService

    def test_delete_from_topic_id(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic, TopicMeta, Post
        board = self._make(Board(slug='foo', title='Foobar'))
        topic = self._make(Topic(board=board, title='Foobar Baz'))
        self._make(TopicMeta(topic=topic, post_count=2))
        post1 = self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Foobar',
            body='Foobar Baz',
            ip_address='127.0.0.1'))
        post2 = self._make(Post(
            topic=topic,
            number=2,
            name='Nameless Foobar',
            body='Second Post',
            ip_address='127.0.0.1'))
        post3 = self._make(Post(
            topic=topic,
            number=3,
            name='Nameless Foobar',
            body='Third time the charm',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        post_delete_svc = self._get_target_class()(self.dbsession)
        post_delete_svc.delete_from_topic_id(topic.id, 2)
        self.dbsession.flush()
        self.assertFalse(inspect(post1).was_deleted)
        self.assertTrue(inspect(post2).was_deleted)
        self.assertFalse(inspect(post3).was_deleted)

    def test_delete_from_topic_id_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import Board, Topic, TopicMeta, Post
        board = self._make(Board(slug='foo', title='Foobar'))
        topic = self._make(Topic(board=board, title='Foobar Baz'))
        self._make(TopicMeta(topic=topic, post_count=2))
        self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Foobar',
            body='Foobar Baz',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        post_delete_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            post_delete_svc.delete_from_topic_id(topic.id, 2)

    def test_delete_from_topic_id_not_found_topic(self):
        from sqlalchemy.orm.exc import NoResultFound
        post_delete_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            post_delete_svc.delete_from_topic_id(-1, 1)


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


class TestRuleBanCreateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import RuleBanCreateService
        return RuleBanCreateService

    def test_create(self):
        from datetime import datetime, timedelta
        rule_ban_create_svc = self._get_target_class()(self.dbsession)
        rule_ban = rule_ban_create_svc.create(
            '10.0.1.0/24',
            description='Violation of galactic law.',
            duration=30,
            scope='galaxy_far_away',
            active=True)
        self.assertEqual(rule_ban.ip_address, '10.0.1.0/24')
        self.assertEqual(rule_ban.description, 'Violation of galactic law.')
        self.assertEqual(rule_ban.scope, 'galaxy_far_away')
        self.assertGreaterEqual(
            rule_ban.active_until,
            datetime.now() + timedelta(days=29, hours=23))
        self.assertTrue(rule_ban.active)

    def test_create_without_optional_fields(self):
        rule_ban_create_svc = self._get_target_class()(self.dbsession)
        rule_ban = rule_ban_create_svc.create('10.0.1.0/24')
        self.assertEqual(rule_ban.ip_address, '10.0.1.0/24')
        self.assertIsNone(rule_ban.description)
        self.assertIsNone(rule_ban.scope)
        self.assertIsNone(rule_ban.active_until)
        self.assertTrue(rule_ban.active)

    def test_create_with_empty_fields(self):
        rule_ban_create_svc = self._get_target_class()(self.dbsession)
        rule_ban = rule_ban_create_svc.create(
            '10.0.1.0/24',
            description='',
            duration='',
            scope='',
            active='')
        self.assertIsNone(rule_ban.scope)
        self.assertIsNone(rule_ban.active_until)
        self.assertIsNone(rule_ban.scope)
        self.assertFalse(rule_ban.active)

    def test_create_deactivated(self):
        rule_ban_create_svc = self._get_target_class()(self.dbsession)
        rule_ban = rule_ban_create_svc.create('10.0.1.0/24', active=False)
        self.assertFalse(rule_ban.active)


class TestRuleBanQueryService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import RuleBanQueryService
        return RuleBanQueryService

    def test_list_active(self):
        from datetime import datetime, timedelta
        from ..models import RuleBan
        rule_ban1 = self._make(RuleBan(
            ip_address='10.0.1.0/24',
            active_until=datetime.now() + timedelta(hours=1)))
        self._make(RuleBan(
            ip_address='10.0.2.0/24',
            active_until=datetime.now() - timedelta(hours=1)))
        rule_ban3 = self._make(RuleBan(
            ip_address='10.0.3.0/24'))
        self._make(RuleBan(
            ip_address='10.0.3.0/24',
            active=False))
        rule_ban5 = self._make(RuleBan(
            ip_address='10.0.3.0/24',
            active_until=datetime.now() + timedelta(hours=2)))
        rule_ban6 = self._make(RuleBan(
            ip_address='10.0.3.0/24',
            created_at=datetime.now() + timedelta(minutes=5)))
        self.dbsession.commit()
        rule_ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            rule_ban_query_svc.list_active(),
            [rule_ban6, rule_ban3, rule_ban5, rule_ban1])

    def test_list_inactive(self):
        from datetime import datetime, timedelta
        from ..models import RuleBan
        self._make(RuleBan(
            ip_address='10.0.1.0/24',
            active_until=datetime.now() + timedelta(hours=1)))
        rule_ban2 = self._make(RuleBan(
            ip_address='10.0.2.0/24',
            active_until=datetime.now() - timedelta(hours=1)))
        self._make(RuleBan(
            ip_address='10.0.3.0/24'))
        rule_ban4 = self._make(RuleBan(
            ip_address='10.0.3.0/24',
            active=False))
        rule_ban5 = self._make(RuleBan(
            ip_address='10.0.3.0/24',
            active_until=datetime.now() - timedelta(hours=2)))
        rule_ban6 = self._make(RuleBan(
            ip_address='10.0.3.0/24',
            created_at=datetime.now() + timedelta(minutes=5),
            active=False))
        self.dbsession.commit()
        rule_ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            rule_ban_query_svc.list_inactive(),
            [rule_ban6, rule_ban4, rule_ban2, rule_ban5])

    def test_is_banned(self):
        from ..models import RuleBan
        self._make(RuleBan(ip_address='10.0.1.0/24'))
        self.dbsession.commit()
        rule_ban_query_svc = self._get_target_class()(self.dbsession)
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

    def test_rule_ban_from_id(self):
        from ..models import RuleBan
        rule_ban = self._make(RuleBan(ip_address='10.0.1.0/24'))
        self.dbsession.commit()
        rule_ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            rule_ban_query_svc.rule_ban_from_id(rule_ban.id),
            rule_ban)

    def test_rule_ban_from_id_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        rule_ban_query_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            rule_ban_query_svc.rule_ban_from_id(-1)

    def test_rule_ban_from_id_string(self):
        from ..models import RuleBan
        rule_ban = self._make(RuleBan(ip_address='10.0.1.0/24'))
        self.dbsession.commit()
        rule_ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            rule_ban_query_svc.rule_ban_from_id(str(rule_ban.id)),
            rule_ban)


class TestRuleBanUpdateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import RuleBanUpdateService
        return RuleBanUpdateService

    def test_update(self):
        import pytz
        from datetime import datetime, timedelta
        from ..models import RuleBan
        rule_ban = self._make(RuleBan(ip_address='10.0.1.0/24'))
        self.dbsession.commit()
        rule_ban_update_svc = self._get_target_class()(self.dbsession)
        rule_ban = rule_ban_update_svc.update(
            rule_ban.id,
            ip_address='10.0.2.0/24',
            description='Violation of galactic law',
            duration=30,
            scope='galaxy_far_away',
            active=False)
        self.assertEqual(rule_ban.ip_address, '10.0.2.0/24')
        self.assertEqual(rule_ban.description, 'Violation of galactic law')
        self.assertGreaterEqual(
            rule_ban.active_until,
            datetime.now(pytz.utc) + timedelta(days=29, hours=23))
        self.assertEqual(rule_ban.scope, 'galaxy_far_away')
        self.assertFalse(rule_ban.active)

    def test_update_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        rule_ban_update_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            rule_ban_update_svc.update(-1, active=False)

    def test_update_duration(self):
        import pytz
        from datetime import datetime, timedelta
        from ..models import RuleBan
        past_now = datetime.now() - timedelta(days=30)
        rule_ban = self._make(RuleBan(
            ip_address='10.0.1.0/24',
            created_at=past_now,
            active_until=past_now + timedelta(days=7)))
        self.dbsession.commit()
        active_until = rule_ban.active_until
        rule_ban_update_svc = self._get_target_class()(self.dbsession)
        rule_ban = rule_ban_update_svc.update(rule_ban.id, duration=14)
        self.assertEqual(rule_ban.duration, 14)
        self.assertGreater(rule_ban.active_until, active_until)
        self.assertLess(rule_ban.active_until, datetime.now(pytz.utc))

    def test_update_duration_no_change(self):
        from datetime import datetime, timedelta
        from ..models import RuleBan
        past_now = datetime.now() - timedelta(days=30)
        rule_ban = self._make(RuleBan(
            ip_address='10.0.1.0/24',
            created_at=past_now,
            active_until=past_now + timedelta(days=7)))
        self.dbsession.commit()
        active_until = rule_ban.active_until
        rule_ban_update_svc = self._get_target_class()(self.dbsession)
        rule_ban = rule_ban_update_svc.update(rule_ban.id, duration=7)
        self.assertEqual(
            rule_ban.active_until,
            active_until)

    def test_update_none(self):
        from ..models import RuleBan
        rule_ban = self._make(RuleBan(
            ip_address='10.0.1.0/24',
            description='In a galaxy far away'))
        self.dbsession.commit()
        rule_ban_update_svc = self._get_target_class()(self.dbsession)
        rule_ban = rule_ban_update_svc.update(rule_ban.id, description=None)
        self.assertIsNone(rule_ban.description)

    def test_update_empty(self):
        from datetime import datetime, timedelta
        from ..models import RuleBan
        rule_ban = self._make(RuleBan(
            ip_address='10.0.1.0/24',
            description='Violation of galactic law',
            active_until=datetime.now() + timedelta(days=7),
            scope='galaxy_far_away'))
        self.dbsession.commit()
        rule_ban_update_svc = self._get_target_class()(self.dbsession)
        rule_ban = rule_ban_update_svc.update(
            rule_ban.id,
            description='',
            duration='',
            scope='',
            active='')
        self.assertIsNone(rule_ban.description)
        self.assertIsNone(rule_ban.active_until)
        self.assertIsNone(rule_ban.scope)
        self.assertFalse(rule_ban.active)


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

    def test_list_all(self):
        from ..models import Setting
        from . import make_cache_region
        cache_region = make_cache_region()
        self._make(Setting(key='app.test', value='test'))
        self._make(Setting(key='bax', value=32))
        self.dbsession.commit()
        setting_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        result = setting_query_svc.list_all(
            _default={
                'foo': None,
                'bar': "baz",
                'bax': 1})
        self.assertEqual(
            result,
            [('bar', "baz"), ('bax', 32), ('foo', None)])

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

    def test_value_from_key_safe_keys(self):
        from . import make_cache_region
        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        with self.assertRaises(KeyError):
            setting_query_svc.value_from_key(
                'app.test',
                safe_keys=True,
                _default={})

    def test_value_from_key_use_cache(self):
        from . import make_cache_region
        from ..models import Setting
        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(
            self.dbsession,
            cache_region)
        self.assertIsNone(
            setting_query_svc.value_from_key(
                'app.test',
                use_cache=True,
                _default={}))
        self._make(Setting(key='app.test', value='test'))
        self.dbsession.commit()
        self.assertIsNone(
            setting_query_svc.value_from_key(
                'app.test',
                use_cache=True,
                _default={}))
        self.assertEqual(
            setting_query_svc.value_from_key(
                'app.test',
                use_cache=False,
                _default={}),
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

    def test_reload_cache(self):
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
        setting_query_svc.reload_cache('app.test')
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
        from ..services import UserQueryService

        class _DummyIdentityService(object):
            def identity_for(self, **kwargs):
                return ','.join(
                    '%s' % (v,) for k, v in sorted(kwargs.items()))

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {'app.time_zone': 'Asia/Bangkok'}.get(key, None)

        return self._get_target_class()(
            self.dbsession,
            _DummyIdentityService(),
            _DummySettingQueryService(),
            UserQueryService(self.dbsession))

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
        self.assertEqual(topic.posts[0].ident_type, 'ident')

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
        self.assertEqual(topic.posts[0].ident_type, 'none')

    def test_create_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        topic_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            topic_create_svc.create(
                'notexists',
                'Hello, world!',
                'Hello Eartians',
                '127.0.0.1')

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

    def test_create_with_user(self):
        from ..models import Board, User
        board = self._make(Board(
            slug='foo',
            title='Foo',
            settings={'name': 'Nameless Foobar'}))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create_with_user(
            board.slug,
            user.id,
            'Hello, world!',
            'Hello Eartians',
            '127.0.0.1')
        self.assertEqual(topic.board, board)
        self.assertEqual(topic.title, 'Hello, world!')
        self.assertEqual(topic.meta.post_count, 1)
        self.assertIsNotNone(topic.meta.bumped_at)
        self.assertEqual(topic.posts[0].number, 1)
        self.assertEqual(topic.posts[0].bumped, True)
        self.assertEqual(topic.posts[0].name, 'Root')
        self.assertEqual(topic.posts[0].ip_address, '127.0.0.1')
        self.assertEqual(topic.posts[0].ident, 'fooident')
        self.assertEqual(topic.posts[0].ident_type, 'ident_admin')

    def test_create_with_user_without_ident(self):
        from ..models import Board, User
        board = self._make(Board(
            slug='foo',
            title='Foo',
            settings={
                'name': 'Nameless Foobar',
                'use_ident': False}))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create_with_user(
            board.slug,
            user.id,
            'Hello, world!',
            'Hello Eartians',
            '127.0.0.1')
        self.assertEqual(topic.posts[0].ident, 'fooident')
        self.assertEqual(topic.posts[0].ident_type, 'ident_admin')

    def test_create_with_user_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import User
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            topic_create_svc.create_with_user(
                'notexists',
                user.id,
                'Hello, world!',
                'Hello Eartians',
                '127.0.0.1')

    def test_create_with_user_not_found_user(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import Board
        board = self._make(Board(
            slug='foo',
            title='Foo',
            settings={
                'name': 'Nameless Foobar',
                'use_ident': False}))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            topic_create_svc.create_with_user(
                board.slug,
                -1,
                'Hello, world!',
                'Hello Eartians',
                '127.0.0.1')

    def test_create_with_user_board_restricted(self):
        from ..models import Board, User
        board = self._make(Board(
            slug='foo',
            title='Foo',
            status='restricted'))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create_with_user(
                board.slug,
                user.id,
                'Hello, world!',
                'Hello Eartians',
                '127.0.0.1')
        self.assertEqual(topic.board, board)
        self.assertEqual(topic.title, 'Hello, world!')
        self.assertEqual(topic.meta.post_count, 1)

    def test_create_with_user_board_locked(self):
        from ..models import Board, User
        board = self._make(Board(
            slug='foo',
            title='Foo',
            status='locked'))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create_with_user(
            board.slug,
            user.id,
            'Hello, world!',
            'Hello Eartians',
            '127.0.0.1')
        self.assertEqual(topic.board, board)
        self.assertEqual(topic.title, 'Hello, world!')
        self.assertEqual(topic.meta.post_count, 1)

    def test_create_with_user_board_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board, User
        board = self._make(Board(
            slug='foo',
            title='Foo',
            status='archived'))
        user = self._make(User(
            username='root',
            encrypted_password='foobar',
            ident='fooident',
            ident_type='ident_admin',
            name='Root'))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            topic_create_svc.create_with_user(
                board.slug,
                user.id,
                'Hello, world!',
                'Hello Eartians',
                '127.0.0.1')


class TestTopicDeleteService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import TopicDeleteService
        return TopicDeleteService

    def test_delete(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic, TopicMeta, Post
        board = self._make(Board(slug='foo', title='Foobar'))
        topic1 = self._make(Topic(board=board, title='Foobar Baz'))
        topic2 = self._make(Topic(board=board, title='Baz Bax'))
        topic_meta1 = self._make(TopicMeta(topic=topic1, post_count=2))
        topic_meta2 = self._make(TopicMeta(topic=topic2, post_count=1))
        post1 = self._make(Post(
            topic=topic1,
            number=1,
            name='Nameless Foobar',
            body='Body',
            ip_address='127.0.0.1'))
        post2 = self._make(Post(
            topic=topic1,
            number=2,
            name='Nameless Foobar',
            body='Foobar',
            ip_address='127.0.0.1'))
        post3 = self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Foobar',
            body='Hi',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        topic_delete_svc = self._get_target_class()(self.dbsession)
        topic_delete_svc.delete(topic1.id)
        self.dbsession.flush()
        self.assertTrue(inspect(topic1).was_deleted)
        self.assertFalse(inspect(topic2).was_deleted)
        self.assertTrue(inspect(topic_meta1).was_deleted)
        self.assertFalse(inspect(topic_meta2).was_deleted)
        self.assertTrue(inspect(post1).was_deleted)
        self.assertTrue(inspect(post2).was_deleted)
        self.assertFalse(inspect(post3).was_deleted)

    def test_delete_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        topic_delete_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            topic_delete_svc.delete(-1)


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

    def test_list_recent(self):
        from datetime import datetime, timedelta
        from ..models import Board, Topic, TopicMeta

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
        topic1 = _make_topic(0.1, board=board1, title='Foo')
        topic2 = _make_topic(1, board=board1, title='Foo')
        topic3 = _make_topic(2, board=board1, title='Foo')
        topic4 = _make_topic(3, board=board1, title='Foo')
        topic5 = _make_topic(4, board=board1, title='Foo')
        topic6 = _make_topic(5, board=board1, title='Foo')
        topic7 = _make_topic(6, board=board1, title='Foo')
        topic8 = _make_topic(6.1, board=board1, title='Foo', status='locked')
        topic9 = _make_topic(6.2, board=board1, title='Foo', status='archived')
        topic10 = _make_topic(7, board=board1, title='Foo')
        topic11 = _make_topic(8, board=board1, title='Foo')
        topic12 = _make_topic(9, board=board1, title='Foo')
        topic13 = _make_topic(0.2, board=board2, title='Foo')
        _make_topic(7, board=board1, title='Foo', status='archived')
        _make_topic(7, board=board1, title='Foo', status='locked')
        self.dbsession.commit()
        topic_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            topic_query_svc.list_recent(_limit=20),
            [
                topic1,
                topic13,
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


class TestTopicUpdateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import TopicUpdateService
        return TopicUpdateService

    def test_update(self):
        from ..models import Board, Topic
        board = self._make(Board(slug='foo', title='Foobar'))
        topic = self._make(Topic(
            board=board,
            title='Foobar Baz',
            status='open'))
        self.dbsession.commit()
        topic_update_svc = self._get_target_class()(self.dbsession)
        topic_update_svc.update(topic.id, status='locked')
        self.assertEqual(topic.status, 'locked')

    def test_update_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        topic_update_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            topic_update_svc.update(-1, status='locked')


class TestUserCreateService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import UserCreateService
        return UserCreateService

    def _make_one(self):
        class _DummyIdentityService(object):
            def identity_for(self, **kwargs):
                return 'id=' + ','.join(
                    '%s' % (v,) for k, v in sorted(kwargs.items()))

        return self._get_target_class()(
            self.dbsession,
            _DummyIdentityService())

    def test_create(self):
        from passlib.hash import argon2
        from ..models import User, Group
        group1 = self._make(Group(name='admin'))
        group2 = self._make(Group(name='mod'))
        user1 = self._make(User(
            username='root',
            encrypted_password='none',
            ident='fooident',
            ident_type='ident_admin',
            name='Root',
            groups=[group1]))
        self.dbsession.commit()
        user_create_svc = self._make_one()
        user2 = user_create_svc.create(
            user1.id,
            'child',
            'passw0rd',
            'Child',
            ['mod', 'janitor'])
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(Group).count(), 3)
        group3 = self.dbsession.query(Group).filter_by(name='janitor').first()
        self.assertEqual(user2.parent, user1)
        self.assertEqual(user2.username, 'child')
        self.assertEqual(user2.ident, 'id=child')
        self.assertEqual(user2.ident_type, 'ident')
        self.assertEqual(user2.name, 'Child')
        self.assertEqual(user2.groups, [group3, group2])
        self.assertTrue(argon2.verify(
            'passw0rd',
            user2.encrypted_password))

    def test_create_root(self):
        from ..models import Group
        user_create_svc = self._make_one()
        user = user_create_svc.create(
            None,
            'root',
            'passw0rd',
            'Root',
            ['admin'])
        self.assertEqual(self.dbsession.query(Group).count(), 1)
        group = self.dbsession.query(Group).filter_by(name='admin').first()
        self.assertIsNone(user.parent)
        self.assertEqual(user.username, 'root')
        self.assertEqual(user.ident, 'id=root')
        self.assertEqual(user.ident_type, 'ident_admin')
        self.assertEqual(user.name, 'Root')
        self.assertEqual(user.groups, [group])

    def test_create_without_group(self):
        from ..models import Group
        user_create_svc = self._make_one()
        user = user_create_svc.create(
            None,
            'root',
            'passw0rd',
            'Root',
            [])
        self.assertEqual(self.dbsession.query(Group).count(), 0)
        self.assertEqual(user.parent, None)
        self.assertEqual(user.username, 'root')
        self.assertEqual(user.ident, 'id=root')
        self.assertEqual(user.ident_type, 'ident')
        self.assertEqual(user.name, 'Root')
        self.assertEqual(user.groups, [])


class TestUserLoginService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import UserLoginService
        return UserLoginService

    def test_authenticate(self):
        from passlib.hash import argon2
        from ..models import User
        self._make(User(
            username='foo',
            encrypted_password=argon2.hash('passw0rd'),
            ident='foo',
            name='Nameless User'))
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
            ident='foo',
            name='Nameless User',
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
            encrypted_password=password,
            ident='foo',
            name='Nameless User'))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertTrue(user_login_svc.authenticate('foo', 'passw0rd'))
        self.assertNotEqual(password, user.encrypted_password)
        password_new = user.encrypted_password
        self.assertTrue(user_login_svc.authenticate('foo', 'passw0rd'))
        self.assertEqual(password_new, user.encrypted_password)

    def test_user_from_token(self):
        from ..models import User, UserSession
        user1 = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            name='Nameless User'))
        user2 = self._make(User(
            username='bar',
            encrypted_password='none',
            ident='bar',
            name='Nameless Bar'))
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
            ident='foo',
            name='Nameless User',
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
            encrypted_password='none',
            ident='foo',
            name='Nameless User'))
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
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            name='Nameless User'))
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
            ident='foo',
            name='Nameless User',
            groups=[group1, group2]))
        user2 = self._make(User(
            username='bar',
            encrypted_password='none',
            ident='foo',
            name='Nameless Bar',
            groups=[group2]))
        user3 = self._make(User(
            username='baz',
            encrypted_password='none',
            ident='baz',
            name='Nameless Baz',
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
            ident='foo',
            name='Nameless User',
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
            ident='foo',
            name='Nameless User',
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
            ident='foo',
            name='Nameless User',
            groups=[group1, group2]))
        user2 = self._make(User(
            username='bar',
            encrypted_password='none',
            ident='bar',
            name='Nameless Bar',
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
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            name='Nameless User'))
        user_session = self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertIsNone(user_session.revoked_at)
        user_login_svc = self._get_target_class()(self.dbsession)
        user_login_svc.revoke_token('foo_token', '127.0.0.1')
        self.assertIsNotNone(user_session.revoked_at)

    def test_revoke_token_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.revoke_token(
            'notexists',
            '127.0.0.1'))

    def test_revoke_token_wrong_ip(self):
        from ..models import User, UserSession
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            name='Nameless User'))
        self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.revoke_token(
            'notexists',
            '127.0.0.2'))

    def test_revoke_token_revoked(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            name='Nameless User'))
        self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1',
            revoked_at=datetime.now() - timedelta(hours=1)))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.revoke_token(
            'foo_token',
            '127.0.0.1'))

    def test_mark_seen(self):
        from ..models import User, UserSession
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            name='Nameless User'))
        user_session = self._make(UserSession(
            user=user,
            token='foo_token',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertIsNone(user_session.last_seen_at)
        self.assertIsNone(user_session.revoked_at)
        user_login_svc = self._get_target_class()(self.dbsession)
        user_login_svc.mark_seen('foo_token', '127.0.0.1', 3600)
        self.assertIsNotNone(user_session.last_seen_at)
        self.assertIsNotNone(user_session.revoked_at)

    def test_mark_seen_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.mark_seen(
            'notexists',
            '127.0.0.1',
            3600))

    def test_mark_seen_wrong_ip(self):
        from ..models import User, UserSession
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            name='Nameless User'))
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
            ident='foo',
            name='Nameless User',
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
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            name='Nameless User'))
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
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            name='Nameless User'))
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
            ident='foo',
            name='Nameless User',
            deactivated=True))
        user_login_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            user_login_svc.token_for('foo', '127.0.0.1')


class TestUserQueryService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import UserQueryService
        return UserQueryService

    def test_user_from_id(self):
        from ..models import User
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            name='Nameless User'))
        self.dbsession.commit()
        user_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_query_svc.user_from_id(user.id),
            user)

    def test_user_from_id_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        user_query_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            user_query_svc.user_from_id(-1)


class TestUserSessionQueryService(ModelSessionMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..services import UserSessionQueryService
        return UserSessionQueryService

    def test_list_recent_from_user_id(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession
        user1 = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            ident_type='ident_admin',
            name='Nameless Foo'))
        user2 = self._make(User(
            username='baz',
            encrypted_password='none',
            ident='baz',
            ident_type='ident_admin',
            name='Nameless Baz'))
        user_session1 = self._make(UserSession(
            user=user1,
            token='user1_token1',
            ip_address='127.0.0.1',
            last_seen_at=datetime.now() - timedelta(days=2)))
        user_session2 = self._make(UserSession(
            user=user1,
            token='user1_token2',
            ip_address='127.0.0.1',
            last_seen_at=datetime.now() - timedelta(days=3)))
        user_session3 = self._make(UserSession(
            user=user1,
            token='user1_token3',
            ip_address='127.0.0.1',
            last_seen_at=datetime.now() - timedelta(days=1)))
        self._make(UserSession(
            user=user2,
            token='user2_token1',
            ip_address='127.0.0.1',
            last_seen_at=datetime.now()))
        self.dbsession.commit()
        user_session_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_session_query_svc.list_recent_from_user_id(user1.id),
            [user_session3, user_session1, user_session2])

    def test_list_recent_from_user_id_empty(self):
        from ..models import User
        user = self._make(User(
            username='foo',
            encrypted_password='none',
            ident='foo',
            ident_type='ident_admin',
            name='Nameless Foo'))
        self.dbsession.commit()
        user_session_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_session_query_svc.list_recent_from_user_id(user.id),
            [])

    def test_list_recent_from_user_id_not_found(self):
        user_session_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_session_query_svc.list_recent_from_user_id(-1),
            [])
