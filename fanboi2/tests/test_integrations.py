import unittest
import unittest.mock

from pyramid import testing
from webob.multidict import MultiDict

from . import ModelSessionMixin


class TestIntegrationAPI(ModelSessionMixin, unittest.TestCase):

    def setUp(self):
        super(TestIntegrationAPI, self).setUp()
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry
        self.request.user_agent = 'Mock/1.0'
        self.request.client_addr = '127.0.0.1'
        self.request.referrer = 'https://www.example.com/referer'
        self.request.url = 'https://www.example.com/url'
        self.request.application_url = 'https://www.example.com'

    def tearDown(self):
        super(TestIntegrationAPI, self).tearDown()
        testing.tearDown()

    def test_root(self):
        from ..views.api import root
        self.request.method = 'GET'
        self.assertEqual(
            root(self.request),
            {})

    def test_boards_get(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services.board import BoardQueryService
        from ..views.api import boards_get
        from . import mock_service
        board1 = self._make(Board(title='Foobar', slug='foobar'))
        board2 = self._make(Board(title='Foobaz', slug='foobaz'))
        board3 = self._make(Board(title='Demo', slug='foodemo'))
        self._make(Board(title='Archived', slug='archived', status='archived'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        self.assertEqual(
            boards_get(request),
            [board3, board1, board2])

    def test_board_get(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services.board import BoardQueryService
        from ..views.api import board_get
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        self.assertEqual(
            board_get(request),
            board)

    def test_board_get_archived(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services.board import BoardQueryService
        from ..views.api import board_get
        from . import mock_service
        board = self._make(Board(
            title='Foobar',
            slug='foobar',
            status='archived'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        self.assertEqual(
            board_get(request),
            board)

    def test_board_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services.board import BoardQueryService
        from ..views.api import board_get
        from . import mock_service
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            board_get(request)

    def test_board_topics_get(self):
        from datetime import datetime, timedelta
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.api import board_topics_get
        from . import mock_service

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
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board1.slug
        self.assertEqual(
            board_topics_get(request),
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

    def test_board_topics_get_empty(self):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.api import board_topics_get
        from . import mock_service
        board = self._make(Board(title='Foo', slug='foo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        self.assertEqual(
            board_topics_get(request),
            [])

    def test_board_topics_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.api import board_topics_get
        from . import mock_service
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            print(board_topics_get(request))

    @unittest.mock.patch('fanboi2.tasks.topic.add_topic.delay')
    def test_board_topics_post(self, add_):
        from ..interfaces import IBoardQueryService, ITopicCreateService
        from ..interfaces import IRateLimiterService, IRuleBanQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicCreateService
        from ..services import IdentityService, SettingQueryService
        from ..services import RateLimiterService, RuleBanQueryService
        from ..views.api import board_topics_post
        from . import mock_service, make_cache_region, DummyRedis
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IRateLimiterService: rate_limiter_svc,
            IRuleBanQueryService: RuleBanQueryService(self.dbsession),
            ITopicCreateService: TopicCreateService(
                self.dbsession,
                IdentityService(redis_conn, 10),
                SettingQueryService(self.dbsession, cache_region))})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/json'
        request.json_body = {}
        request.json_body['title'] = 'title'
        request.json_body['body'] = 'bodyb'
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            0)
        add_.return_value = mock_response = unittest.mock.Mock(id='task-uuid')
        response = board_topics_post(request)
        self.assertEqual(response, mock_response)
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            10)
        add_.assert_called_with(
            'foo',
            'title',
            'bodyb',
            '127.0.0.1',
            payload={
                'application_url': request.application_url,
                'referrer': request.referrer,
                'url': request.url,
                'user_agent': request.user_agent,
            })

    @unittest.mock.patch('fanboi2.tasks.topic.add_topic.delay')
    def test_board_topics_post_wwwform(self, add_):
        from ..interfaces import IBoardQueryService, ITopicCreateService
        from ..interfaces import IRateLimiterService, IRuleBanQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicCreateService
        from ..services import IdentityService, SettingQueryService
        from ..services import RateLimiterService, RuleBanQueryService
        from ..views.api import board_topics_post
        from . import mock_service, make_cache_region, DummyRedis
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IRateLimiterService: rate_limiter_svc,
            IRuleBanQueryService: RuleBanQueryService(self.dbsession),
            ITopicCreateService: TopicCreateService(
                self.dbsession,
                IdentityService(redis_conn, 10),
                SettingQueryService(self.dbsession, cache_region))})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['title'] = 'title'
        request.POST['body'] = 'bodyb'
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            0)
        add_.return_value = mock_response = unittest.mock.Mock(id='task-uuid')
        response = board_topics_post(request)
        self.assertEqual(response, mock_response)
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            10)
        add_.assert_called_with(
            'foo',
            'title',
            'bodyb',
            '127.0.0.1',
            payload={
                'application_url': request.application_url,
                'referrer': request.referrer,
                'url': request.url,
                'user_agent': request.user_agent,
            })

    def test_board_topics_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.api import board_topics_post
        from . import mock_service
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            board_topics_post(request)

    def test_board_topics_post_invalid_title(self):
        from ..errors import ParamsInvalidError
        from ..interfaces import IBoardQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService
        from ..views.api import board_topics_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/json'
        request.json_body = {}
        request.json_body['title'] = 'titl'
        request.json_body['body'] = 'bodyb'
        with self.assertRaises(ParamsInvalidError):
            board_topics_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topics_post_invalid_body(self):
        from ..errors import ParamsInvalidError
        from ..interfaces import IBoardQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService
        from ..views.api import board_topics_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/json'
        request.json_body = {}
        request.json_body['title'] = 'title'
        request.json_body['body'] = 'body'
        with self.assertRaises(ParamsInvalidError):
            board_topics_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topics_post_banned(self):
        from ..errors import BanRejectedError
        from ..interfaces import IBoardQueryService, IRuleBanQueryService
        from ..models import Board, Topic, RuleBan
        from ..services import BoardQueryService, RuleBanQueryService
        from ..views.api import board_topics_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foo'))
        self._make(RuleBan(ip_address='127.0.0.0/24', scope='board:foo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/json'
        request.client_addr = '127.0.0.1'
        request.json_body = {}
        request.json_body['title'] = 'title'
        request.json_body['body'] = 'bodyb'
        with self.assertRaises(BanRejectedError):
            board_topics_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topics_post_banned_unscoped(self):
        from ..errors import BanRejectedError
        from ..interfaces import IBoardQueryService, IRuleBanQueryService
        from ..models import Board, Topic, RuleBan
        from ..services import BoardQueryService, RuleBanQueryService
        from ..views.api import board_topics_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foo'))
        self._make(RuleBan(ip_address='127.0.0.0/24'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/json'
        request.client_addr = '127.0.0.1'
        request.json_body = {}
        request.json_body['title'] = 'title'
        request.json_body['body'] = 'bodyb'
        with self.assertRaises(BanRejectedError):
            board_topics_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topics_post_rate_limited(self):
        from ..errors import RateLimitedError
        from ..interfaces import IBoardQueryService
        from ..interfaces import IRateLimiterService, IRuleBanQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService
        from ..services import RateLimiterService, RuleBanQueryService
        from ..views.api import board_topics_post
        from . import mock_service, DummyRedis
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IRateLimiterService: rate_limiter_svc,
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/json'
        request.json_body = {}
        request.json_body['title'] = 'title'
        request.json_body['body'] = 'bodyb'
        rate_limiter_svc.limit_for(
            10,
            ip_address=request.client_addr,
            board=board.slug)
        with self.assertRaises(RateLimitedError):
            board_topics_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_task_get(self, result_):
        from ..interfaces import ITaskQueryService
        from ..models import Board, Topic
        from ..services import TaskQueryService
        from ..views.api import task_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foo'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self.dbsession.commit()
        result_.return_value = async_result = DummyAsyncResult(
            'dummy',
            'success',
            ['topic', topic.id])
        request = mock_service(self.request, {
            'db': self.dbsession,
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['task'] = 'dummy'
        response = task_get(request)
        self.assertEqual(response.id, async_result.id)
        self.assertEqual(response.deserialize(request), topic)
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_task_get_rejected(self, result_):
        from ..errors import AkismetRejectedError
        from ..interfaces import ITaskQueryService
        from ..services import TaskQueryService
        from ..views.api import task_get
        from . import mock_service, DummyAsyncResult
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['failure', 'akismet_rejected'])
        request = mock_service(self.request, {
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['task'] = 'dummy'
        with self.assertRaises(AkismetRejectedError):
            task_get(request)
        result_.assert_called_with('dummy')

    def test_topic_get(self):
        from ..interfaces import ITopicQueryService
        from ..models import Board, Topic
        from ..services import TopicQueryService
        from ..views.api import topic_get
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Demo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['topic'] = topic.id
        self.assertEqual(
            topic_get(request),
            topic)

    def test_topic_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import ITopicQueryService
        from ..services import TopicQueryService
        from ..views.api import topic_get
        from . import mock_service
        request = mock_service(self.request, {
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['topic'] = '-1'
        with self.assertRaises(NoResultFound):
            topic_get(request)

    def test_topic_posts_get(self):
        from ..interfaces import IPostQueryService
        from ..models import Board, Topic, Post
        from ..services import PostQueryService
        from ..views.api import topic_posts_get
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic1 = self._make(Topic(board=board, title='Demo'))
        topic2 = self._make(Topic(board=board, title='Demo 2'))
        post1 = self._make(Post(
            topic=topic1,
            number=1,
            name='Nameless Fanboi',
            body='Lorem ipsum',
            ip_address='127.0.0.1'))
        post2 = self._make(Post(
            topic=topic1,
            number=2,
            name='Nameless Fanboi',
            body='Dolor sit',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Fanboi',
            body='Foobar',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPostQueryService: PostQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['topic'] = topic1.id
        self.assertEqual(
            topic_posts_get(request),
            [post1, post2])

    def test_topic_posts_get_query(self):
        from ..interfaces import IPostQueryService
        from ..models import Board, Topic, Post
        from ..services import PostQueryService
        from ..views.api import topic_posts_get
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic1 = self._make(Topic(board=board, title='Demo'))
        topic2 = self._make(Topic(board=board, title='Demo 2'))
        posts = []
        for i in range(50):
            posts.append(self._make(Post(
                topic=topic1,
                number=i + 1,
                name='Nameless Fanboi',
                body='Lorem ipsum',
                ip_address='127.0.0.1')))
        self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Fanboi',
            body='Foobar',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPostQueryService: PostQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['topic'] = topic1.id
        request.matchdict['query'] = '1'
        self.assertEqual(
            topic_posts_get(request),
            posts[0:1])
        request.matchdict['query'] = '50'
        self.assertEqual(
            topic_posts_get(request),
            posts[49:50])
        request.matchdict['query'] = '51'
        self.assertEqual(
            topic_posts_get(request),
            [])
        request.matchdict['query'] = '1-50'
        self.assertEqual(
            topic_posts_get(request),
            posts)
        request.matchdict['query'] = '10-20'
        self.assertEqual(
            topic_posts_get(request),
            posts[9:20])
        request.matchdict['query'] = '51-99'
        self.assertEqual(
            topic_posts_get(request),
            [])
        request.matchdict['query'] = '0-51'
        self.assertEqual(
            topic_posts_get(request),
            posts)
        request.matchdict['query'] = '-0'
        self.assertEqual(
            topic_posts_get(request),
            [])
        request.matchdict['query'] = '-5'
        self.assertEqual(
            topic_posts_get(request),
            posts[:5])
        request.matchdict['query'] = '45-'
        self.assertEqual(
            topic_posts_get(request),
            posts[44:])
        request.matchdict['query'] = '100-'
        self.assertEqual(
            topic_posts_get(request),
            [])
        request.matchdict['query'] = 'recent'
        self.assertEqual(
            topic_posts_get(request),
            posts[20:])
        request.matchdict['query'] = 'l30'
        self.assertEqual(
            topic_posts_get(request),
            posts[20:])

    def test_topic_posts_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPostQueryService
        from ..services import PostQueryService
        from ..views.api import topic_posts_get
        from . import mock_service
        request = mock_service(self.request, {
            IPostQueryService: PostQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['topic'] = '-1'
        with self.assertRaises(NoResultFound):
            topic_posts_get(request)

    @unittest.mock.patch('fanboi2.tasks.post.add_post.delay')
    def test_topic_posts_post(self, add_):
        from ..interfaces import IRateLimiterService, IRuleBanQueryService
        from ..interfaces import ITopicQueryService, IPostCreateService
        from ..models import Board, Topic, TopicMeta
        from ..services import IdentityService, SettingQueryService
        from ..services import RateLimiterService, RuleBanQueryService
        from ..services import TopicQueryService, PostCreateService
        from ..views.api import topic_posts_post
        from . import mock_service, make_cache_region, DummyRedis
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(self.request, {
            ITopicQueryService: TopicQueryService(self.dbsession),
            IRateLimiterService: rate_limiter_svc,
            IRuleBanQueryService: RuleBanQueryService(self.dbsession),
            IPostCreateService: PostCreateService(
                self.dbsession,
                IdentityService(redis_conn, 10),
                SettingQueryService(self.dbsession, cache_region))})
        request.method = 'POST'
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/json'
        request.json_body = {}
        request.json_body['body'] = 'bodyb'
        request.json_body['bumped'] = True
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            0)
        add_.return_value = mock_response = unittest.mock.Mock(id='task-uuid')
        response = topic_posts_post(request)
        self.assertEqual(response, mock_response)
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            10)
        add_.assert_called_with(
            topic.id,
            'bodyb',
            True,
            '127.0.0.1',
            payload={
                'application_url': request.application_url,
                'referrer': request.referrer,
                'url': request.url,
                'user_agent': request.user_agent,
            })

    @unittest.mock.patch('fanboi2.tasks.post.add_post.delay')
    def test_topic_posts_post_wwwform(self, add_):
        from ..interfaces import IRateLimiterService, IRuleBanQueryService
        from ..interfaces import ITopicQueryService, IPostCreateService
        from ..models import Board, Topic, TopicMeta
        from ..services import IdentityService, SettingQueryService
        from ..services import RateLimiterService, RuleBanQueryService
        from ..services import TopicQueryService, PostCreateService
        from ..views.api import topic_posts_post
        from . import mock_service, make_cache_region, DummyRedis
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(self.request, {
            ITopicQueryService: TopicQueryService(self.dbsession),
            IRateLimiterService: rate_limiter_svc,
            IRuleBanQueryService: RuleBanQueryService(self.dbsession),
            IPostCreateService: PostCreateService(
                self.dbsession,
                IdentityService(redis_conn, 10),
                SettingQueryService(self.dbsession, cache_region))})
        request.method = 'POST'
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['body'] = 'bodyb'
        request.POST['bumped'] = '1'
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            0)
        add_.return_value = mock_response = unittest.mock.Mock(id='task-uuid')
        response = topic_posts_post(request)
        self.assertEqual(response, mock_response)
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            10)
        add_.assert_called_with(
            topic.id,
            'bodyb',
            True,
            '127.0.0.1',
            payload={
                'application_url': request.application_url,
                'referrer': request.referrer,
                'url': request.url,
                'user_agent': request.user_agent,
            })

    def test_topic_posts_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import ITopicQueryService
        from ..services import TopicQueryService
        from ..views.api import topic_posts_post
        from . import mock_service
        request = mock_service(self.request, {
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['topic'] = '-1'
        with self.assertRaises(NoResultFound):
            topic_posts_post(request)

    def test_topic_posts_post_invalid_body(self):
        from ..errors import ParamsInvalidError
        from ..interfaces import ITopicQueryService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import TopicQueryService
        from ..views.api import topic_posts_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(self.request, {
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/json'
        request.json_body = {}
        request.json_body['body'] = 'body'
        request.json_body['bumped'] = True
        with self.assertRaises(ParamsInvalidError):
            topic_posts_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_topic_posts_post_banned(self):
        from ..errors import BanRejectedError
        from ..interfaces import ITopicQueryService, IRuleBanQueryService
        from ..models import Board, Topic, TopicMeta, Post, RuleBan
        from ..services import TopicQueryService, RuleBanQueryService
        from ..views.api import topic_posts_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(RuleBan(ip_address='127.0.0.0/24', scope='board:foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(self.request, {
            ITopicQueryService: TopicQueryService(self.dbsession),
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/json'
        request.client_addr = '127.0.0.1'
        request.json_body = {}
        request.json_body['body'] = 'bodyb'
        request.json_body['bumped'] = True
        with self.assertRaises(BanRejectedError):
            topic_posts_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_topic_posts_post_banned_unscoped(self):
        from ..errors import BanRejectedError
        from ..interfaces import ITopicQueryService, IRuleBanQueryService
        from ..models import Board, Topic, TopicMeta, Post, RuleBan
        from ..services import TopicQueryService, RuleBanQueryService
        from ..views.api import topic_posts_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(RuleBan(ip_address='127.0.0.0/24'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(self.request, {
            ITopicQueryService: TopicQueryService(self.dbsession),
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/json'
        request.client_addr = '127.0.0.1'
        request.json_body = {}
        request.json_body['body'] = 'bodyb'
        request.json_body['bumped'] = True
        with self.assertRaises(BanRejectedError):
            topic_posts_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_topic_posts_post_rate_limited(self):
        from ..errors import RateLimitedError
        from ..interfaces import IRateLimiterService, IRuleBanQueryService
        from ..interfaces import ITopicQueryService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import RateLimiterService, RuleBanQueryService
        from ..services import TopicQueryService
        from ..views.api import topic_posts_post
        from . import mock_service, DummyRedis
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(self.request, {
            ITopicQueryService: TopicQueryService(self.dbsession),
            IRateLimiterService: rate_limiter_svc,
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/json'
        request.json_body = {}
        request.json_body['body'] = 'bodyb'
        request.json_body['bumped'] = True
        rate_limiter_svc.limit_for(
            10,
            ip_address=request.client_addr,
            board=board.slug)
        with self.assertRaises(RateLimitedError):
            topic_posts_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_pages_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.api import pages_get
        from . import mock_service
        page1 = self._make(Page(title='Foo', body='Foo', slug='foo'))
        page2 = self._make(Page(title='Bar', body='Bar', slug='bar'))
        page3 = self._make(Page(title='Baz', body='Baz', slug='baz'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        self.assertEqual(
            pages_get(request),
            [page2, page3, page1])

    def test_page_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.api import page_get
        from . import mock_service
        page = self._make(Page(title='Foo', body='Foo', slug='foo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = page.slug
        self.assertEqual(
            page_get(request),
            page)

    def test_page_get_internal(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.api import page_get
        from . import mock_service
        page = self._make(Page(
            title='Foo',
            body='Foo',
            slug='foo',
            namespace='internal'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = page.slug
        with self.assertRaises(NoResultFound):
            page_get(request)

    def test_page_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.api import page_get
        from . import mock_service
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'notexists'
        with self.assertRaises(NoResultFound):
            page_get(request)

    def test_error_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..views.api import error_not_found
        self.request.path = '/foobar'
        response = error_not_found(HTTPNotFound(), self.request)
        self.assertEqual(self.request.response.status, '404 Not Found')
        self.assertEqual(response['type'], 'error')
        self.assertEqual(response['status'], 'not_found')
        self.assertEqual(
            response['message'],
            'The resource GET /foobar could not be found.')

    def test_error_base_handler(self):
        from ..errors import BaseError
        from ..views.api import error_base_handler
        self.request.path = '/foobar'
        exc = BaseError()
        response = error_base_handler(exc, self.request)
        self.assertEqual(self.request.response.status, exc.http_status)
        self.assertEqual(response, exc)

    def test_api_routes_predicates(self):
        from ..views.api import _api_routes_only
        self.request.path = '/api/test'
        self.assertTrue(_api_routes_only(None, self.request))

    def test_api_routes_predicates_not_api(self):
        from ..views.api import _api_routes_only
        self.request.path = '/foobar/api'
        self.assertFalse(_api_routes_only(None, self.request))


class TestIntegrationBoard(ModelSessionMixin, unittest.TestCase):

    def setUp(self):
        super(TestIntegrationBoard, self).setUp()
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry
        self.request.user_agent = 'Mock/1.0'
        self.request.client_addr = '127.0.0.1'
        self.request.referrer = 'https://www.example.com/referer'
        self.request.url = 'https://www.example.com/url'
        self.request.application_url = 'https://www.example.com'

    def tearDown(self):
        super(TestIntegrationBoard, self).tearDown()
        testing.tearDown()

    def test_root(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services.board import BoardQueryService
        from ..views.boards import root
        from . import mock_service
        board1 = self._make(Board(title='Foobar', slug='foobar'))
        board2 = self._make(Board(title='Foobaz', slug='foobaz'))
        board3 = self._make(Board(title='Demo', slug='foodemo'))
        self._make(Board(title='Archived', slug='archived', status='archived'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        response = root(request)
        self.assertEqual(
            response['boards'],
            [board3, board1, board2])

    def test_board_show(self):
        from datetime import datetime, timedelta
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.boards import board_show
        from . import mock_service

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
        _make_topic(8, board=board1, title='Foo')
        _make_topic(9, board=board1, title='Foo')
        _make_topic(0, board=board2, title='Foo')
        _make_topic(7, board=board1, title='Foo', status='archived')
        _make_topic(7, board=board1, title='Foo', status='locked')
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board1.slug
        response = board_show(request)
        self.assertEqual(response['board'], board1)
        self.assertEqual(
            response['topics'],
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

    def test_board_show_empty(self):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.boards import board_show
        from . import mock_service
        board = self._make(Board(title='Foo', slug='foo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        response = board_show(request)
        self.assertEqual(response['board'], board)
        self.assertEqual(
            response['topics'],
            [])

    def test_board_show_archived(self):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.boards import board_show
        from . import mock_service
        board = self._make(Board(
            title='Foo',
            slug='foo',
            status='archived'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        response = board_show(request)
        self.assertEqual(response['board'], board)
        self.assertEqual(
            response['topics'],
            [])

    def test_board_show_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.boards import board_show
        from . import mock_service
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            board_show(request)

    def test_board_all(self):
        from datetime import datetime, timedelta
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.boards import board_all
        from . import mock_service

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
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board1.slug
        response = board_all(request)
        self.assertEqual(response['board'], board1)
        self.assertEqual(
            response['topics'],
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

    def test_board_all_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.boards import board_all
        from . import mock_service
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            board_all(request)

    def test_board_new_get(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.boards import board_new_get
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        response = board_new_get(request)
        self.assertEqual(
            response['board'],
            board)

    def test_board_new_get_restricted(self):
        from pyramid.httpexceptions import HTTPForbidden
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.boards import board_new_get
        from . import mock_service
        board = self._make(Board(
            title='Foobar',
            slug='foobar',
            status='restricted'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        with self.assertRaises(HTTPForbidden):
            board_new_get(request)

    def test_board_new_get_locked(self):
        from pyramid.httpexceptions import HTTPForbidden
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.boards import board_new_get
        from . import mock_service
        board = self._make(Board(
            title='Foobar',
            slug='foobar',
            status='locked'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        with self.assertRaises(HTTPForbidden):
            board_new_get(request)

    def test_board_new_get_archived(self):
        from pyramid.httpexceptions import HTTPForbidden
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.boards import board_new_get
        from . import mock_service
        board = self._make(Board(
            title='Foobar',
            slug='foobar',
            status='archived'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        with self.assertRaises(HTTPForbidden):
            board_new_get(request)

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_board_new_get_task(self, result_):
        from ..interfaces import IBoardQueryService, ITaskQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TaskQueryService
        from ..views.boards import board_new_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['topic', topic.id])
        request = mock_service(self.request, {
            'db': self.dbsession,
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        self.config.add_route('topic', '/{board}/{topic}')
        response = board_new_get(request)
        self.assertEqual(
            response.location,
            '/%s/%s' % (board.slug, topic.id))
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_board_new_get_task_wait(self, result_):
        from ..interfaces import IBoardQueryService, ITaskQueryService
        from ..models import Board
        from ..services import BoardQueryService, TaskQueryService
        from ..views.boards import board_new_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult('dummy', 'pending')
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('boards/new_wait.mako')
        board_new_get(request)
        renderer.assert_(
            request=request,
            board=board)
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_board_new_get_task_akismet_rejected(self, result_):
        from ..interfaces import IBoardQueryService, ITaskQueryService
        from ..models import Board
        from ..services import BoardQueryService, TaskQueryService
        from ..views.boards import board_new_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['failure', 'akismet_rejected'])
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('boards/new_error.mako')
        board_new_get(request)
        renderer.assert_(
            request=request,
            board=board,
            name='akismet_rejected')
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_board_new_get_task_dnsbl_rejected(self, result_):
        from ..interfaces import IBoardQueryService, ITaskQueryService
        from ..models import Board
        from ..services import BoardQueryService, TaskQueryService
        from ..views.boards import board_new_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['failure', 'dnsbl_rejected'])
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('boards/new_error.mako')
        board_new_get(request)
        renderer.assert_(
            request=request,
            board=board,
            name='dnsbl_rejected')
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_board_new_get_task_ban_rejected(self, result_):
        from ..interfaces import IBoardQueryService, ITaskQueryService
        from ..models import Board
        from ..services import BoardQueryService, TaskQueryService
        from ..views.boards import board_new_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['failure', 'ban_rejected'])
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('boards/new_error.mako')
        board_new_get(request)
        renderer.assert_(
            request=request,
            board=board,
            name='ban_rejected')
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_board_new_get_task_status_rejected(self, result_):
        from ..interfaces import IBoardQueryService, ITaskQueryService
        from ..models import Board
        from ..services import BoardQueryService, TaskQueryService
        from ..views.boards import board_new_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['failure', 'status_rejected', 'test'])
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('boards/new_error.mako')
        board_new_get(request)
        renderer.assert_(
            request=request,
            board=board,
            status='test',
            name='status_rejected')
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_board_new_get_task_proxy_rejected(self, result_):
        from ..interfaces import IBoardQueryService, ITaskQueryService
        from ..models import Board
        from ..services import BoardQueryService, TaskQueryService
        from ..views.boards import board_new_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['failure', 'proxy_rejected'])
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('boards/new_error.mako')
        board_new_get(request)
        renderer.assert_(
            request=request,
            board=board,
            name='proxy_rejected')
        result_.assert_called_with('dummy')

    def test_board_new_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.boards import board_new_get
        from . import mock_service
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            board_new_get(request)

    @unittest.mock.patch('fanboi2.tasks.topic.add_topic.delay')
    def test_board_new_post(self, add_):
        from ..interfaces import IBoardQueryService, ITopicCreateService
        from ..interfaces import IRateLimiterService, IRuleBanQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicCreateService
        from ..services import IdentityService, SettingQueryService
        from ..services import RateLimiterService, RuleBanQueryService
        from ..views.boards import board_new_post
        from . import mock_service, make_cache_region, DummyRedis
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IRateLimiterService: rate_limiter_svc,
            IRuleBanQueryService: RuleBanQueryService(self.dbsession),
            ITopicCreateService: TopicCreateService(
                self.dbsession,
                IdentityService(redis_conn, 10),
                SettingQueryService(self.dbsession, cache_region))})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['title'] = 'title'
        request.POST['body'] = 'bodyb'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('board_new', '/{board}/new')
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            0)
        add_.return_value = unittest.mock.Mock(id='task-uuid')
        response = board_new_post(request)
        self.assertEqual(response.location, '/foo/new?task=task-uuid')
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            10)
        add_.assert_called_with(
            'foo',
            'title',
            'bodyb',
            '127.0.0.1',
            payload={
                'application_url': request.application_url,
                'referrer': request.referrer,
                'url': request.url,
                'user_agent': request.user_agent,
            })

    def test_board_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.boards import board_new_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['title'] = 'title'
        request.POST['body'] = 'bodyb'
        with self.assertRaises(BadCSRFToken):
            board_new_post(request)

    def test_board_new_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.boards import board_new_post
        from . import mock_service
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = 'notexists'
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['csrf_token'] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_new_post(request)

    def test_board_new_post_invalid_title(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService
        from ..views.boards import board_new_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['title'] = 'titl'
        request.POST['body'] = 'bodyb'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = board_new_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)
        self.assertEqual(response['form'].title.data, 'titl')
        self.assertEqual(response['form'].body.data, 'bodyb')
        self.assertDictEqual(response['form'].errors, {
            'title': ['Field must be between 5 and 200 characters long.']
        })

    def test_board_new_post_invalid_body(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService
        from ..views.boards import board_new_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['title'] = 'title'
        request.POST['body'] = 'body'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = board_new_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)
        self.assertEqual(response['form'].title.data, 'title')
        self.assertEqual(response['form'].body.data, 'body')
        self.assertDictEqual(response['form'].errors, {
            'body': ['Field must be between 5 and 4000 characters long.']
        })

    def test_board_new_post_banned(self):
        from ..interfaces import IBoardQueryService
        from ..interfaces import IRuleBanQueryService
        from ..models import Board, Topic, RuleBan
        from ..services import BoardQueryService, RuleBanQueryService
        from ..views.boards import board_new_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foo'))
        self._make(RuleBan(ip_address='127.0.0.0/24', scope='board:foo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.client_addr = '127.0.0.1'
        request.POST = MultiDict({})
        request.POST['title'] = 'title'
        request.POST['body'] = 'bodyb'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        renderer = self.config.testing_add_renderer('boards/new_error.mako')
        board_new_post(request)
        renderer.assert_(
            request=request,
            board=board,
            name='ban_rejected')
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_new_post_banned_unscoped(self):
        from ..interfaces import IBoardQueryService
        from ..interfaces import IRuleBanQueryService
        from ..models import Board, Topic, RuleBan
        from ..services import BoardQueryService, RuleBanQueryService
        from ..views.boards import board_new_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foo'))
        self._make(RuleBan(ip_address='127.0.0.0/24'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.client_addr = '127.0.0.1'
        request.POST = MultiDict({})
        request.POST['title'] = 'title'
        request.POST['body'] = 'bodyb'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        renderer = self.config.testing_add_renderer('boards/new_error.mako')
        board_new_post(request)
        renderer.assert_(
            request=request,
            board=board,
            name='ban_rejected')
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_new_post_rate_limited(self):
        from ..interfaces import IBoardQueryService
        from ..interfaces import IRateLimiterService, IRuleBanQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService
        from ..services import RateLimiterService, RuleBanQueryService
        from ..views.boards import board_new_post
        from . import mock_service, DummyRedis
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IRateLimiterService: rate_limiter_svc,
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['title'] = 'title'
        request.POST['body'] = 'bodyb'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        renderer = self.config.testing_add_renderer('boards/new_error.mako')
        rate_limiter_svc.limit_for(
            10,
            ip_address=request.client_addr,
            board=board.slug)
        board_new_post(request)
        renderer.assert_(
            request=request,
            board=board,
            name='rate_limited',
            time_left=10)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_topic_show_get(self):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import IPostQueryService
        from ..models import Board, Topic, Post
        from ..services import BoardQueryService, TopicQueryService
        from ..services import PostQueryService
        from ..views.boards import topic_show_get
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic1 = self._make(Topic(board=board, title='Demo'))
        topic2 = self._make(Topic(board=board, title='Demo 2'))
        post1 = self._make(Post(
            topic=topic1,
            number=1,
            name='Nameless Fanboi',
            body='Lorem ipsum',
            ip_address='127.0.0.1'))
        post2 = self._make(Post(
            topic=topic1,
            number=2,
            name='Nameless Fanboi',
            body='Dolor sit',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Fanboi',
            body='Foobar',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            IPostQueryService: PostQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic1.id
        response = topic_show_get(request)
        self.assertEqual(response['board'], board)
        self.assertEqual(response['topic'], topic1)
        self.assertEqual(response['posts'], [post1, post2])

    def test_topic_show_get_query(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import IPostQueryService
        from ..models import Board, Topic, Post
        from ..services import BoardQueryService, TopicQueryService
        from ..services import PostQueryService
        from ..views.boards import topic_show_get
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic1 = self._make(Topic(board=board, title='Demo'))
        topic2 = self._make(Topic(board=board, title='Demo 2'))
        posts = []
        for i in range(50):
            posts.append(self._make(Post(
                topic=topic1,
                number=i + 1,
                name='Nameless Fanboi',
                body='Lorem ipsum',
                ip_address='127.0.0.1')))
        self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Fanboi',
            body='Foobar',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            IPostQueryService: PostQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic1.id
        request.matchdict['query'] = '1'
        response = topic_show_get(request)
        self.assertEqual(response['board'], board)
        self.assertEqual(response['topic'], topic1)
        self.assertEqual(response['posts'], posts[0:1])
        request.matchdict['query'] = '50'
        response = topic_show_get(request)
        self.assertEqual(response['posts'], posts[49:50])
        request.matchdict['query'] = '51'
        with self.assertRaises(HTTPNotFound):
            topic_show_get(request)
        request.matchdict['query'] = '1-50'
        response = topic_show_get(request)
        self.assertEqual(response['posts'], posts)
        request.matchdict['query'] = '10-20'
        response = topic_show_get(request)
        self.assertEqual(response['posts'], posts[9:20])
        request.matchdict['query'] = '51-99'
        with self.assertRaises(HTTPNotFound):
            topic_show_get(request)
        request.matchdict['query'] = '0-51'
        response = topic_show_get(request)
        self.assertEqual(response['posts'], posts)
        request.matchdict['query'] = '-0'
        with self.assertRaises(HTTPNotFound):
            topic_show_get(request)
        request.matchdict['query'] = '-5'
        response = topic_show_get(request)
        self.assertEqual(response['posts'], posts[:5])
        request.matchdict['query'] = '45-'
        response = topic_show_get(request)
        self.assertEqual(response['posts'], posts[44:])
        request.matchdict['query'] = '100-'
        with self.assertRaises(HTTPNotFound):
            topic_show_get(request)
        request.matchdict['query'] = 'recent'
        response = topic_show_get(request)
        self.assertEqual(response['posts'], posts[20:])
        request.matchdict['query'] = 'l30'
        response = topic_show_get(request)
        self.assertEqual(response['posts'], posts[20:])

    def test_topic_show_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import IPostQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..services import PostQueryService
        from ..views.boards import topic_show_get
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            IPostQueryService: PostQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = '-1'
        with self.assertRaises(NoResultFound):
            topic_show_get(request)

    def test_topic_show_get_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import IPostQueryService
        from ..services import BoardQueryService, TopicQueryService
        from ..services import PostQueryService
        from ..views.boards import topic_show_get
        from . import mock_service
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            IPostQueryService: PostQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = 'notexists'
        request.matchdict['topic'] = '-1'
        with self.assertRaises(NoResultFound):
            topic_show_get(request)

    def test_topic_show_get_wrong_board(self):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import IPostQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..services import PostQueryService
        from ..views.boards import topic_show_get
        from . import mock_service
        board1 = self._make(Board(title='Foobar', slug='foobar'))
        board2 = self._make(Board(title='Foobaz', slug='foobaz'))
        topic = self._make(Topic(board=board1, title='Foobar'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            IPostQueryService: PostQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board2.slug
        request.matchdict['topic'] = topic.id
        self.config.add_route('topic', '/{board}/{topic}')
        response = topic_show_get(request)
        self.assertEqual(
            response.location,
            '/%s/%s' % (board1.slug, topic.id))

    def test_topic_show_get_wrong_board_query(self):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import IPostQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..services import PostQueryService
        from ..views.boards import topic_show_get
        from . import mock_service
        board1 = self._make(Board(title='Foobar', slug='foobar'))
        board2 = self._make(Board(title='Foobaz', slug='foobaz'))
        topic = self._make(Topic(board=board1, title='Foobar'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            IPostQueryService: PostQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = board2.slug
        request.matchdict['topic'] = topic.id
        request.matchdict['query'] = 'l10'
        self.config.add_route('topic_scoped', '/{board}/{topic}/{query}')
        response = topic_show_get(request)
        self.assertEqual(
            response.location,
            '/%s/%s/l10' % (board1.slug, topic.id))

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_topic_show_get_task(self, result_):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import ITaskQueryService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import BoardQueryService, TopicQueryService
        from ..services import TaskQueryService
        from ..views.boards import topic_show_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=1))
        post = self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Fanboi',
            body='Hello',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['post', post.id])
        request = mock_service(self.request, {
            'db': self.dbsession,
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        self.config.add_route('topic_scoped', '/{board}/{topic}/{query}')
        response = topic_show_get(request)
        self.assertEqual(
            response.location,
            '/%s/%s/l10' % (board.slug, topic.id))
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_topic_show_get_task_wait(self, result_):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import ITaskQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services import BoardQueryService, TopicQueryService
        from ..services import TaskQueryService
        from ..views.boards import topic_show_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult('dummy', 'pending')
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('topics/show_wait.mako')
        topic_show_get(request)
        renderer.assert_(
            request=request,
            board=board,
            topic=topic)
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_topic_show_get_task_akismet_rejected(self, result_):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import ITaskQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services import BoardQueryService, TopicQueryService
        from ..services import TaskQueryService
        from ..views.boards import topic_show_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['failure', 'akismet_rejected'])
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('topics/show_error.mako')
        topic_show_get(request)
        renderer.assert_(
            request=request,
            board=board,
            topic=topic,
            name='akismet_rejected')
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_topic_show_get_task_dnsbl_rejected(self, result_):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import ITaskQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services import BoardQueryService, TopicQueryService
        from ..services import TaskQueryService
        from ..views.boards import topic_show_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['failure', 'dnsbl_rejected'])
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('topics/show_error.mako')
        topic_show_get(request)
        renderer.assert_(
            request=request,
            board=board,
            topic=topic,
            name='dnsbl_rejected')
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_topic_show_get_task_ban_rejected(self, result_):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import ITaskQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services import BoardQueryService, TopicQueryService
        from ..services import TaskQueryService
        from ..views.boards import topic_show_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['failure', 'ban_rejected'])
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('topics/show_error.mako')
        topic_show_get(request)
        renderer.assert_(
            request=request,
            board=board,
            topic=topic,
            name='ban_rejected')
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_topic_show_get_task_status_rejected(self, result_):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import ITaskQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services import BoardQueryService, TopicQueryService
        from ..services import TaskQueryService
        from ..views.boards import topic_show_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['failure', 'status_rejected', 'test'])
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('topics/show_error.mako')
        topic_show_get(request)
        renderer.assert_(
            request=request,
            board=board,
            topic=topic,
            status='test',
            name='status_rejected')
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_topic_show_get_task_proxy_rejected(self, result_):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import ITaskQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services import BoardQueryService, TopicQueryService
        from ..services import TaskQueryService
        from ..views.boards import topic_show_get
        from . import mock_service, DummyAsyncResult
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['failure', 'proxy_rejected', 'test'])
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            ITaskQueryService: TaskQueryService()})
        request.method = 'GET'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.GET = MultiDict({})
        request.GET['task'] = 'dummy'
        renderer = self.config.testing_add_renderer('topics/show_error.mako')
        topic_show_get(request)
        renderer.assert_(
            request=request,
            board=board,
            topic=topic,
            name='proxy_rejected')
        result_.assert_called_with('dummy')

    @unittest.mock.patch('fanboi2.tasks.post.add_post.delay')
    def test_topic_show_post(self, add_):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..interfaces import IPostCreateService
        from ..interfaces import IRateLimiterService, IRuleBanQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services import BoardQueryService, TopicQueryService
        from ..services import IdentityService, SettingQueryService
        from ..services import PostCreateService
        from ..services import RateLimiterService, RuleBanQueryService
        from ..views.boards import topic_show_post
        from . import mock_service, make_cache_region, DummyRedis
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            IRateLimiterService: rate_limiter_svc,
            IRuleBanQueryService: RuleBanQueryService(self.dbsession),
            IPostCreateService: PostCreateService(
                self.dbsession,
                IdentityService(redis_conn, 10),
                SettingQueryService(self.dbsession, cache_region))})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['body'] = 'bodyb'
        request.POST['bumped'] = True
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            0)
        add_.return_value = unittest.mock.Mock(id='task-uuid')
        self.config.add_route('topic', '/{board}/{topic}')
        response = topic_show_post(request)
        self.assertEqual(
            response.location,
            '/%s/%s?task=task-uuid' % (board.slug, topic.id))
        self.assertEqual(rate_limiter_svc.time_left(
                ip_address=request.client_addr,
                board=board.slug),
            10)
        add_.assert_called_with(
            topic.id,
            'bodyb',
            True,
            '127.0.0.1',
            payload={
                'application_url': request.application_url,
                'referrer': request.referrer,
                'url': request.url,
                'user_agent': request.user_agent,
            })

    def test_topic_show_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services import BoardQueryService, TopicQueryService
        from ..views.boards import topic_show_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['body'] = 'bodyb'
        request.POST['bumped'] = True
        with self.assertRaises(BadCSRFToken):
            topic_show_post(request)

    def test_topic_show_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.boards import topic_show_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = '-1'
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['csrf_token'] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            topic_show_post(request)

    def test_topic_show_post_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..services import BoardQueryService, TopicQueryService
        from ..views.boards import topic_show_post
        from . import mock_service
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = 'notexists'
        request.matchdict['topic'] = '-1'
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['csrf_token'] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            topic_show_post(request)

    def test_topic_show_post_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.boards import topic_show_post
        from . import mock_service
        board1 = self._make(Board(title='Foobar', slug='foobar'))
        board2 = self._make(Board(title='Foobaz', slug='foobaz'))
        topic = self._make(Topic(board=board1, title='Foobar'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board2.slug
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['csrf_token'] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            topic_show_post(request)

    def test_topic_show_post_invalid_body(self):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import BoardQueryService, TopicQueryService
        from ..views.boards import topic_show_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['body'] = 'body'
        request.POST['bumped'] = True
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = topic_show_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)
        self.assertEqual(response['form'].body.data, 'body')
        self.assertEqual(response['form'].bumped.data, True)
        self.assertDictEqual(response['form'].errors, {
            'body': ['Field must be between 5 and 4000 characters long.']
        })

    def test_topic_show_post_banned(self):
        from ..interfaces import IRuleBanQueryService
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic, TopicMeta, Post, RuleBan
        from ..services import RuleBanQueryService
        from ..services import BoardQueryService, TopicQueryService
        from ..views.boards import topic_show_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self._make(RuleBan(ip_address='127.0.0.0/24', scope='board:foobar'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/x-www-form-urlencoded'
        request.client_addr = '127.0.0.1'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['body'] = 'bodyb'
        request.POST['bumped'] = True
        request.POST['csrf_token'] = request.session.get_csrf_token()
        renderer = self.config.testing_add_renderer('topics/show_error.mako')
        topic_show_post(request)
        renderer.assert_(
            request=request,
            board=board,
            topic=topic,
            name='ban_rejected')
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_topic_show_post_banned_unscoped(self):
        from ..interfaces import IRuleBanQueryService
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic, TopicMeta, Post, RuleBan
        from ..services import RuleBanQueryService
        from ..services import BoardQueryService, TopicQueryService
        from ..views.boards import topic_show_post
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self._make(RuleBan(ip_address='127.0.0.0/24'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/x-www-form-urlencoded'
        request.client_addr = '127.0.0.1'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['body'] = 'bodyb'
        request.POST['bumped'] = True
        request.POST['csrf_token'] = request.session.get_csrf_token()
        renderer = self.config.testing_add_renderer('topics/show_error.mako')
        topic_show_post(request)
        renderer.assert_(
            request=request,
            board=board,
            topic=topic,
            name='ban_rejected')
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_topic_show_post_rate_limited(self):
        from ..interfaces import IRateLimiterService, IRuleBanQueryService
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import RateLimiterService, RuleBanQueryService
        from ..services import BoardQueryService, TopicQueryService
        from ..views.boards import topic_show_post
        from . import mock_service, DummyRedis
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            ITopicQueryService: TopicQueryService(self.dbsession),
            IRateLimiterService: rate_limiter_svc,
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['body'] = 'bodyb'
        request.POST['bumped'] = True
        request.POST['csrf_token'] = request.session.get_csrf_token()
        renderer = self.config.testing_add_renderer('topics/show_error.mako')
        rate_limiter_svc.limit_for(
            10,
            ip_address=request.client_addr,
            board=board.slug)
        topic_show_post(request)
        renderer.assert_(
            request=request,
            board=board,
            topic=topic,
            name='rate_limited',
            time_left=10)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_error_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..views.boards import error_not_found
        self.config.testing_add_renderer('not_found.mako')
        response = error_not_found(HTTPNotFound(), self.request)
        self.assertEqual(response.status, '404 Not Found')

    def test_error_bad_request(self):
        from pyramid.httpexceptions import HTTPBadRequest
        from ..views.boards import error_bad_request
        self.config.testing_add_renderer('bad_request.mako')
        response = error_bad_request(HTTPBadRequest(), self.request)
        self.assertEqual(response.status, '400 Bad Request')


class TestIntegrationPage(ModelSessionMixin, unittest.TestCase):

    def setUp(self):
        super(TestIntegrationPage, self).setUp()
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry
        self.request.user_agent = 'Mock/1.0'
        self.request.client_addr = '127.0.0.1'
        self.request.referrer = 'https://www.example.com/referer'
        self.request.url = 'https://www.example.com/url'
        self.request.application_url = 'https://www.example.com'

    def tearDown(self):
        super(TestIntegrationPage, self).tearDown()
        testing.tearDown()

    def test_page_show(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.pages import page_show
        from . import mock_service
        page = self._make(Page(title='Foo', body='Foo', slug='foo'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = page.slug
        response = page_show(request)
        self.assertEqual(
            response['page'],
            page)

    def test_page_show_internal(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.pages import page_show
        from . import mock_service
        page = self._make(Page(
            title='Foo',
            body='Foo',
            slug='foo',
            namespace='internal'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = page.slug
        with self.assertRaises(NoResultFound):
            page_show(request)

    def test_page_show_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.pages import page_show
        from . import mock_service
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'notexists'
        with self.assertRaises(NoResultFound):
            page_show(request)

    def test_page_robots(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.pages import robots_show
        from . import mock_service
        self._make(Page(
            title='Robots',
            slug='global/robots',
            namespace='internal',
            body='Hi'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        self.assertEqual(
            robots_show(request).body,
            b'Hi')

    def test_page_robots_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.pages import robots_show
        from . import mock_service
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        with self.assertRaises(NoResultFound):
            robots_show(request)


class TestIntegrationAdmin(ModelSessionMixin, unittest.TestCase):

    def setUp(self):
        super(TestIntegrationAdmin, self).setUp()
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry
        self.request.user_agent = 'Mock/1.0'
        self.request.client_addr = '127.0.0.1'
        self.request.referrer = 'https://www.example.com/referer'
        self.request.url = 'https://www.example.com/url'
        self.request.application_url = 'https://www.example.com'

    def tearDown(self):
        super(TestIntegrationAdmin, self).tearDown()
        testing.tearDown()

    def test_login_get(self):
        from ..forms import AdminLoginForm
        from ..interfaces import ISettingQueryService
        from ..views.admin import login_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {'setup.version': '0.30.0'}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'GET'
        response = login_get(request)
        self.assertIsInstance(response['form'], AdminLoginForm)

    def test_login_get_not_installed(self):
        from ..interfaces import ISettingQueryService
        from ..views.admin import login_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'GET'
        self.config.add_route('admin_setup', '/setup')
        response = login_get(request)
        self.assertEqual(
            response.location,
            '/setup')

    def test_login_post(self):
        from pyramid.authentication import AuthTktAuthenticationPolicy
        from pyramid.authorization import ACLAuthorizationPolicy
        from passlib.hash import argon2
        from ..interfaces import IUserLoginService
        from ..models import User, UserSession
        from ..services import UserLoginService
        from ..views.admin import login_post
        from . import mock_service
        self._make(User(
            username='foo',
            encrypted_password=argon2.hash('passw0rd')))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IUserLoginService: UserLoginService(self.dbsession)})
        request.method = 'POST'
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['username'] = 'foo'
        request.POST['password'] = 'passw0rd'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        authn_policy = AuthTktAuthenticationPolicy('foo')
        authz_policy = ACLAuthorizationPolicy()
        self.config.set_authorization_policy(authz_policy)
        self.config.set_authentication_policy(authn_policy)
        self.config.add_route('admin_root', '/admin')
        response = login_post(request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 1)
        self.assertEqual(response.location, '/admin')
        self.assertIn('Set-Cookie', response.headers)

    def test_login_post_wrong_password(self):
        from passlib.hash import argon2
        from ..forms import AdminLoginForm
        from ..interfaces import IUserLoginService
        from ..models import User, UserSession
        from ..services import UserLoginService
        from ..views.admin import login_post
        from . import mock_service
        self._make(User(
            username='foo',
            encrypted_password=argon2.hash('passw0rd')))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IUserLoginService: UserLoginService(self.dbsession)})
        request.method = 'POST'
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['username'] = 'foo'
        request.POST['password'] = 'password'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = login_post(request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertIsInstance(response['form'], AdminLoginForm)
        self.assertEqual(
            request.session.pop_flash(queue='error'),
            ['Username or password is invalid.'])

    def test_login_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..models import UserSession
        from ..views.admin import login_post
        self.request.method = 'POST'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.session = testing.DummySession()
        self.request.POST = MultiDict({})
        self.request.POST['username'] = 'foo'
        self.request.POST['password'] = 'passw0rd'
        with self.assertRaises(BadCSRFToken):
            login_post(self.request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)

    def test_login_post_not_found(self):
        from ..forms import AdminLoginForm
        from ..interfaces import IUserLoginService
        from ..models import UserSession
        from ..services import UserLoginService
        from ..views.admin import login_post
        from . import mock_service
        request = mock_service(self.request, {
            IUserLoginService: UserLoginService(self.dbsession)})
        request.method = 'POST'
        request.content_type = 'application/x-www-form-urlencoded'
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST['username'] = 'foo'
        request.POST['password'] = 'passw0rd'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = login_post(request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertIsInstance(response['form'], AdminLoginForm)
        self.assertEqual(
            request.session.pop_flash(queue='error'),
            ['Username or password is invalid.'])

    def test_login_post_invalid_username(self):
        from ..models import UserSession
        from ..views.admin import login_post
        self.request.method = 'POST'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.session = testing.DummySession()
        self.request.POST = MultiDict({})
        self.request.POST['username'] = ''
        self.request.POST['password'] = 'passw0rd'
        self.request.POST['csrf_token'] = self.request.session.get_csrf_token()
        response = login_post(self.request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertEqual(response['form'].username.data, '')
        self.assertEqual(response['form'].password.data, 'passw0rd')
        self.assertDictEqual(response['form'].errors, {
            'username': ['This field is required.']})

    def test_login_post_invalid_password(self):
        from ..models import UserSession
        from ..views.admin import login_post
        self.request.method = 'POST'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.session = testing.DummySession()
        self.request.POST = MultiDict({})
        self.request.POST['username'] = 'foo'
        self.request.POST['password'] = ''
        self.request.POST['csrf_token'] = self.request.session.get_csrf_token()
        response = login_post(self.request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertEqual(response['form'].username.data, 'foo')
        self.assertEqual(response['form'].password.data, '')
        self.assertDictEqual(response['form'].errors, {
            'password': ['This field is required.']})

    def test_setup_get(self):
        from ..forms import AdminSetupForm
        from ..interfaces import ISettingQueryService
        from ..views.admin import setup_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'GET'
        response = setup_get(request)
        self.assertIsInstance(response['form'], AdminSetupForm)

    def test_setup_get_already_setup(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import ISettingQueryService
        from ..views.admin import setup_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {'setup.version': '0.30.0'}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'GET'
        with self.assertRaises(HTTPNotFound):
            setup_get(request)

    def test_setup_post(self):
        from ..interfaces import ISettingQueryService, ISettingUpdateService
        from ..interfaces import IUserCreateService
        from ..models import User, UserSession
        from ..services import SettingQueryService, SettingUpdateService
        from ..services import UserCreateService
        from ..version import __VERSION__
        from ..views.admin import setup_post
        from . import mock_service, make_cache_region
        cache_region = make_cache_region()
        setting_query_svc = SettingQueryService(self.dbsession, cache_region)
        request = mock_service(self.request, {
            IUserCreateService: UserCreateService(self.dbsession),
            ISettingQueryService: setting_query_svc,
            ISettingUpdateService: SettingUpdateService(
                self.dbsession,
                cache_region)})
        self.assertIsNone(setting_query_svc.value_from_key('setup.version'))
        request.method = 'POST'
        request.POST = MultiDict({})
        request.POST['username'] = 'root'
        request.POST['password'] = 'passw0rd'
        request.POST['password_confirm'] = 'passw0rd'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_root', '/admin')
        response = setup_post(request)
        user = self.dbsession.query(User).one()
        self.assertEqual(user.username, 'root')
        self.assertNotEqual(user.encrypted_password, 'passw0rd')
        self.assertIsNone(user.parent)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertEqual(
            setting_query_svc.value_from_key('setup.version'),
            __VERSION__)
        self.assertEqual(response.location, '/admin')
        self.assertEqual(
            request.session.pop_flash(queue='success'),
            ['Successfully setup initial user.'])

    def test_setup_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'POST'
        request.POST = MultiDict({})
        request.POST['username'] = 'root'
        request.POST['password'] = 'passw0rd'
        request.POST['password_confirm'] = 'passw0rd'
        with self.assertRaises(BadCSRFToken):
            setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)

    def test_setup_post_already_setup(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {'setup.version': '0.30.0'}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'POST'
        request.POST = MultiDict({})
        with self.assertRaises(HTTPNotFound):
            setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)

    def test_setup_post_invalid_username(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'POST'
        request.POST = MultiDict({})
        request.POST['username'] = ''
        request.POST['password'] = 'passw0rd'
        request.POST['password_confirm'] = 'passw0rd'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response['form'].username.data, '')
        self.assertEqual(response['form'].password.data, 'passw0rd')
        self.assertEqual(response['form'].password_confirm.data, 'passw0rd')
        self.assertDictEqual(response['form'].errors, {
            'username': ['This field is required.']})

    def test_setup_post_invalid_password(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'POST'
        request.POST = MultiDict({})
        request.POST['username'] = 'root'
        request.POST['password'] = ''
        request.POST['password_confirm'] = 'passw0rd'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response['form'].username.data, 'root')
        self.assertEqual(response['form'].password.data, '')
        self.assertEqual(response['form'].password_confirm.data, 'passw0rd')
        self.assertDictEqual(response['form'].errors, {
            'password': ['This field is required.'],
            'password_confirm': ['Password must match.']})

    def test_setup_post_invalid_password_shorter(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'POST'
        request.POST = MultiDict({})
        request.POST['username'] = 'root'
        request.POST['password'] = 'passw0r'
        request.POST['password_confirm'] = 'passw0r'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response['form'].username.data, 'root')
        self.assertEqual(response['form'].password.data, 'passw0r')
        self.assertEqual(response['form'].password_confirm.data, 'passw0r')
        self.assertDictEqual(response['form'].errors, {
            'password': ['Field must be between 8 and 64 characters long.']})

    def test_setup_post_invalid_password_longer(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key):
                return {}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'POST'
        request.POST = MultiDict({})
        request.POST['username'] = 'root'
        request.POST['password'] = 'p' * 65
        request.POST['password_confirm'] = 'p' * 65
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response['form'].username.data, 'root')
        self.assertEqual(response['form'].password.data, 'p' * 65)
        self.assertEqual(response['form'].password_confirm.data, 'p' * 65)
        self.assertDictEqual(response['form'].errors, {
            'password': ['Field must be between 8 and 64 characters long.']})
