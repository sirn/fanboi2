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
            def value_from_key(self, key, **kwargs):
                return {'setup.version': '0.30.0'}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'GET'
        response = login_get(request)
        self.assertIsInstance(response['form'], AdminLoginForm)

    def test_login_get_logged_in(self):
        from ..views.admin import login_get
        self.request.method = 'GET'
        self.config.testing_securitypolicy(userid='foo')
        self.config.add_route('admin_dashboard', '/admin/dashboard')
        response = login_get(self.request)
        self.assertEqual(response.location, '/admin/dashboard')

    def test_login_get_not_installed(self):
        from ..interfaces import ISettingQueryService
        from ..views.admin import login_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
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
        self.config.testing_securitypolicy(
            userid=None,
            remember_result=[('Set-Cookie', 'foobar')])
        self.config.add_route('admin_dashboard', '/admin/dashboard')
        response = login_post(request)
        self.assertEqual(response.location, '/admin/dashboard')
        self.assertEqual(self.dbsession.query(UserSession).count(), 1)
        self.assertIn('Set-Cookie', response.headers)

    def test_login_post_logged_in(self):
        from pyramid.httpexceptions import HTTPForbidden
        from ..views.admin import login_post
        self.request.method = 'POST'
        self.config.testing_securitypolicy(userid='foo')
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST['username'] = 'foo'
        self.request.POST['password'] = 'password'
        self.request.POST['csrf_token'] = self.request.session.get_csrf_token()
        with self.assertRaises(HTTPForbidden):
            login_post(self.request)

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

    def test_login_post_deactivated(self):
        from passlib.hash import argon2
        from ..forms import AdminLoginForm
        from ..interfaces import IUserLoginService
        from ..models import User, UserSession
        from ..services import UserLoginService
        from ..views.admin import login_post
        from . import mock_service
        self._make(User(
            username='foo',
            encrypted_password=argon2.hash('passw0rd'),
            deactivated=True))
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
        response = login_post(request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertIsInstance(response['form'], AdminLoginForm)
        self.assertEqual(
            request.session.pop_flash(queue='error'),
            ['Username or password is invalid.'])

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

    def test_logout_get(self):
        from ..interfaces import IUserLoginService
        from ..models import User, UserSession
        from ..services import UserLoginService
        from ..views.admin import logout_get
        from . import mock_service
        user = self._make(User(
            username='foo',
            encrypted_password='none'))
        user_session = self._make(UserSession(
            user=user,
            token='foo_token1',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IUserLoginService: UserLoginService(self.dbsession)})
        request.method = 'GET'
        request.client_addr = '127.0.0.1'
        self.config.testing_securitypolicy(
            userid='foo_token1',
            forget_result=[('Set-Cookie', 'foobar')])
        self.config.add_route('admin_root', '/admin')
        self.assertIsNone(user_session.revoked_at)
        response = logout_get(request)
        self.assertEqual(response.location, '/admin')
        self.assertIn('Set-Cookie', response.headers)
        self.assertIsNotNone(user_session.revoked_at)

    def test_logout_get_not_logged_in(self):
        from ..views.admin import logout_get
        self.request.method = 'GET'
        self.request.client_addr = '127.0.0.1'
        self.config.testing_securitypolicy(userid=None)
        self.config.add_route('admin_root', '/admin')
        response = logout_get(self.request)
        self.assertEqual(response.location, '/admin')

    def test_setup_get(self):
        from ..forms import AdminSetupForm
        from ..interfaces import ISettingQueryService
        from ..views.admin import setup_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
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
            def value_from_key(self, key, **kwargs):
                return {'setup.version': '0.30.0'}.get(key, None)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'GET'
        with self.assertRaises(HTTPNotFound):
            setup_get(request)

    def test_setup_post(self):
        from ..interfaces import ISettingQueryService, ISettingUpdateService
        from ..interfaces import IUserCreateService
        from ..models import User, UserSession, Group
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
        group = self.dbsession.query(Group).one()
        self.assertEqual(response.location, '/admin')
        self.assertEqual(user.username, 'root')
        self.assertEqual(user.groups, [group])
        self.assertNotEqual(user.encrypted_password, 'passw0rd')
        self.assertIsNone(user.parent)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertEqual(
            setting_query_svc.value_from_key('setup.version'),
            __VERSION__)
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
            def value_from_key(self, key, **kwargs):
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
            def value_from_key(self, key, **kwargs):
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
            def value_from_key(self, key, **kwargs):
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
            def value_from_key(self, key, **kwargs):
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
            def value_from_key(self, key, **kwargs):
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
            def value_from_key(self, key, **kwargs):
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

    def test_dashboard_get(self):
        from ..views.admin import dashboard_get
        self.request.method = 'GET'
        response = dashboard_get(self.request)
        self.assertEqual(response, {})

    def test_bans_get(self):
        from datetime import datetime, timedelta
        from ..interfaces import IRuleBanQueryService
        from ..models import RuleBan
        from ..services import RuleBanQueryService
        from ..views.admin import bans_get
        from . import mock_service
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
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'GET'
        response = bans_get(request)
        self.assertEqual(
            response['bans'],
            [rule_ban6, rule_ban3, rule_ban5, rule_ban1])

    def test_bans_inactive_get(self):
        from datetime import datetime, timedelta
        from ..interfaces import IRuleBanQueryService
        from ..models import RuleBan
        from ..services import RuleBanQueryService
        from ..views.admin import bans_inactive_get
        from . import mock_service
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
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'GET'
        response = bans_inactive_get(request)
        self.assertEqual(
            response['bans'],
            [rule_ban6, rule_ban4, rule_ban2, rule_ban5])

    def test_ban_new_get(self):
        from ..forms import AdminRuleBanForm
        from ..views.admin import ban_new_get
        self.request.method = 'GET'
        response = ban_new_get(self.request)
        self.assertIsInstance(response['form'], AdminRuleBanForm)

    def test_ban_new_post(self):
        import pytz
        from datetime import datetime, timedelta
        from ..interfaces import IRuleBanCreateService
        from ..models import RuleBan
        from ..services import RuleBanCreateService
        from ..views.admin import ban_new_post
        from . import mock_service
        request = mock_service(self.request, {
            'db': self.dbsession,
            IRuleBanCreateService: RuleBanCreateService(self.dbsession)})
        request.method = 'POST'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['ip_address'] = '10.0.1.0/24'
        request.POST['description'] = 'Violation of galactic law'
        request.POST['duration'] = '30'
        request.POST['scope'] = 'galaxy_far_away'
        request.POST['active'] = '1'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_ban', '/admin/bans/{ban}')
        response = ban_new_post(request)
        rule_ban = self.dbsession.query(RuleBan).first()
        self.assertEqual(response.location, '/admin/bans/%s' % rule_ban.id)
        self.assertEqual(self.dbsession.query(RuleBan).count(), 1)
        self.assertEqual(rule_ban.ip_address, '10.0.1.0/24')
        self.assertEqual(rule_ban.description, 'Violation of galactic law')
        self.assertGreaterEqual(
            rule_ban.active_until,
            datetime.now(pytz.utc) + timedelta(days=29, hours=23))
        self.assertEqual(rule_ban.scope, 'galaxy_far_away')
        self.assertTrue(rule_ban.active)

    def test_ban_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import ban_new_post
        self.request.method = 'POST'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict({})
        self.request.POST['ip_address'] = '10.0.1.0/24'
        self.request.POST['description'] = 'Violation of galactic law'
        self.request.POST['duration'] = 30
        self.request.POST['scope'] = 'galaxy_far_away'
        self.request.POST['active'] = '1'
        with self.assertRaises(BadCSRFToken):
            ban_new_post(self.request)

    def test_ban_new_post_invalid_ip_address(self):
        from ..interfaces import IRuleBanCreateService
        from ..models import RuleBan
        from ..services import RuleBanCreateService
        from ..views.admin import ban_new_post
        from . import mock_service
        request = mock_service(self.request, {
            IRuleBanCreateService: RuleBanCreateService(self.dbsession)})
        request.method = 'POST'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['ip_address'] = 'foobar'
        request.POST['description'] = 'Violation of galactic law'
        request.POST['duration'] = '30'
        request.POST['scope'] = 'galaxy_far_away'
        request.POST['active'] = '1'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = ban_new_post(request)
        self.assertEqual(self.dbsession.query(RuleBan).count(), 0)
        self.assertEqual(response['form'].ip_address.data, 'foobar')
        self.assertDictEqual(response['form'].errors, {
            'ip_address': ['Must be a valid IP address.']})

    def test_ban_get(self):
        from ..models import RuleBan
        from ..interfaces import IRuleBanQueryService
        from ..services import RuleBanQueryService
        from ..views.admin import ban_get
        from . import mock_service
        rule_ban = self._make(RuleBan(ip_address='10.0.0.0/24'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['ban'] = str(rule_ban.id)
        response = ban_get(request)
        self.assertEqual(response['ban'], rule_ban)

    def test_ban_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IRuleBanQueryService
        from ..services import RuleBanQueryService
        from ..views.admin import ban_get
        from . import mock_service
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['ban'] = '-1'
        with self.assertRaises(NoResultFound):
            ban_get(request)

    def test_ban_edit_get(self):
        from datetime import datetime, timedelta
        from ..models import RuleBan
        from ..interfaces import IRuleBanQueryService
        from ..services import RuleBanQueryService
        from ..views.admin import ban_edit_get
        from . import mock_service
        now = datetime.now()
        rule_ban = self._make(RuleBan(
            ip_address='10.0.0.0/24',
            description='Violation of galactic law',
            active_until=now + timedelta(days=30),
            scope='galaxy_far_away',
            active=True,
            created_at=now))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['ban'] = str(rule_ban.id)
        response = ban_edit_get(request)
        self.assertEqual(response['ban'], rule_ban)
        self.assertEqual(response['form'].ip_address.data, '10.0.0.0/24')
        self.assertEqual(
            response['form'].description.data,
            'Violation of galactic law')
        self.assertEqual(response['form'].duration.data, 30)
        self.assertEqual(response['form'].scope.data, 'galaxy_far_away')
        self.assertTrue(response['form'].active.data)

    def test_ban_edit_get_no_duration(self):
        from ..models import RuleBan
        from ..interfaces import IRuleBanQueryService
        from ..services import RuleBanQueryService
        from ..views.admin import ban_edit_get
        from . import mock_service
        rule_ban = self._make(RuleBan(ip_address='10.0.0.0/24'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['ban'] = str(rule_ban.id)
        response = ban_edit_get(request)
        self.assertEqual(response['form'].duration.data, 0)

    def test_ban_edit_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IRuleBanQueryService
        from ..services import RuleBanQueryService
        from ..views.admin import ban_edit_get
        from . import mock_service
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['ban'] = '-1'
        with self.assertRaises(NoResultFound):
            ban_edit_get(request)

    def test_ban_edit_post(self):
        import pytz
        from datetime import datetime, timedelta
        from ..models import RuleBan
        from ..interfaces import IRuleBanQueryService, IRuleBanUpdateService
        from ..services import RuleBanQueryService, RuleBanUpdateService
        from ..views.admin import ban_edit_post
        from . import mock_service
        rule_ban = self._make(RuleBan(ip_address='10.0.0.0/24'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession),
            IRuleBanUpdateService: RuleBanUpdateService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['ban'] = str(rule_ban.id)
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['ip_address'] = '10.0.1.0/24'
        request.POST['description'] = 'Violation of galactic law'
        request.POST['duration'] = 30
        request.POST['scope'] = 'galaxy_far_away'
        request.POST['active'] = ''
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_ban', '/admin/bans/{ban}')
        response = ban_edit_post(request)
        self.assertEqual(response.location, '/admin/bans/%s' % rule_ban.id)
        self.assertEqual(rule_ban.ip_address, '10.0.1.0/24')
        self.assertEqual(rule_ban.description, 'Violation of galactic law')
        self.assertGreaterEqual(
            rule_ban.active_until,
            datetime.now(pytz.utc) + timedelta(days=29, hours=23))
        self.assertEqual(rule_ban.scope, 'galaxy_far_away')
        self.assertFalse(rule_ban.active)

    def test_ban_edit_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IRuleBanQueryService
        from ..services import RuleBanQueryService
        from ..views.admin import ban_edit_post
        from . import mock_service
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['ban'] = '-1'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['csrf_token'] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            ban_edit_post(request)

    def test_ban_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..models import RuleBan
        from ..views.admin import ban_edit_post
        rule_ban = self._make(RuleBan(ip_address='10.0.0.0/24'))
        self.request.method = 'POST'
        self.request.matchdict['ban'] = str(rule_ban.id)
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict({})
        self.request.POST['ip_address'] = '10.0.1.0/24'
        self.request.POST['description'] = 'Violation of galactic law'
        self.request.POST['duration'] = 30
        self.request.POST['scope'] = 'galaxy_far_away'
        self.request.POST['active'] = ''
        with self.assertRaises(BadCSRFToken):
            ban_edit_post(self.request)

    def test_ban_edit_post_duration(self):
        import pytz
        from datetime import datetime, timedelta
        from ..models import RuleBan
        from ..interfaces import IRuleBanQueryService, IRuleBanUpdateService
        from ..services import RuleBanQueryService, RuleBanUpdateService
        from ..views.admin import ban_edit_post
        from . import mock_service
        past_now = datetime.now() - timedelta(days=30)
        rule_ban = self._make(RuleBan(
            ip_address='10.0.0.0/24',
            created_at=past_now,
            active_until=past_now + timedelta(days=7)))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession),
            IRuleBanUpdateService: RuleBanUpdateService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['ban'] = str(rule_ban.id)
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['ip_address'] = '10.0.0.0/24'
        request.POST['description'] = ''
        request.POST['duration'] = '14'
        request.POST['scope'] = ''
        request.POST['active'] = ''
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_ban', '/admin/bans/{ban}')
        active_until = rule_ban.active_until
        response = ban_edit_post(request)
        self.assertEqual(response.location, '/admin/bans/%s' % rule_ban.id)
        self.assertEqual(rule_ban.duration, 14)
        self.assertGreater(rule_ban.active_until, active_until)
        self.assertLess(rule_ban.active_until, datetime.now(pytz.utc))

    def test_ban_edit_post_duration_no_change(self):
        from datetime import datetime, timedelta
        from ..models import RuleBan
        from ..interfaces import IRuleBanQueryService, IRuleBanUpdateService
        from ..services import RuleBanQueryService, RuleBanUpdateService
        from ..views.admin import ban_edit_post
        from . import mock_service
        past_now = datetime.now() - timedelta(days=30)
        rule_ban = self._make(RuleBan(
            ip_address='10.0.0.0/24',
            created_at=past_now,
            active_until=past_now + timedelta(days=7)))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession),
            IRuleBanUpdateService: RuleBanUpdateService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['ban'] = str(rule_ban.id)
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['ip_address'] = '10.0.0.0/24'
        request.POST['description'] = ''
        request.POST['duration'] = '7'
        request.POST['scope'] = ''
        request.POST['active'] = ''
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_ban', '/admin/bans/{ban}')
        active_until = rule_ban.active_until
        response = ban_edit_post(request)
        self.assertEqual(response.location, '/admin/bans/%s' % rule_ban.id)
        self.assertEqual(
            rule_ban.active_until,
            active_until)

    def test_ban_edit_post_invalid_ip_address(self):
        from ..models import RuleBan
        from ..interfaces import IRuleBanQueryService, IRuleBanUpdateService
        from ..services import RuleBanQueryService, RuleBanUpdateService
        from ..views.admin import ban_edit_post
        from . import mock_service
        rule_ban = self._make(RuleBan(ip_address='10.0.0.0/24'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IRuleBanQueryService: RuleBanQueryService(self.dbsession),
            IRuleBanUpdateService: RuleBanUpdateService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['ban'] = str(rule_ban.id)
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['ip_address'] = 'foobar'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = ban_edit_post(request)
        self.assertEqual(rule_ban.ip_address, '10.0.0.0/24')
        self.assertEqual(response['ban'], rule_ban)
        self.assertEqual(response['form'].ip_address.data, 'foobar')
        self.assertDictEqual(response['form'].errors, {
            'ip_address': ['Must be a valid IP address.']})

    def test_boards_get(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.admin import boards_get
        from . import mock_service
        board1 = self._make(Board(slug='foo', title='Foo', status='open'))
        board2 = self._make(Board(
            slug='baz',
            title='Baz',
            status='restricted'))
        board3 = self._make(Board(slug='bax', title='Bax', status='locked'))
        board4 = self._make(Board(slug='wel', title='Wel', status='open'))
        board5 = self._make(Board(slug='bar', title='Bar', status='archived'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        response = boards_get(request)
        self.assertEqual(
            response['boards'],
            [board5, board3, board2, board1, board4])

    def test_board_new_get(self):
        from ..forms import AdminBoardNewForm
        from ..views.admin import board_new_get
        self.request.method = 'GET'
        response = board_new_get(self.request)
        self.assertIsInstance(response['form'], AdminBoardNewForm)

    def test_board_new_post(self):
        from ..interfaces import IBoardCreateService
        from ..models import Board
        from ..services import BoardCreateService
        from ..views.admin import board_new_post
        from . import mock_service
        request = mock_service(self.request, {
            IBoardCreateService: BoardCreateService(self.dbsession)})
        request.method = 'POST'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['slug'] = 'foobar'
        request.POST['title'] = 'Foobar'
        request.POST['status'] = 'open'
        request.POST['description'] = 'Foobar'
        request.POST['agreements'] = 'I agree'
        request.POST['settings'] = '{"name":"Nameless Foobar"}'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_board', '/admin/boards/{board}')
        response = board_new_post(request)
        board = self.dbsession.query(Board).first()
        self.assertEqual(response.location, '/admin/boards/foobar')
        self.assertEqual(self.dbsession.query(Board).count(), 1)
        self.assertEqual(board.slug, 'foobar')
        self.assertEqual(board.title, 'Foobar')
        self.assertEqual(board.description, 'Foobar')
        self.assertEqual(board.agreements, 'I agree')
        self.assertEqual(board.settings, {
            'max_posts': 1000,
            'name': 'Nameless Foobar',
            'post_delay': 10,
            'use_ident': True})

    def test_board_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_new_post
        self.request.method = 'POST'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict([])
        self.request.POST['slug'] = 'foobar'
        self.request.POST['title'] = 'Foobar'
        self.request.POST['status'] = 'open'
        self.request.POST['description'] = 'Foobar'
        self.request.POST['agreements'] = 'I agree'
        self.request.POST['settings'] = '{}'
        with self.assertRaises(BadCSRFToken):
            board_new_post(self.request)

    def test_board_new_post_invalid_status(self):
        from ..models import Board
        from ..views.admin import board_new_post
        self.request.method = 'POST'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict([])
        self.request.POST['slug'] = 'foobar'
        self.request.POST['title'] = 'Foobar'
        self.request.POST['status'] = 'foobar'
        self.request.POST['description'] = 'Foobar'
        self.request.POST['agreements'] = 'I agree'
        self.request.POST['settings'] = '{}'
        self.request.POST['csrf_token'] = self.request.session.get_csrf_token()
        response = board_new_post(self.request)
        self.assertEqual(self.dbsession.query(Board).count(), 0)
        self.assertEqual(response['form'].slug.data, 'foobar')
        self.assertEqual(response['form'].title.data, 'Foobar')
        self.assertEqual(response['form'].status.data, 'foobar')
        self.assertEqual(response['form'].description.data, 'Foobar')
        self.assertEqual(response['form'].agreements.data, 'I agree')
        self.assertEqual(response['form'].settings.data, '{}')
        self.assertDictEqual(response['form'].errors, {
            'status': ['Not a valid choice']})

    def test_board_new_post_invalid_settings(self):
        from ..models import Board
        from ..views.admin import board_new_post
        self.request.method = 'POST'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict([])
        self.request.POST['slug'] = 'foobar'
        self.request.POST['title'] = 'Foobar'
        self.request.POST['status'] = 'open'
        self.request.POST['description'] = 'Foobar'
        self.request.POST['agreements'] = 'I agree'
        self.request.POST['settings'] = 'foobar'
        self.request.POST['csrf_token'] = self.request.session.get_csrf_token()
        response = board_new_post(self.request)
        self.assertEqual(self.dbsession.query(Board).count(), 0)
        self.assertEqual(response['form'].slug.data, 'foobar')
        self.assertEqual(response['form'].title.data, 'Foobar')
        self.assertEqual(response['form'].status.data, 'open')
        self.assertEqual(response['form'].description.data, 'Foobar')
        self.assertEqual(response['form'].agreements.data, 'I agree')
        self.assertEqual(response['form'].settings.data, 'foobar')
        self.assertDictEqual(response['form'].errors, {
            'settings': ['Must be a valid JSON.']})

    def test_board_get(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.admin import board_get
        from . import mock_service
        board = self._make(Board(title='Foobar', slug='foobar'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = 'foobar'
        response = board_get(request)
        self.assertEqual(response['board'], board)

    def test_board_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_get
        from . import mock_service
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = 'foobar'
        with self.assertRaises(NoResultFound):
            board_get(request)

    def test_board_edit_get(self):
        from ..forms import AdminBoardForm
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.admin import board_edit_get
        from . import mock_service
        board = self._make(Board(
            title='Foobar',
            slug='foobar',
            description='Foobar',
            agreements='I agree',
            settings={'name': 'Nameless Foobar'}))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = 'foobar'
        response = board_edit_get(request)
        self.assertEqual(response['board'], board)
        self.assertIsInstance(response['form'], AdminBoardForm)
        self.assertEqual(response['form'].title.data, 'Foobar')
        self.assertEqual(response['form'].status.data, 'open')
        self.assertEqual(response['form'].description.data, 'Foobar')
        self.assertEqual(response['form'].agreements.data, 'I agree')
        self.assertEqual(
            response['form'].settings.data,
            '{\n' +
            '    "max_posts": 1000,\n' +
            '    "name": "Nameless Foobar",\n' +
            '    "post_delay": 10,\n' +
            '    "use_ident": true\n' +
            '}')

    def test_board_edit_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_edit_get
        from . import mock_service
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['board'] = 'foobar'
        with self.assertRaises(NoResultFound):
            board_edit_get(request)

    def test_board_edit_post(self):
        from ..interfaces import IBoardQueryService, IBoardUpdateService
        from ..models import Board
        from ..services import BoardQueryService, BoardUpdateService
        from ..views.admin import board_edit_post
        from . import mock_service
        board = self._make(Board(slug='baz', title='Baz'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IBoardUpdateService: BoardUpdateService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = 'baz'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['title'] = 'Foobar'
        request.POST['status'] = 'locked'
        request.POST['description'] = 'Foobar'
        request.POST['agreements'] = 'I agree'
        request.POST['settings'] = '{"name":"Nameless Foobar"}'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_board', '/admin/boards/{board}')
        response = board_edit_post(request)
        self.assertEqual(response.location, '/admin/boards/baz')
        self.assertEqual(board.title, 'Foobar')
        self.assertEqual(board.status, 'locked')
        self.assertEqual(board.description, 'Foobar')
        self.assertEqual(board.agreements, 'I agree')
        self.assertEqual(board.settings, {
            'max_posts': 1000,
            'name': 'Nameless Foobar',
            'post_delay': 10,
            'use_ident': True})

    def test_board_edit_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_edit_post
        from . import mock_service
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = 'notexists'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['csrf_token'] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_edit_post(request)

    def test_board_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..models import Board
        from ..views.admin import board_edit_post
        board = self._make(Board(slug='baz', title='Baz'))
        self.dbsession.commit()
        self.request.method = 'POST'
        self.request.matchdict['board'] = board.slug
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict([])
        self.request.POST['title'] = 'Foobar'
        self.request.POST['status'] = 'open'
        self.request.POST['description'] = 'Foobar'
        self.request.POST['agreements'] = 'I agree'
        self.request.POST['settings'] = '{}'
        with self.assertRaises(BadCSRFToken):
            board_edit_post(self.request)

    def test_board_edit_post_invalid_status(self):
        from ..interfaces import IBoardQueryService, IBoardUpdateService
        from ..models import Board
        from ..services import BoardQueryService, BoardUpdateService
        from ..views.admin import board_edit_post
        from . import mock_service
        board = self._make(Board(slug='baz', title='Baz'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IBoardUpdateService: BoardUpdateService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = 'baz'
        request.POST = MultiDict([])
        request.POST['title'] = 'Foobar'
        request.POST['status'] = 'foobar'
        request.POST['description'] = 'Foobar'
        request.POST['agreements'] = 'I agree'
        request.POST['settings'] = '{"name":"Nameless Foobar"}'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_board', '/admin/boards/{board}')
        response = board_edit_post(request)
        self.assertEqual(board.status, 'open')
        self.assertEqual(response['form'].title.data, 'Foobar')
        self.assertEqual(response['form'].status.data, 'foobar')
        self.assertEqual(response['form'].description.data, 'Foobar')
        self.assertEqual(response['form'].agreements.data, 'I agree')
        self.assertEqual(
            response['form'].settings.data,
            '{"name":"Nameless Foobar"}')
        self.assertDictEqual(response['form'].errors, {
            'status': ['Not a valid choice']})

    def test_board_edit_post_invalid_settings(self):
        from ..interfaces import IBoardQueryService, IBoardUpdateService
        from ..models import Board
        from ..services import BoardQueryService, BoardUpdateService
        from ..views.admin import board_edit_post
        from . import mock_service
        board = self._make(Board(slug='baz', title='Baz'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IBoardQueryService: BoardQueryService(self.dbsession),
            IBoardUpdateService: BoardUpdateService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['board'] = 'baz'
        request.POST = MultiDict([])
        request.POST['title'] = 'Foobar'
        request.POST['status'] = 'locked'
        request.POST['description'] = 'Foobar'
        request.POST['agreements'] = 'I agree'
        request.POST['settings'] = 'invalid'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_board', '/admin/boards/{board}')
        response = board_edit_post(request)
        self.assertEqual(board.status, 'open')
        self.assertEqual(response['form'].title.data, 'Foobar')
        self.assertEqual(response['form'].status.data, 'locked')
        self.assertEqual(response['form'].description.data, 'Foobar')
        self.assertEqual(response['form'].agreements.data, 'I agree')
        self.assertEqual(response['form'].settings.data, 'invalid')
        self.assertDictEqual(response['form'].errors, {
            'settings': ['Must be a valid JSON.']})

    def test_topics_get(self):
        from datetime import datetime, timedelta
        from ..interfaces import ITopicQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services import TopicQueryService
        from ..views.admin import topics_get
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
        request = mock_service(self.request, {
            ITopicQueryService: TopicQueryService(self.dbsession)})
        request.method = 'GET'
        response = topics_get(request)
        self.assertEqual(
            response['topics'],
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

    def test_pages_get(self):
        from sqlalchemy import inspect
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import pages_get
        from . import mock_service
        internal_pages = (
            ('foo', 'none'),
            ('bar', 'markdown'),
            ('baz', 'html'))

        class _WrappedPageQueryService(PageQueryService):
            def list_internal(self):
                return super(_WrappedPageQueryService, self).\
                    list_internal(_internal_pages=internal_pages)

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
        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession)})
        request.method = 'GET'
        response = pages_get(request)
        self.assertEqual(
            response['pages'],
            [page2, page3, page1])
        self.assertEqual(response['pages_internal'][0].slug, 'bar')
        self.assertEqual(response['pages_internal'][1].slug, 'baz')
        self.assertEqual(response['pages_internal'][2].slug, 'foo')
        self.assertEqual(response['pages_internal'][3].slug, 'hoge')
        self.assertTrue(inspect(response['pages_internal'][0]).persistent)
        self.assertFalse(inspect(response['pages_internal'][1]).persistent)
        self.assertFalse(inspect(response['pages_internal'][2]).persistent)
        self.assertTrue(inspect(response['pages_internal'][3]).persistent)

    def test_page_new_get(self):
        from ..forms import AdminPublicPageNewForm
        from ..views.admin import page_new_get
        self.request.method = 'GET'
        response = page_new_get(self.request)
        self.assertIsInstance(response['form'], AdminPublicPageNewForm)

    def test_page_new_post(self):
        from ..interfaces import IPageCreateService
        from ..models import Page
        from ..services import PageCreateService
        from ..views.admin import page_new_post
        from . import mock_service
        request = mock_service(self.request, {
            IPageCreateService: PageCreateService(self.dbsession)})
        request.method = 'POST'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['title'] = 'Foobar'
        request.POST['slug'] = 'foobar'
        request.POST['body'] = '**Hello, world!**'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_page', '/admin/pages/{page}')
        response = page_new_post(request)
        page = self.dbsession.query(Page).first()
        self.assertEqual(response.location, '/admin/pages/foobar')
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        self.assertEqual(page.slug, 'foobar')
        self.assertEqual(page.title, 'Foobar')
        self.assertEqual(page.body, '**Hello, world!**')
        self.assertEqual(page.namespace, 'public')
        self.assertEqual(page.formatter, 'markdown')

    def test_page_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_new_post
        self.request.method = 'POST'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict({})
        self.request.POST['title'] = 'Foobar'
        self.request.POST['slug'] = 'foobar'
        self.request.POST['body'] = '**Hello, world!**'
        with self.assertRaises(BadCSRFToken):
            page_new_post(self.request)

    def test_page_new_post_invalid_title(self):
        from ..forms import AdminPublicPageNewForm
        from ..models import Page
        from ..views.admin import page_new_post
        self.request.method = 'POST'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict({})
        self.request.POST['title'] = ''
        self.request.POST['slug'] = 'foobar'
        self.request.POST['body'] = '**Hello, world!**'
        self.request.POST['csrf_token'] = self.request.session.get_csrf_token()
        response = page_new_post(self.request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)
        self.assertIsInstance(response['form'], AdminPublicPageNewForm)
        self.assertEqual(response['form'].title.data, '')
        self.assertEqual(response['form'].slug.data, 'foobar')
        self.assertEqual(response['form'].body.data, '**Hello, world!**')
        self.assertDictEqual(response['form'].errors, {
            'title': ['This field is required.']})

    def test_page_new_post_invalid_slug(self):
        from ..forms import AdminPublicPageNewForm
        from ..models import Page
        from ..views.admin import page_new_post
        self.request.method = 'POST'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict({})
        self.request.POST['title'] = 'Foobar'
        self.request.POST['slug'] = ''
        self.request.POST['body'] = '**Hello, world!**'
        self.request.POST['csrf_token'] = self.request.session.get_csrf_token()
        response = page_new_post(self.request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)
        self.assertIsInstance(response['form'], AdminPublicPageNewForm)
        self.assertEqual(response['form'].title.data, 'Foobar')
        self.assertEqual(response['form'].slug.data, '')
        self.assertEqual(response['form'].body.data, '**Hello, world!**')
        self.assertDictEqual(response['form'].errors, {
            'slug': ['This field is required.']})

    def test_page_new_post_invalid_body(self):
        from ..forms import AdminPublicPageNewForm
        from ..models import Page
        from ..views.admin import page_new_post
        self.request.method = 'POST'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict({})
        self.request.POST['title'] = 'Foobar'
        self.request.POST['slug'] = 'foobar'
        self.request.POST['body'] = ''
        self.request.POST['csrf_token'] = self.request.session.get_csrf_token()
        response = page_new_post(self.request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)
        self.assertIsInstance(response['form'], AdminPublicPageNewForm)
        self.assertEqual(response['form'].title.data, 'Foobar')
        self.assertEqual(response['form'].slug.data, 'foobar')
        self.assertEqual(response['form'].body.data, '')
        self.assertDictEqual(response['form'].errors, {
            'body': ['This field is required.']})

    def test_page_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_get
        from . import mock_service
        page = self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Hello**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'foobar'
        response = page_get(request)
        self.assertEqual(response['page'], page)

    def test_page_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_get
        from . import mock_service
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'notexists'
        with self.assertRaises(NoResultFound):
            page_get(request)

    def test_page_edit_get(self):
        from ..forms import AdminPublicPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_edit_get
        from . import mock_service
        page = self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Hello**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'foobar'
        response = page_edit_get(request)
        self.assertEqual(response['page'], page)
        self.assertIsInstance(response['form'], AdminPublicPageForm)
        self.assertEqual(response['form'].title.data, 'Foobar')
        self.assertEqual(response['form'].body.data, '**Hello**')

    def test_page_edit_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_edit_get
        from . import mock_service
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'notexists'
        with self.assertRaises(NoResultFound):
            page_edit_get(request)

    def test_page_edit_post(self):
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_edit_post
        from . import mock_service
        page = self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Hello**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession),
            IPageUpdateService: PageUpdateService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['page'] = 'foobar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['title'] = 'Baz'
        request.POST['body'] = '**Baz**'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_page', '/admin/pages/{page}')
        response = page_edit_post(request)
        self.assertEqual(response.location, '/admin/pages/foobar')
        self.assertEqual(page.slug, 'foobar')
        self.assertEqual(page.title, 'Baz')
        self.assertEqual(page.body, '**Baz**')
        self.assertEqual(page.namespace, 'public')
        self.assertEqual(page.formatter, 'markdown')

    def test_page_edit_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_edit_post
        from . import mock_service
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['page'] = 'notexists'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['csrf_token'] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            page_edit_post(request)

    def test_page_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_edit_post
        from . import mock_service
        page = self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Hello**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        self.request.method = 'POST'
        self.request.matchdict['page'] = 'notexists'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict([])
        self.request.POST['title'] = 'Baz'
        self.request.POST['body'] = '**Baz**'
        with self.assertRaises(BadCSRFToken):
            page_edit_post(self.request)

    def test_page_edit_post_invalid_title(self):
        from ..forms import AdminPublicPageForm
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_edit_post
        from . import mock_service
        page = self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Hello**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['page'] = 'foobar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['title'] = ''
        request.POST['body'] = '**Baz**'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = page_edit_post(request)
        self.assertIsInstance(response['form'], AdminPublicPageForm)
        self.assertEqual(response['form'].title.data, '')
        self.assertEqual(response['form'].body.data, '**Baz**')
        self.assertEqual(page.slug, 'foobar')
        self.assertEqual(page.title, 'Foobar')
        self.assertEqual(page.body, '**Hello**')
        self.assertEqual(page.namespace, 'public')
        self.assertEqual(page.formatter, 'markdown')

    def test_page_edit_post_invalid_body(self):
        from ..forms import AdminPublicPageForm
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_edit_post
        from . import mock_service
        page = self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Hello**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: PageQueryService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['page'] = 'foobar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['title'] = 'Baz'
        request.POST['body'] = ''
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = page_edit_post(request)
        self.assertIsInstance(response['form'], AdminPublicPageForm)
        self.assertEqual(response['form'].title.data, 'Baz')
        self.assertEqual(response['form'].body.data, '')
        self.assertEqual(page.slug, 'foobar')
        self.assertEqual(page.title, 'Foobar')
        self.assertEqual(page.body, '**Hello**')
        self.assertEqual(page.namespace, 'public')
        self.assertEqual(page.formatter, 'markdown')

    def test_page_delete_post(self):
        from ..interfaces import IPageDeleteService
        from ..models import Page
        from ..services import PageDeleteService
        from ..views.admin import page_delete_post
        from . import mock_service
        page = self._make(Page(
            slug='foobar',
            title='Foobar',
            body='**Hello**',
            namespace='public',
            formatter='markdown'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageDeleteService: PageDeleteService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['page'] = 'foobar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_pages', '/admin/pages')
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        response = page_delete_post(request)
        self.assertEqual(response.location, '/admin/pages')
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_delete_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageDeleteService
        from ..services import PageDeleteService
        from ..views.admin import page_delete_post
        from . import mock_service
        request = mock_service(self.request, {
            IPageDeleteService: PageDeleteService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['page'] = 'notexists'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['csrf_token'] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            page_delete_post(request)

    def test_page_delete_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_delete_post
        self.request.method = 'POST'
        self.request.matchdict['page'] = 'notexists'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict([])
        with self.assertRaises(BadCSRFToken):
            page_delete_post(self.request)

    def test_page_internal_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_get
        from . import mock_service

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).\
                    internal_page_from_slug(
                        slug,
                        _internal_pages=(('global/foobar', 'html'),))

        page = self._make(Page(
            slug='global/foobar',
            title='global/foobar',
            body='<em>Hello</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'global/foobar'
        response = page_internal_get(request)
        self.assertEqual(response['page_slug'], 'global/foobar')
        self.assertEqual(response['page'], page)

    def test_page_internal_get_not_found(self):
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_get
        from . import mock_service

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).\
                    internal_page_from_slug(
                        slug,
                        _internal_pages=(('global/notexists', 'none'),))

        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'global/notexists'
        response = page_internal_get(request)
        self.assertEqual(response['page_slug'], 'global/notexists')
        self.assertIsNone(response['page'])

    def test_page_internal_get_not_allowed(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_get
        from . import mock_service

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).\
                    internal_page_from_slug(
                        slug,
                        _internal_pages=tuple())

        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'global/foobar'
        with self.assertRaises(HTTPNotFound):
            page_internal_get(request)

    def test_page_internal_edit_get(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_get
        from . import mock_service

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).\
                    internal_page_from_slug(
                        slug,
                        _internal_pages=(('global/foobar', 'html'),))

        page = self._make(Page(
            slug='global/foobar',
            title='global/foobar',
            body='<em>Hello</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'global/foobar'
        response = page_internal_edit_get(request)
        self.assertIsInstance(response['form'], AdminPageForm)
        self.assertEqual(response['form'].body.data, '<em>Hello</em>')
        self.assertEqual(response['page_slug'], 'global/foobar')
        self.assertEqual(response['page'], page)

    def test_page_internal_edit_get_auto_create(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_get
        from . import mock_service

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).\
                    internal_page_from_slug(
                        slug,
                        _internal_pages=(('global/foobar', 'html'),))

        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'global/foobar'
        response = page_internal_edit_get(request)
        self.assertIsInstance(response['form'], AdminPageForm)
        self.assertEqual(response['form'].body.data, None)
        self.assertEqual(response['page_slug'], 'global/foobar')
        self.assertIsNone(response['page'])

    def test_page_internal_edit_not_allowed(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_get
        from . import mock_service

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).\
                    internal_page_from_slug(
                        slug,
                        _internal_pages=tuple())

        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'global/notallowed'
        with self.assertRaises(HTTPNotFound):
            page_internal_edit_get(request)

    def test_page_internal_edit_post(self):
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).\
                    internal_page_from_slug(
                        slug,
                        _internal_pages=(('global/foobar', 'html'),))

        page = self._make(Page(
            slug='global/foobar',
            title='global/foobar',
            body='<em>Hello</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession),
            IPageUpdateService: PageUpdateService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'global/foobar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['body'] = '<em>World</em>'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_page_internal', '/admin/pages_i/{page}')
        response = page_internal_edit_post(request)
        self.assertEqual(response.location, '/admin/pages_i/global/foobar')
        self.assertEqual(page.slug, 'global/foobar')
        self.assertEqual(page.title, 'global/foobar')
        self.assertEqual(page.body, '<em>World</em>')
        self.assertEqual(page.namespace, 'internal')
        self.assertEqual(page.formatter, 'html')

    def test_page_internal_edit_post_auto_create(self):
        from ..interfaces import IPageQueryService, IPageCreateService
        from ..models import Page
        from ..services import PageQueryService, PageCreateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service

        class _WrappedPageCreateService(PageCreateService):
            def create_internal(self, slug, body):
                return super(_WrappedPageCreateService, self).\
                    create_internal(
                        slug,
                        body,
                        _internal_pages=(('global/foobar', 'html'),))

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).\
                    internal_page_from_slug(
                        slug,
                        _internal_pages=(('global/foobar', 'html'),))

        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession),
            IPageCreateService: _WrappedPageCreateService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'global/foobar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['body'] = '<em>World</em>'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_page_internal', '/admin/pages_i/{page}')
        response = page_internal_edit_post(request)
        self.assertEqual(response.location, '/admin/pages_i/global/foobar')
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        page = self.dbsession.query(Page).first()
        self.assertEqual(page.slug, 'global/foobar')
        self.assertEqual(page.title, 'global/foobar')
        self.assertEqual(page.body, '<em>World</em>')
        self.assertEqual(page.namespace, 'internal')
        self.assertEqual(page.formatter, 'html')

    def test_page_internal_edit_post_not_allowed(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IPageQueryService, IPageCreateService
        from ..models import Page
        from ..services import PageQueryService, PageCreateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).\
                    internal_page_from_slug(
                        slug,
                        _internal_pages=tuple())

        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'global/foobar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['body'] = '<em>World</em>'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            page_internal_edit_post(request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_internal_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_internal_edit_post
        self.request.method = 'GET'
        self.request.matchdict['page'] = 'global/foobar'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict([])
        self.request.POST['body'] = '<em>World</em>'
        with self.assertRaises(BadCSRFToken):
            page_internal_edit_post(self.request)

    def test_page_internal_edit_post_invalid_body(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).\
                    internal_page_from_slug(
                        slug,
                        _internal_pages=(('global/foobar', 'html'),))

        page = self._make(Page(
            slug='global/foobar',
            title='global/foobar',
            body='<em>Hello</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession),
            IPageUpdateService: PageUpdateService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'global/foobar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['body'] = ''
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = page_internal_edit_post(request)
        self.assertIsInstance(response['form'], AdminPageForm)
        self.assertEqual(response['form'].body.data, '')
        self.assertEqual(response['form'].errors, {
            'body': ['This field is required.']})
        self.assertEqual(response['page_slug'], 'global/foobar')
        self.assertEqual(response['page'], page)
        self.assertEqual(page.slug, 'global/foobar')
        self.assertEqual(page.title, 'global/foobar')
        self.assertEqual(page.body, '<em>Hello</em>')
        self.assertEqual(page.namespace, 'internal')
        self.assertEqual(page.formatter, 'html')

    def test_page_internal_edit_post_auto_create_invalid_body(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService, IPageCreateService
        from ..models import Page
        from ..services import PageQueryService, PageCreateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).\
                    internal_page_from_slug(
                        slug,
                        _internal_pages=(('global/foobar', 'html'),))

        request = mock_service(self.request, {
            IPageQueryService: _WrappedPageQueryService(self.dbsession)})
        request.method = 'GET'
        request.matchdict['page'] = 'global/foobar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['body'] = ''
        request.POST['csrf_token'] = request.session.get_csrf_token()
        response = page_internal_edit_post(request)
        self.assertIsInstance(response['form'], AdminPageForm)
        self.assertEqual(response['form'].body.data, '')
        self.assertEqual(response['form'].errors, {
            'body': ['This field is required.']})
        self.assertEqual(response['page_slug'], 'global/foobar')
        self.assertIsNone(response['page'])
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_internal_delete_post(self):
        from ..interfaces import IPageDeleteService
        from ..models import Page
        from ..services import PageDeleteService
        from ..views.admin import page_internal_delete_post
        from . import mock_service
        page = self._make(Page(
            slug='global/foobar',
            title='global/foobar',
            body='<em>Hello</em>',
            namespace='internal',
            formatter='html'))
        self.dbsession.commit()
        request = mock_service(self.request, {
            IPageDeleteService: PageDeleteService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['page'] = 'global/foobar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_pages', '/admin/pages')
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        response = page_internal_delete_post(request)
        self.assertEqual(response.location, '/admin/pages')
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_internal_delete_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageDeleteService
        from ..services import PageDeleteService
        from ..views.admin import page_internal_delete_post
        from . import mock_service
        request = mock_service(self.request, {
            IPageDeleteService: PageDeleteService(self.dbsession)})
        request.method = 'POST'
        request.matchdict['page'] = 'global/notexists'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict([])
        request.POST['csrf_token'] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            page_internal_delete_post(request)

    def test_page_internal_delete_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_internal_delete_post
        self.request.method = 'POST'
        self.request.matchdict['page'] = 'global/notexists'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict([])
        with self.assertRaises(BadCSRFToken):
            page_internal_delete_post(self.request)

    def test_settings_get(self):
        from ..interfaces import ISettingQueryService
        from ..views.admin import settings_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def list_all(self):
                return [('foo', 'bar'), ('baz', 'bax')]

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'GET'
        response = settings_get(request)
        self.assertEqual(
            response['settings'],
            [('foo', 'bar'), ('baz', 'bax')])

    def test_setting_get(self):
        from ..forms import AdminSettingForm
        from ..interfaces import ISettingQueryService
        from ..views.admin import setting_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return 'foobar'

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'GET'
        request.matchdict['setting'] = 'foo.bar'
        response = setting_get(request)
        self.assertEqual(response['key'], 'foo.bar')
        self.assertIsInstance(response['form'], AdminSettingForm)
        self.assertEqual(response['form'].value.data, '"foobar"')

    def test_setting_get_unsafe(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import ISettingQueryService
        from ..views.admin import setting_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                raise KeyError(key)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'GET'
        request.matchdict['setting'] = 'unsafekey'
        with self.assertRaises(HTTPNotFound):
            setting_get(request)

    def test_setting_post(self):
        from ..interfaces import ISettingQueryService, ISettingUpdateService
        from ..views.admin import setting_post
        from . import mock_service
        updated_key = None
        updated_value = None

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return 'foobar'

        class _DummySettingUpdateService(object):
            def update(self, key, value):
                nonlocal updated_key
                nonlocal updated_value
                updated_key = key
                updated_value = value
                return True

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService(),
            ISettingUpdateService: _DummySettingUpdateService()})
        request.method = 'POST'
        request.matchdict['setting'] = 'foo.bar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['value'] = '{"bar":"baz"}'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_settings', '/admin/settings')
        response = setting_post(request)
        self.assertEqual(response.location, "/admin/settings")
        self.assertEqual(updated_key, "foo.bar")
        self.assertEqual(updated_value, {'bar': 'baz'})

    def test_setting_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import setting_post
        self.request.method = 'POST'
        self.request.matchdict['setting'] = 'foo.bar'
        self.request.content_type = 'application/x-www-form-urlencoded'
        self.request.POST = MultiDict({})
        self.request.POST['value'] = '{"bar":"baz"}'
        self.config.add_route('admin_settings', '/admin/settings')
        with self.assertRaises(BadCSRFToken):
            setting_post(self.request)

    def test_setting_post_unsafe(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import ISettingQueryService
        from ..views.admin import setting_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                raise KeyError(key)

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'POST'
        request.matchdict['setting'] = 'foo.bar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['value'] = '{"bar":"baz"}'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_settings', '/admin/settings')
        with self.assertRaises(HTTPNotFound):
            setting_post(request)

    def test_setting_post_invalid_value(self):
        from ..interfaces import ISettingQueryService
        from ..views.admin import setting_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return 'foobar'

        request = mock_service(self.request, {
            ISettingQueryService: _DummySettingQueryService()})
        request.method = 'POST'
        request.matchdict['setting'] = 'foo.bar'
        request.content_type = 'application/x-www-form-urlencoded'
        request.POST = MultiDict({})
        request.POST['value'] = 'invalid'
        request.POST['csrf_token'] = request.session.get_csrf_token()
        self.config.add_route('admin_settings', '/admin/settings')
        response = setting_post(request)
        self.assertEqual(response['form'].value.data, 'invalid')
        self.assertDictEqual(response['form'].errors, {
            'value': ['Must be a valid JSON.']})
