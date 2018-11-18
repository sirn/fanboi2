import unittest

from pyramid import testing

from . import ModelSessionMixin


class _DummyFilterService(object):
    def __init__(self, rejected_by=None):
        self._rejected_by = rejected_by

    def evaluate(self, payload):
        from ..services.filter_ import FilterResult

        return FilterResult(rejected_by=self._rejected_by, filters=[])


class _DummyIdentityService(object):
    def identity_for(self, **kwargs):
        return ",".join("%s" % (v,) for k, v in sorted(kwargs.items()))


class _DummySettingQueryService(object):
    def value_from_key(self, key, **kwargs):
        return {"app.time_zone": "Asia/Bangkok"}.get(key, None)


class TestResultProxyWithModel(ModelSessionMixin, unittest.TestCase):
    def setUp(self):
        super(TestResultProxyWithModel, self).setUp()
        self.request = testing.setUp()

    def tearDown(self):
        super(TestResultProxyWithModel, self).tearDown()
        testing.tearDown()

    def _get_target_class(self):
        from ..tasks import ResultProxy

        return ResultProxy

    def test_deserialize_board(self):
        from ..models import Board
        from . import mock_service, DummyAsyncResult

        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["board", board.id])
        )
        request = mock_service(self.request, {"db": self.dbsession})
        self.assertEqual(result_proxy.deserialize(request), board)

    def test_deserialize_page(self):
        from ..models import Page
        from . import mock_service, DummyAsyncResult

        page = self._make(
            Page(title="Test", body="**Test**", slug="test", formatter="markdown")
        )
        self.dbsession.commit()
        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["page", page.id])
        )
        request = mock_service(self.request, {"db": self.dbsession})
        self.assertEqual(result_proxy.deserialize(request), page)

    def test_deserialize_post(self):
        from ..models import Board, Topic, Post
        from . import mock_service, DummyAsyncResult

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Foobar"))
        post = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["post", post.id])
        )
        request = mock_service(self.request, {"db": self.dbsession})
        self.assertEqual(result_proxy.deserialize(request), post)

    def test_deserialize_ban(self):
        from ..models import Ban
        from . import mock_service, DummyAsyncResult

        ban = self._make(Ban(ip_address="127.0.0.1"))
        self.dbsession.commit()
        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["ban", ban.id])
        )
        request = mock_service(self.request, {"db": self.dbsession})
        self.assertEqual(result_proxy.deserialize(request), ban)

    def test_deserialize_setting(self):
        from ..models import Setting
        from . import mock_service, DummyAsyncResult

        setting = self._make(Setting(key="foo", value="bar"))
        self.dbsession.commit()
        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["setting", setting.key])
        )
        request = mock_service(self.request, {"db": self.dbsession})
        self.assertEqual(result_proxy.deserialize(request), setting)

    def test_deserialize_topic(self):
        from ..models import Board, Topic
        from . import mock_service, DummyAsyncResult

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self.dbsession.commit()
        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["topic", topic.id])
        )
        request = mock_service(self.request, {"db": self.dbsession})
        self.assertEqual(result_proxy.deserialize(request), topic)

    def test_deserialize_topic_meta(self):
        from ..models import Board, Topic, TopicMeta
        from . import mock_service, DummyAsyncResult

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Foobar"))
        topic_meta = self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["topic_meta", topic_meta.topic_id])
        )
        request = mock_service(self.request, {"db": self.dbsession})
        self.assertEqual(result_proxy.deserialize(request), topic_meta)


