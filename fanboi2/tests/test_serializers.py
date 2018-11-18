import json
import unittest

from pyramid import testing

from . import ModelSessionMixin


class _DummyQuery(object):
    def __init__(self, obj):
        self._obj = obj

    def query(self, obj_cls):
        self._obj_cls = obj_cls
        return self

    def get(self, *args):
        self._args = args
        return self._obj


class _DummySettingQueryService(object):
    def value_from_key(self, key, **kwargs):
        return {"app.time_zone": "Asia/Bangkok"}.get(key, None)


class _RendererMixin(object):
    def setUp(self):
        super(_RendererMixin, self).setUp()
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry

    def tearDown(self):
        super(_RendererMixin, self).tearDown()
        testing.tearDown()

    def _get_target_function(self):
        from ..serializers import initialize_renderer

        return initialize_renderer()

    def _make_one(self, request, obj):
        renderer = self._get_target_function()(None)
        return json.loads(renderer(obj, {"request": request}))


class TestJSONRenderer(_RendererMixin, unittest.TestCase):
    def test_datetime(self):
        from datetime import datetime, timezone
        from . import mock_service
        from ..interfaces import ISettingQueryService

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        date = datetime(2013, 1, 2, 0, 4, 1, 0, timezone.utc)
        self.assertEqual(self._make_one(request, date), "2013-01-02T07:04:01+07:00")

    def test_error_serializer(self):
        from ..errors import BaseError

        error = BaseError()
        response = self._make_one(self.request, error)
        self.assertEqual(response["type"], "error")
        self.assertEqual(response["status"], error.name)
        self.assertEqual(response["message"], error.message(self.request))

    def test_result_proxy(self):
        from ..tasks import ResultProxy
        from . import DummyAsyncResult

        self.config.add_route("api_task", "/task/{task}/")
        result_proxy = ResultProxy(DummyAsyncResult("demo", "pending"))
        response = self._make_one(self.request, result_proxy)
        self.assertEqual(response["type"], "task")
        self.assertEqual(response["status"], "pending")
        self.assertEqual(response["id"], "demo")
        self.assertEqual(response["path"], "/task/demo/")
        self.assertNotIn("data", response)

    def test_result_proxy_success(self):
        from ..tasks import ResultProxy
        from ..models import Board
        from ..interfaces import ISettingQueryService
        from . import mock_service, DummyAsyncResult

        board = Board(title="Foobar", slug="foo")
        request = mock_service(
            self.request,
            {
                ISettingQueryService: _DummySettingQueryService(),
                "db": _DummyQuery(board),
            },
        )
        self.config.add_route("api_task", "/task/{task}/")
        self.config.add_route("api_board", "/board/{board}/")
        result = ["board", board.id]
        result_proxy = ResultProxy(DummyAsyncResult("demo", "success", result))
        response = self._make_one(request, result_proxy)
        self.assertEqual(response["type"], "task")
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["id"], "demo")
        self.assertEqual(response["path"], "/task/demo/")
        self.assertIn("data", response)

    def test_async_result(self):
        from ..tasks import celery

        self.config.add_route("api_task", "/task/{task}/")
        async_result = celery.AsyncResult("demo")
        response = self._make_one(self.request, async_result)
        self.assertEqual(response["type"], "task")
        self.assertEqual(response["status"], "queued")
        self.assertEqual(response["id"], "demo")
        self.assertEqual(response["path"], "/task/demo/")


