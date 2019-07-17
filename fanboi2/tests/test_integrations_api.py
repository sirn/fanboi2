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
        self.request.user_agent = "Mock/1.0"
        self.request.client_addr = "127.0.0.1"
        self.request.referrer = "https://www.example.com/referer"
        self.request.url = "https://www.example.com/url"
        self.request.application_url = "https://www.example.com"

    def tearDown(self):
        super(TestIntegrationAPI, self).tearDown()
        testing.tearDown()

    def test_root(self):
        from ..views.api import root

        self.request.method = "GET"
        self.assertEqual(root(self.request), {})

    def test_boards_get(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services.board import BoardQueryService
        from ..views.api import boards_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        board3 = self._make(Board(title="Demo", slug="foodemo"))
        self._make(Board(title="Archived", slug="archived", status="archived"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        self.assertEqual(boards_get(request), [board3, board1, board2])

    def test_board_get(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services.board import BoardQueryService
        from ..views.api import board_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        self.assertEqual(board_get(request), board)

    def test_board_get_archived(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services.board import BoardQueryService
        from ..views.api import board_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar", status="archived"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        self.assertEqual(board_get(request), board)

    def test_board_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services.board import BoardQueryService
        from ..views.api import board_get
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        with self.assertRaises(NoResultFound):
            board_get(request)

    def test_board_topics_get(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.api import board_topics_get
        from . import mock_service

        def _make_topic(days=0, hours=0, **kwargs):
            topic = self._make(Topic(**kwargs))
            self._make(
                TopicMeta(
                    topic=topic,
                    post_count=0,
                    posted_at=func.now(),
                    bumped_at=func.now() - timedelta(days=days, hours=hours),
                )
            )
            return topic

        board1 = self._make(Board(title="Foo", slug="foo"))
        board2 = self._make(Board(title="Bar", slug="bar"))
        topic1 = _make_topic(board=board1, title="Foo")
        topic2 = _make_topic(days=1, board=board1, title="Foo")
        topic3 = _make_topic(days=2, board=board1, title="Foo")
        topic4 = _make_topic(days=3, board=board1, title="Foo")
        topic5 = _make_topic(days=4, board=board1, title="Foo")
        topic6 = _make_topic(days=5, board=board1, title="Foo")
        topic7 = _make_topic(days=6, board=board1, title="Foo")
        topic8 = _make_topic(hours=1, board=board1, title="Foo", status="locked")
        topic9 = _make_topic(hours=5, board=board1, title="Foo", status="archived")
        topic10 = _make_topic(days=7, board=board1, title="Foo")
        topic11 = _make_topic(days=8, board=board1, title="Foo")
        topic12 = _make_topic(days=9, board=board1, title="Foo")
        _make_topic(board=board2, title="Foo")
        _make_topic(days=7, hours=1, board=board1, title="Foo", status="archived")
        _make_topic(days=7, hours=1, board=board1, title="Foo", status="locked")
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board1.slug
        self.assertEqual(
            board_topics_get(request),
            [
                topic1,
                topic8,
                topic9,
                topic2,
                topic3,
                topic4,
                topic5,
                topic6,
                topic7,
                topic10,
                topic11,
                topic12,
            ],
        )

    def test_board_topics_get_empty(self):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.api import board_topics_get
        from . import mock_service

        board = self._make(Board(title="Foo", slug="foo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        self.assertEqual(board_topics_get(request), [])

    def test_board_topics_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..services.board import BoardQueryService
        from ..services.topic import TopicQueryService
        from ..views.api import board_topics_get
        from . import mock_service

        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        with self.assertRaises(NoResultFound):
            board_topics_get(request)

    @unittest.mock.patch("fanboi2.tasks.topic.add_topic.delay")
    def test_board_topics_post(self, add_):
        from ..interfaces import (
            IBanQueryService,
            IBanwordQueryService,
            IBoardQueryService,
            IRateLimiterService,
            ITopicCreateService,
        )
        from ..models import Board
        from ..services import (
            BanQueryService,
            BanwordQueryService,
            BoardQueryService,
            IdentityService,
            RateLimiterService,
            ScopeService,
            SettingQueryService,
            TopicCreateService,
            UserQueryService,
        )
        from ..views.api import board_topics_post
        from . import mock_service, make_cache_region, DummyRedis

        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IRateLimiterService: rate_limiter_svc,
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
                IBanwordQueryService: BanwordQueryService(
                    self.dbsession, ScopeService()
                ),
                ITopicCreateService: TopicCreateService(
                    self.dbsession,
                    IdentityService(
                        redis_conn, SettingQueryService(self.dbsession, cache_region)
                    ),
                    SettingQueryService(self.dbsession, cache_region),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.content_type = "application/json"
        request.json_body = {}
        request.json_body["title"] = "title"
        request.json_body["body"] = "bodyb"
        self.assertEqual(
            rate_limiter_svc.time_left(
                ip_address=request.client_addr, board=board.slug
            ),
            0,
        )
        add_.return_value = mock_response = unittest.mock.Mock(id="task-uuid")
        response = board_topics_post(request)
        self.assertEqual(response, mock_response)
        self.assertEqual(
            rate_limiter_svc.time_left(
                ip_address=request.client_addr, board=board.slug
            ),
            10,
        )
        add_.assert_called_with(
            "foo",
            "title",
            "bodyb",
            "127.0.0.1",
            payload={
                "application_url": request.application_url,
                "referrer": request.referrer,
                "url": request.url,
                "user_agent": request.user_agent,
            },
        )

    @unittest.mock.patch("fanboi2.tasks.topic.add_topic.delay")
    def test_board_topics_post_wwwform(self, add_):
        from ..interfaces import (
            IBanQueryService,
            IBanwordQueryService,
            IBoardQueryService,
            IRateLimiterService,
            ITopicCreateService,
        )
        from ..models import Board
        from ..services import (
            BanQueryService,
            BanwordQueryService,
            BoardQueryService,
            IdentityService,
            RateLimiterService,
            ScopeService,
            SettingQueryService,
            TopicCreateService,
            UserQueryService,
        )
        from ..views.api import board_topics_post
        from . import mock_service, make_cache_region, DummyRedis

        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IRateLimiterService: rate_limiter_svc,
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
                IBanwordQueryService: BanwordQueryService(
                    self.dbsession, ScopeService()
                ),
                ITopicCreateService: TopicCreateService(
                    self.dbsession,
                    IdentityService(
                        redis_conn, SettingQueryService(self.dbsession, cache_region)
                    ),
                    SettingQueryService(self.dbsession, cache_region),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["title"] = "title"
        request.POST["body"] = "bodyb"
        self.assertEqual(
            rate_limiter_svc.time_left(
                ip_address=request.client_addr, board=board.slug
            ),
            0,
        )
        add_.return_value = mock_response = unittest.mock.Mock(id="task-uuid")
        response = board_topics_post(request)
        self.assertEqual(response, mock_response)
        self.assertEqual(
            rate_limiter_svc.time_left(
                ip_address=request.client_addr, board=board.slug
            ),
            10,
        )
        add_.assert_called_with(
            "foo",
            "title",
            "bodyb",
            "127.0.0.1",
            payload={
                "application_url": request.application_url,
                "referrer": request.referrer,
                "url": request.url,
                "user_agent": request.user_agent,
            },
        )

    def test_board_topics_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.api import board_topics_post
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "POST"
        request.matchdict["board"] = "notexists"
        with self.assertRaises(NoResultFound):
            board_topics_post(request)

    def test_board_topics_post_invalid_title(self):
        from ..errors import ParamsInvalidError
        from ..interfaces import IBoardQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService
        from ..views.api import board_topics_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.content_type = "application/json"
        request.json_body = {}
        request.json_body["title"] = "titl"
        request.json_body["body"] = "bodyb"
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

        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.content_type = "application/json"
        request.json_body = {}
        request.json_body["title"] = "title"
        request.json_body["body"] = "body"
        with self.assertRaises(ParamsInvalidError):
            board_topics_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topics_post_banned(self):
        from ..errors import BanRejectedError
        from ..interfaces import IBoardQueryService, IBanQueryService
        from ..models import Board, Topic, Ban
        from ..services import BoardQueryService, BanQueryService, ScopeService
        from ..views.api import board_topics_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        self._make(Ban(ip_address="127.0.0.0/24", scope="board:foo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.content_type = "application/json"
        request.client_addr = "127.0.0.1"
        request.json_body = {}
        request.json_body["title"] = "title"
        request.json_body["body"] = "bodyb"
        with self.assertRaises(BanRejectedError):
            board_topics_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topics_post_banned_unscoped(self):
        from ..errors import BanRejectedError
        from ..interfaces import IBoardQueryService, IBanQueryService
        from ..models import Board, Topic, Ban
        from ..services import BoardQueryService, BanQueryService, ScopeService
        from ..views.api import board_topics_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        self._make(Ban(ip_address="127.0.0.0/24"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.content_type = "application/json"
        request.client_addr = "127.0.0.1"
        request.json_body = {}
        request.json_body["title"] = "title"
        request.json_body["body"] = "bodyb"
        with self.assertRaises(BanRejectedError):
            board_topics_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topics_post_banword_banned(self):
        from ..errors import BanwordRejectedError
        from ..interfaces import (
            IBanQueryService,
            IBanwordQueryService,
            IBoardQueryService,
        )
        from ..models import Banword, Board, Topic
        from ..services import (
            BoardQueryService,
            BanQueryService,
            BanwordQueryService,
            ScopeService,
        )
        from ..views.api import board_topics_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        self._make(Banword(expr="https?:\\/\\/bit\\.ly", scope="board:foo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
                IBanwordQueryService: BanwordQueryService(
                    self.dbsession, ScopeService()
                ),
                IBoardQueryService: BoardQueryService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.content_type = "application/json"
        request.client_addr = "127.0.0.1"
        request.json_body = {}
        request.json_body["title"] = "title"
        request.json_body["body"] = "foo\nhttps://bit.ly/spam\nbar"
        with self.assertRaises(BanwordRejectedError):
            board_topics_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topics_post_banword_banned_unscoped(self):
        from ..errors import BanwordRejectedError
        from ..interfaces import (
            IBanQueryService,
            IBanwordQueryService,
            IBoardQueryService,
        )
        from ..models import Banword, Board, Topic
        from ..services import (
            BoardQueryService,
            BanQueryService,
            BanwordQueryService,
            ScopeService,
        )
        from ..views.api import board_topics_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        self._make(Banword(expr="https?:\\/\\/bit\\.ly"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
                IBanwordQueryService: BanwordQueryService(
                    self.dbsession, ScopeService()
                ),
                IBoardQueryService: BoardQueryService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.content_type = "application/json"
        request.client_addr = "127.0.0.1"
        request.json_body = {}
        request.json_body["title"] = "title"
        request.json_body["body"] = "foo\nhttps://bit.ly/spam\nbar"
        with self.assertRaises(BanwordRejectedError):
            board_topics_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topics_post_rate_limited(self):
        from ..errors import RateLimitedError
        from ..interfaces import (
            IBanQueryService,
            IBanwordQueryService,
            IBoardQueryService,
            IRateLimiterService,
        )
        from ..models import Board, Topic
        from ..services import (
            BanQueryService,
            BanwordQueryService,
            BoardQueryService,
            RateLimiterService,
            ScopeService,
        )
        from ..views.api import board_topics_post
        from . import mock_service, DummyRedis

        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IRateLimiterService: rate_limiter_svc,
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
                IBanwordQueryService: BanwordQueryService(
                    self.dbsession, ScopeService()
                ),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.content_type = "application/json"
        request.json_body = {}
        request.json_body["title"] = "title"
        request.json_body["body"] = "bodyb"
        rate_limiter_svc.limit_for(10, ip_address=request.client_addr, board=board.slug)
        with self.assertRaises(RateLimitedError):
            board_topics_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    @unittest.mock.patch("fanboi2.tasks.celery.AsyncResult")
    def test_task_get(self, result_):
        from ..interfaces import ITaskQueryService
        from ..models import Board, Topic
        from ..services import TaskQueryService
        from ..views.api import task_get
        from . import mock_service, DummyAsyncResult

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self.dbsession.commit()
        result_.return_value = async_result = DummyAsyncResult(
            "dummy", "success", ["topic", topic.id]
        )
        request = mock_service(
            self.request, {"db": self.dbsession, ITaskQueryService: TaskQueryService()}
        )
        request.method = "GET"
        request.matchdict["task"] = "dummy"
        response = task_get(request)
        self.assertEqual(response.id, async_result.id)
        self.assertEqual(response.deserialize(request), topic)
        result_.assert_called_with("dummy")

    @unittest.mock.patch("fanboi2.tasks.celery.AsyncResult")
    def test_task_get_rejected(self, result_):
        from ..errors import AkismetRejectedError
        from ..interfaces import ITaskQueryService
        from ..services import TaskQueryService
        from ..views.api import task_get
        from . import mock_service, DummyAsyncResult

        result_.return_value = DummyAsyncResult(
            "dummy", "success", ["failure", "akismet_rejected"]
        )
        request = mock_service(self.request, {ITaskQueryService: TaskQueryService()})
        request.method = "GET"
        request.matchdict["task"] = "dummy"
        with self.assertRaises(AkismetRejectedError):
            task_get(request)
        result_.assert_called_with("dummy")

    def test_topic_get(self):
        from ..interfaces import ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.api import topic_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                )
            },
        )
        request.method = "GET"
        request.matchdict["topic"] = topic.id
        self.assertEqual(topic_get(request), topic)

    def test_topic_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import ITopicQueryService
        from ..services import BoardQueryService, TopicQueryService
        from ..views.api import topic_get
        from . import mock_service

        request = mock_service(
            self.request,
            {
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                )
            },
        )
        request.method = "GET"
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            topic_get(request)

    def test_topic_posts_get(self):
        from ..interfaces import IPostQueryService
        from ..models import Board, Topic, Post
        from ..services import PostQueryService
        from ..views.api import topic_posts_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        post1 = self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Fanboi",
                body="Lorem ipsum",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Fanboi",
                body="Dolor sit",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IPostQueryService: PostQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["topic"] = topic1.id
        self.assertEqual(topic_posts_get(request), [post1, post2])

    def test_topic_posts_get_query(self):
        from ..interfaces import IPostQueryService
        from ..models import Board, Topic, Post
        from ..services import PostQueryService
        from ..views.api import topic_posts_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        posts = []
        for i in range(50):
            posts.append(
                self._make(
                    Post(
                        topic=topic1,
                        number=i + 1,
                        name="Nameless Fanboi",
                        body="Lorem ipsum",
                        ip_address="127.0.0.1",
                    )
                )
            )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IPostQueryService: PostQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["topic"] = topic1.id
        request.matchdict["query"] = "1"
        self.assertEqual(topic_posts_get(request), posts[0:1])
        request.matchdict["query"] = "50"
        self.assertEqual(topic_posts_get(request), posts[49:50])
        request.matchdict["query"] = "51"
        self.assertEqual(topic_posts_get(request), [])
        request.matchdict["query"] = "1-50"
        self.assertEqual(topic_posts_get(request), posts)
        request.matchdict["query"] = "10-20"
        self.assertEqual(topic_posts_get(request), posts[9:20])
        request.matchdict["query"] = "51-99"
        self.assertEqual(topic_posts_get(request), [])
        request.matchdict["query"] = "0-51"
        self.assertEqual(topic_posts_get(request), posts)
        request.matchdict["query"] = "-0"
        self.assertEqual(topic_posts_get(request), [])
        request.matchdict["query"] = "-5"
        self.assertEqual(topic_posts_get(request), posts[:5])
        request.matchdict["query"] = "45-"
        self.assertEqual(topic_posts_get(request), posts[44:])
        request.matchdict["query"] = "100-"
        self.assertEqual(topic_posts_get(request), [])
        request.matchdict["query"] = "recent"
        self.assertEqual(topic_posts_get(request), posts[20:])
        request.matchdict["query"] = "l30"
        self.assertEqual(topic_posts_get(request), posts[20:])

    def test_topic_posts_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPostQueryService
        from ..services import PostQueryService
        from ..views.api import topic_posts_get
        from . import mock_service

        request = mock_service(
            self.request, {IPostQueryService: PostQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            topic_posts_get(request)

    @unittest.mock.patch("fanboi2.tasks.post.add_post.delay")
    def test_topic_posts_post(self, add_):
        from ..interfaces import (
            IBanQueryService,
            IBanwordQueryService,
            IPostCreateService,
            IRateLimiterService,
            ITopicQueryService,
        )
        from ..models import Board, Topic, TopicMeta
        from ..services import (
            BanQueryService,
            BanwordQueryService,
            BoardQueryService,
            IdentityService,
            PostCreateService,
            RateLimiterService,
            ScopeService,
            SettingQueryService,
            TopicQueryService,
            UserQueryService,
        )
        from ..views.api import topic_posts_post
        from . import mock_service, make_cache_region, DummyRedis

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(
            self.request,
            {
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IRateLimiterService: rate_limiter_svc,
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
                IBanwordQueryService: BanwordQueryService(
                    self.dbsession, ScopeService()
                ),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    IdentityService(
                        redis_conn, SettingQueryService(self.dbsession, cache_region)
                    ),
                    SettingQueryService(self.dbsession, cache_region),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        request.method = "POST"
        request.matchdict["topic"] = topic.id
        request.content_type = "application/json"
        request.json_body = {}
        request.json_body["body"] = "bodyb"
        request.json_body["bumped"] = True
        self.assertEqual(
            rate_limiter_svc.time_left(
                ip_address=request.client_addr, board=board.slug
            ),
            0,
        )
        add_.return_value = mock_response = unittest.mock.Mock(id="task-uuid")
        response = topic_posts_post(request)
        self.assertEqual(response, mock_response)
        self.assertEqual(
            rate_limiter_svc.time_left(
                ip_address=request.client_addr, board=board.slug
            ),
            10,
        )
        add_.assert_called_with(
            topic.id,
            "bodyb",
            True,
            "127.0.0.1",
            payload={
                "application_url": request.application_url,
                "referrer": request.referrer,
                "url": request.url,
                "user_agent": request.user_agent,
            },
        )

    @unittest.mock.patch("fanboi2.tasks.post.add_post.delay")
    def test_topic_posts_post_wwwform(self, add_):
        from ..interfaces import (
            IBanQueryService,
            IBanwordQueryService,
            IPostCreateService,
            IRateLimiterService,
            ITopicQueryService,
        )
        from ..models import Board, Topic, TopicMeta
        from ..services import (
            BanQueryService,
            BanwordQueryService,
            BoardQueryService,
            IdentityService,
            PostCreateService,
            RateLimiterService,
            ScopeService,
            SettingQueryService,
            TopicQueryService,
            UserQueryService,
        )
        from ..views.api import topic_posts_post
        from . import mock_service, make_cache_region, DummyRedis

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(
            self.request,
            {
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IRateLimiterService: rate_limiter_svc,
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
                IBanwordQueryService: BanwordQueryService(
                    self.dbsession, ScopeService()
                ),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    IdentityService(
                        redis_conn, SettingQueryService(self.dbsession, cache_region)
                    ),
                    SettingQueryService(self.dbsession, cache_region),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        request.method = "POST"
        request.matchdict["topic"] = topic.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["body"] = "bodyb"
        request.POST["bumped"] = "1"
        self.assertEqual(
            rate_limiter_svc.time_left(
                ip_address=request.client_addr, board=board.slug
            ),
            0,
        )
        add_.return_value = mock_response = unittest.mock.Mock(id="task-uuid")
        response = topic_posts_post(request)
        self.assertEqual(response, mock_response)
        self.assertEqual(
            rate_limiter_svc.time_left(
                ip_address=request.client_addr, board=board.slug
            ),
            10,
        )
        add_.assert_called_with(
            topic.id,
            "bodyb",
            True,
            "127.0.0.1",
            payload={
                "application_url": request.application_url,
                "referrer": request.referrer,
                "url": request.url,
                "user_agent": request.user_agent,
            },
        )

    def test_topic_posts_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import ITopicQueryService
        from ..services import BoardQueryService, TopicQueryService
        from ..views.api import topic_posts_post
        from . import mock_service

        request = mock_service(
            self.request,
            {
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                )
            },
        )
        request.method = "POST"
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            topic_posts_post(request)

    def test_topic_posts_post_invalid_body(self):
        from ..errors import ParamsInvalidError
        from ..interfaces import ITopicQueryService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import BoardQueryService, TopicQueryService
        from ..views.api import topic_posts_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                )
            },
        )
        request.method = "POST"
        request.matchdict["topic"] = topic.id
        request.content_type = "application/json"
        request.json_body = {}
        request.json_body["body"] = "body"
        request.json_body["bumped"] = True
        with self.assertRaises(ParamsInvalidError):
            topic_posts_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_topic_posts_post_banned(self):
        from ..errors import BanRejectedError
        from ..interfaces import ITopicQueryService, IBanQueryService
        from ..models import Board, Topic, TopicMeta, Post, Ban
        from ..services import (
            BoardQueryService,
            TopicQueryService,
            BanQueryService,
            ScopeService,
        )
        from ..views.api import topic_posts_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(Ban(ip_address="127.0.0.0/24", scope="board:foobar"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
            },
        )
        request.method = "POST"
        request.matchdict["topic"] = topic.id
        request.content_type = "application/json"
        request.client_addr = "127.0.0.1"
        request.json_body = {}
        request.json_body["body"] = "bodyb"
        request.json_body["bumped"] = True
        with self.assertRaises(BanRejectedError):
            topic_posts_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_topic_posts_post_banned_unscoped(self):
        from ..errors import BanRejectedError
        from ..interfaces import ITopicQueryService, IBanQueryService
        from ..models import Board, Topic, TopicMeta, Post, Ban
        from ..services import (
            BoardQueryService,
            TopicQueryService,
            BanQueryService,
            ScopeService,
        )
        from ..views.api import topic_posts_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(Ban(ip_address="127.0.0.0/24"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
            },
        )
        request.method = "POST"
        request.matchdict["topic"] = topic.id
        request.content_type = "application/json"
        request.client_addr = "127.0.0.1"
        request.json_body = {}
        request.json_body["body"] = "bodyb"
        request.json_body["bumped"] = True
        with self.assertRaises(BanRejectedError):
            topic_posts_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_topic_posts_banword_banned(self):
        from ..errors import BanwordRejectedError
        from ..interfaces import (
            IBanQueryService,
            IBanwordQueryService,
            ITopicQueryService,
        )
        from ..models import Board, Topic, TopicMeta, Post, Banword
        from ..services import (
            BanQueryService,
            BanwordQueryService,
            BoardQueryService,
            ScopeService,
            TopicQueryService,
        )
        from ..views.api import topic_posts_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(Banword(expr="https?:\\/\\/bit\\.ly"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
                IBanwordQueryService: BanwordQueryService(
                    self.dbsession, ScopeService()
                ),
            },
        )

        request.method = "POST"
        request.matchdict["topic"] = topic.id
        request.content_type = "application/json"
        request.client_addr = "127.0.0.1"
        request.json_body = {}
        request.json_body["body"] = "foo\nhttps://bit.ly/spam\nbar"
        request.json_body["bumped"] = True
        with self.assertRaises(BanwordRejectedError):
            topic_posts_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_topic_posts_post_rate_limited(self):
        from ..errors import RateLimitedError
        from ..interfaces import (
            IBanQueryService,
            IBanwordQueryService,
            IRateLimiterService,
            ITopicQueryService,
        )
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import (
            BanQueryService,
            BanwordQueryService,
            BoardQueryService,
            RateLimiterService,
            TopicQueryService,
            ScopeService,
        )
        from ..views.api import topic_posts_post
        from . import mock_service, DummyRedis

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        rate_limiter_svc = RateLimiterService(redis_conn)
        request = mock_service(
            self.request,
            {
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IRateLimiterService: rate_limiter_svc,
                IBanQueryService: BanQueryService(self.dbsession, ScopeService()),
                IBanwordQueryService: BanwordQueryService(
                    self.dbsession, ScopeService()
                ),
            },
        )
        request.method = "POST"
        request.matchdict["topic"] = topic.id
        request.content_type = "application/json"
        request.json_body = {}
        request.json_body["body"] = "bodyb"
        request.json_body["bumped"] = True
        rate_limiter_svc.limit_for(10, ip_address=request.client_addr, board=board.slug)
        with self.assertRaises(RateLimitedError):
            topic_posts_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_pages_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.api import pages_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page1 = self._make(Page(title="Foo", body="Foo", slug="foo"))
        page2 = self._make(Page(title="Bar", body="Bar", slug="bar"))
        page3 = self._make(Page(title="Baz", body="Baz", slug="baz"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        self.assertEqual(pages_get(request), [page2, page3, page1])

    def test_page_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.api import page_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(Page(title="Foo", body="Foo", slug="foo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = page.slug
        self.assertEqual(page_get(request), page)

    def test_page_get_internal(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.api import page_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(title="Foo", body="Foo", slug="foo", namespace="internal")
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = page.slug
        with self.assertRaises(NoResultFound):
            page_get(request)

    def test_page_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.api import page_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "notexists"
        with self.assertRaises(NoResultFound):
            page_get(request)

    def test_error_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..views.api import error_not_found

        self.request.path = "/foobar"
        response = error_not_found(HTTPNotFound(), self.request)
        self.assertEqual(self.request.response.status, "404 Not Found")
        self.assertEqual(response["type"], "error")
        self.assertEqual(response["status"], "not_found")
        self.assertEqual(
            response["message"], "The resource GET /foobar could not be found."
        )

    def test_error_base_handler(self):
        from ..errors import BaseError
        from ..views.api import error_base_handler

        self.request.path = "/foobar"
        exc = BaseError()
        response = error_base_handler(exc, self.request)
        self.assertEqual(self.request.response.status, exc.http_status)
        self.assertEqual(response, exc)

    def test_api_routes_predicates(self):
        from ..views.api import _api_routes_only

        self.request.path = "/api/test"
        self.assertTrue(_api_routes_only(None, self.request))

    def test_api_routes_predicates_not_api(self):
        from ..views.api import _api_routes_only

        self.request.path = "/foobar/api"
        self.assertFalse(_api_routes_only(None, self.request))