class TestResultProxy(unittest.TestCase):
    def setUp(self):
        super(TestResultProxy, self).setUp()
        self.request = testing.setUp()

    def tearDown(self):
        super(TestResultProxy, self).tearDown()
        testing.tearDown()

    def _get_target_class(self):
        from ..tasks import ResultProxy

        return ResultProxy

    def test_deserialize_rate_limited(self):
        from ..errors import RateLimitedError
        from . import DummyAsyncResult

        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["failure", "rate_limited", 10])
        )
        self.assertIsInstance(result_proxy.deserialize(self.request), RateLimitedError)

    def test_deserialize_params_invalid(self):
        from ..errors import ParamsInvalidError
        from . import DummyAsyncResult

        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["failure", "params_invalid", []])
        )
        self.assertIsInstance(
            result_proxy.deserialize(self.request), ParamsInvalidError
        )

    def test_deserialize_akismet_rejected(self):
        from ..errors import AkismetRejectedError
        from . import DummyAsyncResult

        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["failure", "akismet_rejected"])
        )
        self.assertIsInstance(
            result_proxy.deserialize(self.request), AkismetRejectedError
        )

    def test_deserialize_dnsbl_rejected(self):
        from ..errors import DNSBLRejectedError
        from . import DummyAsyncResult

        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["failure", "dnsbl_rejected"])
        )
        self.assertIsInstance(
            result_proxy.deserialize(self.request), DNSBLRejectedError
        )

    def test_deserialize_ban_rejected(self):
        from ..errors import BanRejectedError
        from . import DummyAsyncResult

        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["failure", "ban_rejected"])
        )
        self.assertIsInstance(result_proxy.deserialize(self.request), BanRejectedError)

    def test_deserialize_status_rejected(self):
        from ..errors import StatusRejectedError
        from . import DummyAsyncResult

        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["failure", "status_rejected", "demo"])
        )
        self.assertIsInstance(
            result_proxy.deserialize(self.request), StatusRejectedError
        )

    def test_deserialize_proxy_rejected(self):
        from ..errors import ProxyRejectedError
        from . import DummyAsyncResult

        result_proxy = self._get_target_class()(
            DummyAsyncResult("demo", "success", ["failure", "proxy_rejected", "demo"])
        )
        self.assertIsInstance(
            result_proxy.deserialize(self.request), ProxyRejectedError
        )

    def test_success(self):
        from . import DummyAsyncResult

        result_proxy = self._get_target_class()(DummyAsyncResult("demo", "success"))
        self.assertTrue(result_proxy.success())

    def test_success_non_success(self):
        from . import DummyAsyncResult

        result_proxy = self._get_target_class()(DummyAsyncResult("demo", "pending"))
        self.assertFalse(result_proxy.success())

    def test_getattr(self):
        from ..tasks import ResultProxy
        from . import DummyAsyncResult

        class DummyDummyAsyncResult(DummyAsyncResult):
            def dummy(self):
                return "dummy"

        proxy = ResultProxy(DummyDummyAsyncResult("demo", "success"))
        self.assertEqual(proxy.dummy(), "dummy")