class TestJSONRendererWithModel(_RendererMixin, ModelSessionMixin, unittest.TestCase):
    def setUp(self):
        super(TestJSONRendererWithModel, self).setUp()
        from . import mock_service
        from ..interfaces import ISettingQueryService

        self.request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )

    def _make_one(self, request, obj):
        renderer = self._get_target_function()(None)
        return json.loads(renderer(obj, {"request": request}))

    def test_query(self):
        from ..models import Board

        board1 = self._make(Board(title="Foo", slug="foo"))
        board2 = self._make(Board(title="Bar", slug="bar"))
        self.dbsession.commit()
        self.config.add_route("api_board", "/board/{board}")
        response = self._make_one(
            self.request, self.dbsession.query(Board).order_by(Board.title)
        )
        self.assertIsInstance(response, list)
        self.assertEqual(response[0]["title"], board2.title)
        self.assertEqual(response[1]["title"], board1.title)

    def test_board(self):
        from ..models import Board

        board = self._make(Board(title="Foobar", slug="foo", status="open"))
        self.dbsession.commit()
        self.config.add_route("api_board", "/board/{board}/")
        response = self._make_one(self.request, board)
        self.assertEqual(response["type"], "board")
        self.assertEqual(response["title"], "Foobar")
        self.assertEqual(response["slug"], "foo")
        self.assertEqual(response["status"], "open")
        self.assertEqual(response["path"], "/board/foo/")
        self.assertIn("agreements", response)
        self.assertIn("description", response)
        self.assertIn("id", response)
        self.assertIn("settings", response)
        self.assertNotIn("topics", response)

    def test_board_with_topics(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        self.config.add_route("api_board", "/board/{board}/")
        self.config.add_route("api_topic", "/board/{topic}/")
        self.request.params = {"topics": True}
        response = self._make_one(self.request, board)
        self.assertIn("topics", response)

    def test_board_with_topics_board(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        self.request.params = {"topics": True, "board": True}
        self.config.add_route("api_board", "/board/{board}/")
        self.config.add_route("api_topic", "/board/{topic}/")
        response = self._make_one(self.request, board)
        self.assertNotIn("topics", response)

    def test_topic(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        self.config.add_route("api_topic", "/topic/{topic}/")
        response = self._make_one(self.request, topic)
        self.assertEqual(response["type"], "topic")
        self.assertEqual(response["title"], "Heavenly Moon")
        self.assertEqual(response["board_id"], board.id)
        self.assertEqual(response["path"], "/topic/%s/" % topic.id)
        self.assertIn("bumped_at", response)
        self.assertIn("created_at", response)
        self.assertIn("post_count", response)
        self.assertIn("posted_at", response)
        self.assertIn("status", response)
        self.assertNotIn("posts", response)

    def test_topic_with_board(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        self.request.params = {"board": True}
        self.config.add_route("api_topic", "/topic/{topic}/")
        self.config.add_route("api_board", "/board/{board}/")
        response = self._make_one(self.request, topic)
        self.assertEqual(response["board_id"], board.id)
        self.assertIn("board", response)

    def test_topic_with_board_topics(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        self.request.params = {"board": True, "topics": True}
        self.config.add_route("api_topic", "/topic/{topic}/")
        self.config.add_route("api_board", "/board/{board}/")
        response = self._make_one(self.request, topic)
        self.assertIn("board", response)
        self.assertNotIn("topics", response["board"])

    def test_topic_with_posts(self):
        from ..models import Board, Topic, TopicMeta, Post

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        self._make(TopicMeta(topic=topic, post_count=1))
        self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Hello, world",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        self.request.params = {"posts": True}
        self.config.add_route("api_topic", "/topic/{topic}/")
        self.config.add_route("api_topic_posts_scoped", "/topic/{topic}/{query}")
        response = self._make_one(self.request, topic)
        self.assertEqual(response["title"], "Heavenly Moon")
        self.assertEqual(response["board_id"], board.id)
        self.assertIn("posts", response)

    def test_topic_with_posts_topic(self):
        from ..models import Board, Topic, TopicMeta, Post

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        self._make(TopicMeta(topic=topic, post_count=1))
        self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Hello, world",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        self.request.params = {"posts": True, "topic": True}
        self.config.add_route("api_topic", "/topic/{topic}/")
        response = self._make_one(self.request, topic)
        self.assertEqual(response["title"], "Heavenly Moon")
        self.assertEqual(response["board_id"], board.id)
        self.assertNotIn("posts", response)

    def test_post(self):
        from ..models import Board, Topic, TopicMeta, Post

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        self._make(TopicMeta(topic=topic, post_count=1))
        post = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Hello, world",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        self.config.add_route("api_topic_posts_scoped", "/topic/{topic}/{query}/")
        response = self._make_one(self.request, post)
        self.assertEqual(response["type"], "post")
        self.assertEqual(response["body"], "Hello, world")
        self.assertEqual(response["body_formatted"], "<p>Hello, world</p>")
        self.assertEqual(response["topic_id"], topic.id)
        self.assertEqual(response["path"], "/topic/%s/%s/" % (topic.id, post.number))
        self.assertIn("bumped", response)
        self.assertIn("created_at", response)
        self.assertIn("ident", response)
        self.assertIn("ident_type", response)
        self.assertIn("name", response)
        self.assertIn("number", response)
        self.assertNotIn("ip_address", response)

    def test_post_with_topic(self):
        from ..models import Board, Topic, TopicMeta, Post

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        self._make(TopicMeta(topic=topic, post_count=1))
        post = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Hello, world",
                ip_address="127.0.0.1",
            )
        )
        self.request.params = {"topic": True}
        self.config.add_route("api_topic", "/topic/{topic}/")
        self.config.add_route("api_topic_posts_scoped", "/topic/{topic}/{query}/")
        response = self._make_one(self.request, post)
        self.assertIn("topic", response)

    def test_post_with_topic_board(self):
        from ..models import Board, Topic, TopicMeta, Post

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        self._make(TopicMeta(topic=topic, post_count=1))
        post = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Hello, world",
                ip_address="127.0.0.1",
            )
        )
        self.request.params = {"topic": True, "board": True}
        self.config.add_route("api_board", "/board/{board}/")
        self.config.add_route("api_topic", "/topic/{topic}/")
        self.config.add_route("api_topic_posts_scoped", "/topic/{topic}/{query}/")
        response = self._make_one(self.request, post)
        self.assertIn("topic", response)
        self.assertIn("board", response["topic"])

    def test_post_with_topic_posts(self):
        from ..models import Board, Topic, TopicMeta, Post

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        self._make(TopicMeta(topic=topic, post_count=1))
        post = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Hello, world",
                ip_address="127.0.0.1",
            )
        )
        self.request.params = {"topic": True, "posts": True}
        self.config.add_route("api_topic", "/topic/{topic}/")
        self.config.add_route("api_topic_posts_scoped", "/topic/{topic}/{query}/")
        response = self._make_one(self.request, post)
        self.assertIn("topic", response)
        self.assertNotIn("posts", response["topic"])

    def test_page(self):
        from ..models import Page

        page = self._make(
            Page(title="Test", body="**Test**", slug="test", formatter="markdown")
        )
        self.config.add_route("api_page", "/page/{page}")
        response = self._make_one(self.request, page)
        self.assertEqual(response["type"], "page")
        self.assertEqual(response["body"], "**Test**")
        self.assertEqual(response["body_formatted"], "<p><strong>Test</strong></p>\n")
        self.assertEqual(response["formatter"], "markdown")
        self.assertEqual(response["slug"], "test")
        self.assertEqual(response["title"], "Test")
        self.assertEqual(response["path"], "/page/test")
        self.assertIn("updated_at", response)
