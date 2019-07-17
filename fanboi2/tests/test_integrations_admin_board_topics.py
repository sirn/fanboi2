import unittest
import unittest.mock

from webob.multidict import MultiDict

from . import IntegrationMixin


class TestIntegrationAdminBoardTopics(IntegrationMixin, unittest.TestCase):
    def test_board_topics_get(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..interfaces import ITopicQueryService, IBoardQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services import TopicQueryService, BoardQueryService
        from ..views.admin import board_topics_get
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
        topic9 = _make_topic(hours=2, board=board1, title="Foo", status="locked")
        topic10 = _make_topic(hours=3, board=board1, title="Foo", status="archived")
        topic11 = _make_topic(days=7, board=board1, title="Foo")
        topic12 = _make_topic(days=8, board=board1, title="Foo")
        topic13 = _make_topic(days=9, board=board1, title="Foo")
        topic15 = _make_topic(hours=1, board=board1, title="Foo")
        _make_topic(days=6, hours=1, board=board2, title="Foo")
        _make_topic(days=7, hours=1, board=board1, title="Foo", status="archived")
        _make_topic(days=7, hours=1, board=board1, title="Foo", status="locked")
        _make_topic(hours=2, board=board2, title="Foo")
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
        request.matchdict["board"] = "foo"
        response = board_topics_get(request)
        self.assertEqual(response["board"], board1)
        self.assertEqual(
            response["topics"],
            [
                topic1,
                topic15,
                topic9,
                topic10,
                topic2,
                topic3,
                topic4,
                topic5,
                topic6,
                topic7,
                topic11,
                topic12,
                topic13,
            ],
        )

    def test_board_topics_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import ITopicQueryService, IBoardQueryService
        from ..services import TopicQueryService, BoardQueryService
        from ..views.admin import board_topics_get
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

    def test_board_topic_new_get(self):
        from sqlalchemy.sql import func
        from ..forms import TopicForm
        from ..models import Board, User, UserSession
        from ..interfaces import IBoardQueryService, IUserLoginService
        from ..services import BoardQueryService, UserLoginService
        from ..views.admin import board_topic_new_get
        from . import mock_service

        board = self._make(Board(slug="foo", title="Foobar"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=func.now(),
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = "foo"
        request.client_addr = "127.0.0.1"
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_new_get(request)
        self.assertEqual(response["user"], user)
        self.assertEqual(response["board"], board)
        self.assertIsInstance(response["form"], TopicForm)

    def test_board_topic_new_get_not_found(self):
        from sqlalchemy.sql import func
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, IUserLoginService
        from ..models import User, UserSession
        from ..services import BoardQueryService, UserLoginService
        from ..views.admin import board_topic_new_get
        from . import mock_service

        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=func.now(),
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.client_addr = "127.0.0.1"
        self.config.testing_securitypolicy(userid="foo_token")
        with self.assertRaises(NoResultFound):
            board_topic_new_get(request)

    def test_board_topic_new_post(self):
        from sqlalchemy.sql import func
        from ..models import Board, Topic, User, UserSession
        from ..interfaces import (
            IBoardQueryService,
            IUserLoginService,
            ITopicCreateService,
        )
        from ..services import (
            BoardQueryService,
            UserLoginService,
            TopicCreateService,
            IdentityService,
            SettingQueryService,
            UserQueryService,
        )
        from ..views.admin import board_topic_new_post
        from . import mock_service, make_cache_region, DummyRedis

        board = self._make(Board(slug="foo", title="Foobar"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=func.now(),
            )
        )
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
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
        request.matchdict["board"] = "foo"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["title"] = "Foobar"
        request.POST["body"] = "Hello, world"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        self.config.add_route("admin_board_topic", "/admin/boards/{board}/{topic}")
        response = board_topic_new_post(request)
        topic = self.dbsession.query(Topic).one()
        self.assertEqual(response.location, "/admin/boards/foo/%s" % topic.id)
        self.assertEqual(topic.board, board)
        self.assertEqual(topic.title, "Foobar")
        self.assertEqual(topic.posts[0].body, "Hello, world")
        self.assertEqual(topic.posts[0].ip_address, "127.0.0.1")
        self.assertEqual(topic.posts[0].ident, "fooident")
        self.assertEqual(topic.posts[0].ident_type, "ident_admin")
        self.assertEqual(topic.posts[0].name, "Foo")
        self.assertTrue(topic.posts[0].bumped)

    def test_board_topic_new_post_not_found(self):
        from sqlalchemy.sql import func
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import Topic, User, UserSession
        from ..interfaces import IBoardQueryService, IUserLoginService
        from ..services import BoardQueryService, UserLoginService
        from ..views.admin import board_topic_new_post
        from . import mock_service

        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=func.now(),
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "notfound"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["title"] = "Foobar"
        request.POST["body"] = "Hello, world"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        with self.assertRaises(NoResultFound):
            board_topic_new_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topic_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_topic_new_post

        self.request.method = "POST"
        self.request.matchdict["board"] = "foo"
        self.request.client_addr = "127.0.0.1"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["title"] = "Foobar"
        self.request.POST["body"] = "Hello, world"
        with self.assertRaises(BadCSRFToken):
            board_topic_new_post(self.request)

    def test_board_topic_new_post_invalid_title(self):
        from sqlalchemy.sql import func
        from ..forms import TopicForm
        from ..interfaces import IBoardQueryService, IUserLoginService
        from ..models import Board, Topic, User, UserSession
        from ..services import BoardQueryService, UserLoginService
        from ..views.admin import board_topic_new_post
        from . import mock_service

        board = self._make(Board(slug="foo", title="Foobar"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=func.now(),
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "foo"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["title"] = ""
        request.POST["body"] = "Hello, world"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_new_post(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["user"], user)
        self.assertIsInstance(response["form"], TopicForm)
        self.assertEqual(response["form"].title.data, "")
        self.assertEqual(response["form"].body.data, "Hello, world")
        self.assertDictEqual(
            response["form"].errors, {"title": ["This field is required."]}
        )
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topic_new_post_invalid_body(self):
        from sqlalchemy.sql import func
        from ..forms import TopicForm
        from ..interfaces import IBoardQueryService, IUserLoginService
        from ..models import Board, Topic, User, UserSession
        from ..services import BoardQueryService, UserLoginService
        from ..views.admin import board_topic_new_post
        from . import mock_service

        board = self._make(Board(slug="foo", title="Foobar"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=func.now(),
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "foo"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["title"] = "Foobar"
        request.POST["body"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_new_post(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["user"], user)
        self.assertIsInstance(response["form"], TopicForm)
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].body.data, "")
        self.assertDictEqual(
            response["form"].errors, {"body": ["This field is required."]}
        )
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topic_get(self):
        from sqlalchemy.sql import func
        from ..forms import PostForm
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostQueryService,
            IUserLoginService,
        )
        from ..models import Board, Topic, Post, User, UserSession
        from ..services import (
            BoardQueryService,
            TopicQueryService,
            PostQueryService,
            UserLoginService,
        )
        from ..views.admin import board_topic_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=func.now(),
            )
        )
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
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IPostQueryService: PostQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_get(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic1)
        self.assertEqual(response["posts"], [post1, post2])
        self.assertEqual(response["user"], user)
        self.assertIsInstance(response["form"], PostForm)

    def test_board_topic_get_query(self):
        from sqlalchemy.sql import func
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostQueryService,
            IUserLoginService,
        )
        from ..models import Board, Topic, Post, User, UserSession
        from ..services import (
            BoardQueryService,
            TopicQueryService,
            PostQueryService,
            UserLoginService,
        )
        from ..views.admin import board_topic_get
        from . import mock_service

        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=func.now(),
            )
        )
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
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IPostQueryService: PostQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        request.matchdict["query"] = "1"
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_get(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic1)
        self.assertEqual(response["posts"], posts[0:1])
        request.matchdict["query"] = "50"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[49:50])
        request.matchdict["query"] = "51"
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)
        request.matchdict["query"] = "1-50"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts)
        request.matchdict["query"] = "10-20"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[9:20])
        request.matchdict["query"] = "51-99"
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)
        request.matchdict["query"] = "0-51"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts)
        request.matchdict["query"] = "-0"
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)
        request.matchdict["query"] = "-5"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[:5])
        request.matchdict["query"] = "45-"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[44:])
        request.matchdict["query"] = "100-"
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)
        request.matchdict["query"] = "recent"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[20:])
        request.matchdict["query"] = "l30"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[20:])

    def test_board_topic_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
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
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_get(request)

    def test_board_topic_get_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_get
        from . import mock_service

        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_get(request)

    def test_board_topic_get_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
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
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)

    def test_board_topic_get_wrong_board_query(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
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
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        request.matchdict["query"] = "l10"
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)

    def test_board_topic_post(self):
        from sqlalchemy.sql import func
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IUserLoginService,
            IPostCreateService,
        )
        from ..models import Board, Topic, TopicMeta, Post, User, UserSession
        from ..services import (
            BoardQueryService,
            TopicQueryService,
            UserLoginService,
            PostCreateService,
            IdentityService,
            SettingQueryService,
            UserQueryService,
        )
        from ..views.admin import board_topic_post
        from . import mock_service, make_cache_region, DummyRedis

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
        self._make(TopicMeta(topic=topic, post_count=0))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=func.now(),
            )
        )
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IUserLoginService: UserLoginService(self.dbsession),
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
        request.matchdict["board"] = "foobar"
        request.matchdict["topic"] = topic.id
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["body"] = "Hello, world"
        request.POST["bumped"] = "t"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        self.config.add_route(
            "admin_board_topic_posts", "/admin/boards/{board}/{topic}/{query}"
        )
        response = board_topic_post(request)
        post = self.dbsession.query(Post).one()
        self.assertEqual(response.location, "/admin/boards/foobar/%s/recent" % topic.id)
        self.assertEqual(post.body, "Hello, world")
        self.assertEqual(post.ip_address, "127.0.0.1")
        self.assertEqual(post.ident, "fooident")
        self.assertEqual(post.ident_type, "ident_admin")
        self.assertEqual(post.name, "Foo")
        self.assertTrue(post.bumped)

    def test_board_topic_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Post
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_post
        from . import mock_service

        self._make(Board(title="Foobar", slug="foobar"))
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
        request.method = "POST"
        request.matchdict["board"] = "foobar"
        request.matchdict["topic"] = "-1"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["body"] = "Hello, world"
        request.POST["bumped"] = "t"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_board_topic_post_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..models import Post
        from ..services import BoardQueryService
        from ..views.admin import board_topic_post
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "POST"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["body"] = "Hello, world"
        request.POST["bumped"] = "t"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_board_topic_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_topic_post

        self.request.method = "POST"
        self.request.matchdict["board"] = "foobar"
        self.request.matchdict["topic"] = "1"
        self.request.client_addr = "127.0.0.1"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["body"] = "Hello, world"
        self.request.POST["bumped"] = "t"
        with self.assertRaises(BadCSRFToken):
            board_topic_post(self.request)

    def test_board_topic_post_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_post
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        self._make(Board(title="Baz", slug="baz"))
        topic = self._make(Topic(board=board1, title="Demo"))
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
        request.method = "POST"
        request.matchdict["board"] = "baz"
        request.matchdict["topic"] = topic.id
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["body"] = "Hello, world"
        request.POST["bumped"] = "t"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_post(request)

    def test_board_topic_post_invalid_body(self):
        from sqlalchemy.sql import func
        from ..forms import PostForm
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IUserLoginService,
        )
        from ..models import Board, Topic, Post, User, UserSession
        from ..services import BoardQueryService, TopicQueryService, UserLoginService
        from ..views.admin import board_topic_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=func.now(),
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "foobar"
        request.matchdict["topic"] = topic.id
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["body"] = ""
        request.POST["bumped"] = "t"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_post(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)
        self.assertEqual(response["user"], user)
        self.assertIsInstance(response["form"], PostForm)
        self.assertEqual(response["form"].body.data, "")
        self.assertTrue(response["form"].bumped.data)
        self.assertDictEqual(
            response["form"].errors, {"body": ["This field is required."]}
        )
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_board_topic_edit_get(self):
        from ..forms import AdminTopicForm
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
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
        request.matchdict["topic"] = topic.id
        response = board_topic_edit_get(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)
        self.assertIsInstance(response["form"], AdminTopicForm)
        self.assertEqual(response["form"].status.data, "open")

    def test_board_topic_edit_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
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
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_edit_get(request)

    def test_board_topic_edit_get_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_edit_get
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_edit_get(request)

    def test_board_topic_edit_get_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        self._make(Board(title="Baz", slug="baz"))
        topic = self._make(Topic(board=board1, title="Demo"))
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
        request.matchdict["board"] = "baz"
        request.matchdict["topic"] = topic.id
        with self.assertRaises(HTTPNotFound):
            board_topic_edit_get(request)

    def test_board_topic_edit_post(self):
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            ITopicUpdateService,
        )
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService, TopicUpdateService
        from ..views.admin import board_topic_edit_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                ITopicUpdateService: TopicUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["status"] = "locked"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route(
            "admin_board_topic_posts", "/admin/boards/{board}/{topic}/{query}"
        )
        self.assertEqual(topic.status, "open")
        response = board_topic_edit_post(request)
        self.assertEqual(response.location, "/admin/boards/foobar/%s/recent" % topic.id)
        self.assertEqual(topic.status, "locked")

    def test_board_topic_edit_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
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
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["status"] = "locked"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_edit_post(request)

    def test_board_topic_edit_post_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_edit_post
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "POST"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["status"] = "locked"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_edit_post(request)

    def test_board_topic_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_topic_edit_post

        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.method = "POST"
        self.request.matchdict["board"] = "foobar"
        self.request.matchdict["topic"] = "-1"
        with self.assertRaises(BadCSRFToken):
            board_topic_edit_post(self.request)

    def test_board_topic_edit_post_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_post
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        self._make(Board(title="Baz", slug="baz"))
        topic = self._make(Topic(board=board1, title="Demo"))
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
        request.method = "POST"
        request.matchdict["board"] = "baz"
        request.matchdict["topic"] = topic.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["status"] = "locked"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_edit_post(request)

    def test_board_topic_edit_post_invalid_status(self):
        from ..forms import AdminTopicForm
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
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
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["status"] = "foobar"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = board_topic_edit_post(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)
        self.assertIsInstance(response["form"], AdminTopicForm)
        self.assertEqual(response["form"].status.data, "foobar")
        self.assertDictEqual(
            response["form"].errors, {"status": ["Not a valid choice"]}
        )

    def test_board_topic_delete_get(self):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_delete_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
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
        request.matchdict["topic"] = topic.id
        response = board_topic_delete_get(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)

    def test_board_topic_delete_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_delete_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
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
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_delete_get(request)

    def test_board_topic_delete_get_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_delete_get
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_delete_get(request)

    def test_board_topic_delete_get_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_delete_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        self._make(Board(title="Baz", slug="baz"))
        topic = self._make(Topic(board=board1, title="Demo"))
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
        request.matchdict["board"] = "baz"
        request.matchdict["topic"] = topic.id
        with self.assertRaises(HTTPNotFound):
            board_topic_delete_get(request)

    def test_board_topic_delete_post(self):
        from sqlalchemy import inspect
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            ITopicDeleteService,
        )
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import BoardQueryService, TopicQueryService, TopicDeleteService
        from ..views.admin import board_topic_delete_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        topic_meta1 = self._make(TopicMeta(topic=topic1, post_count=2))
        topic_meta2 = self._make(TopicMeta(topic=topic2, post_count=1))
        post1 = self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Foo",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Foo",
                body="Foobar 2",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Foo",
                body="Foobar 3",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                ITopicDeleteService: TopicDeleteService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_board_topics", "/admin/boards/{board}/topics")
        response = board_topic_delete_post(request)
        self.assertEqual(response.location, "/admin/boards/foobar/topics")
        self.dbsession.flush()
        self.assertTrue(inspect(topic1).was_deleted)
        self.assertFalse(inspect(topic2).was_deleted)
        self.assertTrue(inspect(topic_meta1).was_deleted)
        self.assertFalse(inspect(topic_meta2).was_deleted)
        self.assertTrue(inspect(post1).was_deleted)
        self.assertTrue(inspect(post2).was_deleted)
        self.assertFalse(inspect(post3).was_deleted)

    def test_board_topic_delete_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_delete_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
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
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_delete_post(request)

    def test_board_topic_delete_post_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_delete_post
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_delete_post(request)

    def test_board_topic_delete_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_topic_delete_post

        self.request.method = "GET"
        self.request.matchdict["board"] = "foobar"
        self.request.matchdict["topic"] = "-1"
        with self.assertRaises(BadCSRFToken):
            board_topic_delete_post(self.request)

    def test_board_topic_delete_post_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from sqlalchemy import inspect
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_delete_post
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobar Baz", slug="baz"))
        topic1 = self._make(Topic(board=board1, title="Demo"))
        topic2 = self._make(Topic(board=board2, title="Demo 2"))
        topic_meta1 = self._make(TopicMeta(topic=topic1, post_count=2))
        topic_meta2 = self._make(TopicMeta(topic=topic2, post_count=1))
        post1 = self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Foo",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Foo",
                body="Foobar 2",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Foo",
                body="Foobar 3",
                ip_address="127.0.0.1",
            )
        )
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
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic1.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_delete_post(request)
        self.dbsession.flush()
        self.assertFalse(inspect(topic1).was_deleted)
        self.assertFalse(inspect(topic2).was_deleted)
        self.assertFalse(inspect(topic_meta1).was_deleted)
        self.assertFalse(inspect(topic_meta2).was_deleted)
        self.assertFalse(inspect(post1).was_deleted)
        self.assertFalse(inspect(post2).was_deleted)
        self.assertFalse(inspect(post3).was_deleted)

    def test_board_topic_posts_delete_get(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostQueryService,
        )
        from ..models import Board, Topic, Post
        from ..services import BoardQueryService, TopicQueryService, PostQueryService
        from ..views.admin import board_topic_posts_delete_get
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
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IPostQueryService: PostQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        request.matchdict["query"] = "2"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic1)
        self.assertEqual(response["posts"], posts[1:2])
        request.matchdict["query"] = "50"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[49:50])
        request.matchdict["query"] = "51"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)
        request.matchdict["query"] = "2-50"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[1:])
        request.matchdict["query"] = "10-20"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[9:20])
        request.matchdict["query"] = "51-99"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)
        request.matchdict["query"] = "-0"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)
        request.matchdict["query"] = "45-"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[44:])
        request.matchdict["query"] = "100-"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)
        request.matchdict["query"] = "recent"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[20:])
        request.matchdict["query"] = "l30"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[20:])

    def test_board_topic_posts_delete_get_with_first_post(self):
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostQueryService,
        )
        from ..models import Board, Topic, Post
        from ..services import BoardQueryService, TopicQueryService, PostQueryService
        from ..views.admin import board_topic_posts_delete_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        posts = []
        for i in range(30):
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
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IPostQueryService: PostQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        renderer = self.config.testing_add_renderer(
            "admin/boards/topics/posts/delete_error.mako"
        )
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts, query=None
        )
        request.matchdict["query"] = "1"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts[0:1], query="1"
        )
        request.matchdict["query"] = "1-30"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts, query="1-30"
        )
        request.matchdict["query"] = "0-31"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts, query="0-31"
        )
        request.matchdict["query"] = "-5"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts[:5], query="-5"
        )
        request.matchdict["query"] = "recent"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts, query="recent"
        )
        request.matchdict["query"] = "l30"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts, query="l30"
        )

    def test_board_topic_posts_delete_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
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
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_posts_delete_get(request)

    def test_board_topic_posts_delete_get_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_posts_delete_get
        from . import mock_service

        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_posts_delete_get(request)

    def test_board_topic_posts_delete_get_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
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
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)

    def test_board_topic_posts_delete_get_wrong_board_query(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
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
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        request.matchdict["query"] = "l10"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)

    def test_board_topic_posts_delete_post(self):
        from sqlalchemy import inspect
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostDeleteService,
            IPostQueryService,
        )
        from ..models import Board, Topic, Post
        from ..services import (
            BoardQueryService,
            TopicQueryService,
            PostDeleteService,
            PostQueryService,
        )
        from ..views.admin import board_topic_posts_delete_post
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

        def assert_posts_deleted(begin, end):
            if begin is not None:
                for p in posts[:begin]:
                    self.assertFalse(inspect(p).was_deleted)
            for p in posts[begin:end]:
                self.assertTrue(inspect(p).was_deleted)
            if end is not None:
                for p in posts[end:]:
                    self.assertFalse(inspect(p).was_deleted)

        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IPostQueryService: PostQueryService(self.dbsession),
                IPostDeleteService: PostDeleteService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        request.matchdict["query"] = "2"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route(
            "admin_board_topic_posts", "/admin/boards/{board}/{topic}/{query}"
        )
        response = board_topic_posts_delete_post(request)
        self.dbsession.flush()
        self.assertEqual(
            response.location, "/admin/boards/foobar/%s/recent" % topic1.id
        )
        assert_posts_deleted(1, 2)
        self.dbsession.rollback()
        request.matchdict["query"] = "50"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(49, 50)
        self.dbsession.rollback()
        request.matchdict["query"] = "51"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "2-50"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(1, None)
        self.dbsession.rollback()
        request.matchdict["query"] = "10-20"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(9, 20)
        self.dbsession.rollback()
        request.matchdict["query"] = "51-99"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "-0"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "45-"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(44, None)
        self.dbsession.rollback()
        request.matchdict["query"] = "100-"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "recent"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(20, None)
        self.dbsession.rollback()
        request.matchdict["query"] = "l30"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(20, None)

    def test_board_topic_posts_delete_post_first_post(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostQueryService,
        )
        from ..models import Board, Topic, Post
        from ..services import BoardQueryService, TopicQueryService, PostQueryService
        from ..views.admin import board_topic_posts_delete_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        posts = []
        for i in range(30):
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
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(
                    self.dbsession, BoardQueryService(self.dbsession)
                ),
                IPostQueryService: PostQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "1"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "1-30"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "0-31"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "-5"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "recent"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "l30"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)

    def test_board_topic_posts_delete_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
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
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_posts_delete_post(request)

    def test_board_topic_posts_delete_post_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_posts_delete_post
        from . import mock_service

        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_posts_delete_post(request)

    def test_board_topic_posts_delete_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_topic_posts_delete_post

        self.request.method = "GET"
        self.request.matchdict["board"] = "foobar"
        self.request.matchdict["topic"] = "1"
        with self.assertRaises(BadCSRFToken):
            board_topic_posts_delete_post(self.request)

    def test_board_topic_posts_delete_post_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_post
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
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
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)

    def test_board_topic_posts_delete_post_wrong_board_query(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_post
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
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
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        request.matchdict["query"] = "l10"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