class TestAddPostTask(ModelSessionMixin, unittest.TestCase):
    def setUp(self):
        from ..tasks import celery

        super(TestAddPostTask, self).setUp()
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry
        celery.config_from_object({"task_always_eager": True})

    def tearDown(self):
        from ..tasks import celery

        super(TestAddPostTask, self).tearDown()
        testing.tearDown()
        celery.config_from_object({"task_always_eager": False})

    def _get_target_func(self):
        from ..tasks.post import add_post

        return add_post

    def test_add_post(self):
        from datetime import datetime
        from pytz import timezone
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(
            Board(title="Foobar", slug="foo", settings={"name": "Nameless Foobar"})
        )
        topic = self._make(Topic(board=board, title="Foobar", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            True,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        post = self.dbsession.query(Post).get(resp[1])
        topic = self.dbsession.query(Topic).get(topic.id)
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(post.number, 1)
        self.assertEqual(post.name, "Nameless Foobar")
        self.assertEqual(post.ip_address, "127.0.0.1")
        self.assertEqual(post.body, "Hello, world!")
        self.assertEqual(
            post.ident,
            "foo,127.0.0.1,%s"
            % (datetime.now(timezone("Asia/Bangkok")).strftime("%Y%m%d")),
        )
        self.assertTrue(post.bumped)
        self.assertEqual(topic.status, "open")
        self.assertEqual(topic_meta.post_count, 1)
        self.assertIsNotNone(topic_meta.bumped_at)
        self.assertIsNotNone(topic_meta.posted_at)

    def test_add_post_without_bumped(self):
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Foobar", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            False,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        post = self.dbsession.query(Post).get(resp[1])
        self.assertFalse(post.bumped)

    def test_add_post_without_ident(self):
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(
            Board(title="Foobar", slug="foo", settings={"use_ident": False})
        )
        topic = self._make(Topic(board=board, title="Foobar", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            True,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        post = self.dbsession.query(Post).get(resp[1])
        self.assertIsNone(post.ident)

    def test_add_post_topic_limit(self):
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(
            Board(title="Foobar", slug="foo", settings={"max_posts": 10})
        )
        topic = self._make(Topic(board=board, title="Foobar", status="open"))
        self._make(TopicMeta(topic=topic, post_count=9))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            True,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        post = self.dbsession.query(Post).get(resp[1])
        topic = self.dbsession.query(Topic).get(topic.id)
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(post.number, 10)
        self.assertEqual(topic_meta.post_count, 10)
        self.assertEqual(topic.status, "archived")

    def test_add_post_topic_locked(self):
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Foobar", status="locked"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            True,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(self.dbsession.query(Post).count(), 0)
        self.assertEqual(topic_meta.post_count, 0)
        self.assertEqual(resp, ("failure", "status_rejected", "locked"))

    def test_add_post_topic_archived(self):
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Foobar", status="archived"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            True,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(self.dbsession.query(Post).count(), 0)
        self.assertEqual(topic_meta.post_count, 0)
        self.assertEqual(resp, ("failure", "status_rejected", "archived"))

    def test_add_post_board_restricted(self):
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo", status="restricted"))
        topic = self._make(Topic(board=board, title="Foobar", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            True,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        post = self.dbsession.query(Post).get(resp[1])
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(post.number, 1)
        self.assertEqual(topic_meta.post_count, 1)

    def test_add_post_board_locked(self):
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo", status="locked"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            True,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(self.dbsession.query(Post).count(), 0)
        self.assertEqual(topic_meta.post_count, 0)
        self.assertEqual(resp, ("failure", "status_rejected", "locked"))

    def test_add_post_board_archived(self):
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo", status="archived"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            True,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(self.dbsession.query(Post).count(), 0)
        self.assertEqual(topic_meta.post_count, 0)
        self.assertEqual(resp, ("failure", "status_rejected", "archived"))

    def test_add_post_filter_akismet_rejected(self):
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(rejected_by="akismet"),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            True,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        self.assertEqual(resp, ("failure", "akismet_rejected"))

    def test_add_post_filter_dnsbl_rejected(self):
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(rejected_by="dnsbl"),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            True,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        self.assertEqual(resp, ("failure", "dnsbl_rejected"))

    def test_add_post_filter_proxy_rejected(self):
        from ..interfaces import IFilterService, IPostCreateService
        from ..models import Board, Topic, TopicMeta
        from ..services import PostCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(rejected_by="proxy"),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            topic.id,
            "Hello, world!",
            True,
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        self.assertEqual(resp, ("failure", "proxy_rejected"))


class TestAddTopicTask(ModelSessionMixin, unittest.TestCase):
    def setUp(self):
        from ..tasks import celery

        super(TestAddTopicTask, self).setUp()
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry
        celery.config_from_object({"task_always_eager": True})

    def tearDown(self):
        from ..tasks import celery

        super(TestAddTopicTask, self).tearDown()
        testing.tearDown()
        celery.config_from_object({"task_always_eager": False})

    def _get_target_func(self):
        from ..tasks.topic import add_topic

        return add_topic

    def test_add_topic(self):
        from datetime import datetime
        from pytz import timezone
        from ..interfaces import IFilterService, ITopicCreateService
        from ..models import Board, Topic, TopicMeta
        from ..services import TopicCreateService, UserQueryService
        from . import mock_service

        board = self._make(
            Board(title="Foobar", slug="foo", settings={"name": "Nameless Foobar"})
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                ITopicCreateService: TopicCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            board.slug,
            "Title",
            "Hello, world!",
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        topic = self.dbsession.query(Topic).get(resp[1])
        topic_meta = self.dbsession.query(TopicMeta).get(resp[1])
        self.assertTrue(topic.posts[0].bumped)
        self.assertEqual(topic.title, "Title")
        self.assertEqual(topic.status, "open")
        self.assertEqual(topic_meta.post_count, 1)
        self.assertIsNotNone(topic_meta.bumped_at)
        self.assertIsNotNone(topic_meta.posted_at)
        self.assertEqual(topic.posts[0].number, 1)
        self.assertEqual(topic.posts[0].name, "Nameless Foobar")
        self.assertEqual(topic.posts[0].ip_address, "127.0.0.1")
        self.assertEqual(topic.posts[0].body, "Hello, world!")
        self.assertEqual(
            topic.posts[0].ident,
            "foo,127.0.0.1,%s"
            % (datetime.now(timezone("Asia/Bangkok")).strftime("%Y%m%d")),
        )

    def test_add_topic_without_ident(self):
        from ..interfaces import IFilterService, ITopicCreateService
        from ..models import Board, Topic
        from ..services import TopicCreateService, UserQueryService
        from . import mock_service

        board = self._make(
            Board(title="Foobar", slug="foo", settings={"use_ident": False})
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                ITopicCreateService: TopicCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            board.slug,
            "Title",
            "Hello, world!",
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        topic = self.dbsession.query(Topic).get(resp[1])
        self.assertIsNone(topic.posts[0].ident)

    def test_add_topic_board_restricted(self):
        from ..interfaces import IFilterService, ITopicCreateService
        from ..models import Board, Topic
        from ..services import TopicCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo", status="restricted"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                ITopicCreateService: TopicCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            board.slug,
            "Title",
            "Hello, world!",
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        self.assertEqual(self.dbsession.query(Topic).count(), 0)
        self.assertEqual(resp, ("failure", "status_rejected", "restricted"))

    def test_add_topic_board_locked(self):
        from ..interfaces import IFilterService, ITopicCreateService
        from ..models import Board, Topic
        from ..services import TopicCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo", status="locked"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                ITopicCreateService: TopicCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            board.slug,
            "Title",
            "Hello, world!",
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        self.assertEqual(self.dbsession.query(Topic).count(), 0)
        self.assertEqual(resp, ("failure", "status_rejected", "locked"))

    def test_add_topic_board_archived(self):
        from ..interfaces import IFilterService, ITopicCreateService
        from ..models import Board, Topic
        from ..services import TopicCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo", status="archived"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService(),
                ITopicCreateService: TopicCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            board.slug,
            "Title",
            "Hello, world!",
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        self.assertEqual(self.dbsession.query(Topic).count(), 0)
        self.assertEqual(resp, ("failure", "status_rejected", "archived"))

    def test_add_topic_filter_akismet_rejected(self):
        from ..interfaces import IFilterService, ITopicCreateService
        from ..models import Board, Topic
        from ..services import TopicCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService("akismet"),
                ITopicCreateService: TopicCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            board.slug,
            "Title",
            "Hello, world!",
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        self.assertEqual(self.dbsession.query(Topic).count(), 0)
        self.assertEqual(resp, ("failure", "akismet_rejected"))

    def test_add_topic_filter_dnsbl_rejected(self):
        from ..interfaces import IFilterService, ITopicCreateService
        from ..models import Board, Topic
        from ..services import TopicCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService("dnsbl"),
                ITopicCreateService: TopicCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            board.slug,
            "Title",
            "Hello, world!",
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        self.assertEqual(self.dbsession.query(Topic).count(), 0)
        self.assertEqual(resp, ("failure", "dnsbl_rejected"))

    def test_add_topic_filter_proxy_rejected(self):
        from ..interfaces import IFilterService, ITopicCreateService
        from ..models import Board, Topic
        from ..services import TopicCreateService, UserQueryService
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IFilterService: _DummyFilterService("proxy"),
                ITopicCreateService: TopicCreateService(
                    self.dbsession,
                    _DummyIdentityService(),
                    _DummySettingQueryService(),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        resp = self._get_target_func()(
            board.slug,
            "Title",
            "Hello, world!",
            "127.0.0.1",
            payload={
                "application_url": "https://www.example.com/",
                "referrer": "https://www.example.com/referrer",
                "url": "https://www.example.com/url",
                "user_agent": "Mock/1.0",
            },
            _request=request,
            _registry=self.config.registry,
        )
        self.assertEqual(self.dbsession.query(Topic).count(), 0)
        self.assertEqual(resp, ("failure", "proxy_rejected"))
