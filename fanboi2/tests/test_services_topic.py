import unittest
import unittest.mock

from sqlalchemy.orm.exc import NoResultFound

from . import ModelSessionMixin


class TestTopicCreateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import TopicCreateService

        return TopicCreateService

    def _make_one(self):
        from ..services import UserQueryService

        class _DummyIdentityService(object):
            def identity_with_tz_for(self, tz, **kwargs):
                return ",".join("%s" % (v,) for k, v in sorted(kwargs.items()))

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {"app.time_zone": "Asia/Bangkok"}.get(key, None)

        return self._get_target_class()(
            self.dbsession,
            _DummyIdentityService(),
            _DummySettingQueryService(),
            UserQueryService(self.dbsession),
        )

    def test_create(self):
        from ..models import Board

        board = self._make(
            Board(slug="foo", title="Foo", settings={"name": "Nameless Foobar"})
        )
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create(
            board.slug, "Hello, world!", "Hello Eartians", "127.0.0.1"
        )
        self.assertEqual(topic.board, board)
        self.assertEqual(topic.title, "Hello, world!")
        self.assertEqual(topic.meta.post_count, 1)
        self.assertIsNotNone(topic.meta.bumped_at)
        self.assertEqual(topic.posts[0].number, 1)
        self.assertEqual(topic.posts[0].bumped, True)
        self.assertEqual(topic.posts[0].name, "Nameless Foobar")
        self.assertEqual(topic.posts[0].ip_address, "127.0.0.1")
        self.assertEqual(topic.posts[0].ident, "foo,127.0.0.1")
        self.assertEqual(topic.posts[0].ident_type, "ident")

    def test_create_without_ident(self):
        from ..models import Board

        board = self._make(
            Board(slug="foo", title="Foo", settings={"use_ident": False})
        )
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create(
            board.slug, "Hello, world!", "Hello Eartians", "127.0.0.1"
        )
        self.assertIsNone(topic.posts[0].ident)
        self.assertEqual(topic.posts[0].ident_type, "none")

    def test_create_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound

        topic_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            topic_create_svc.create(
                "notexists", "Hello, world!", "Hello Eartians", "127.0.0.1"
            )

    def test_create_board_restricted(self):
        from ..errors import StatusRejectedError
        from ..models import Board

        board = self._make(Board(slug="foo", title="Foo", status="restricted"))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            topic_create_svc.create(
                board.slug, "Hello, world!", "Hello Eartians", "127.0.0.1"
            )

    def test_create_board_locked(self):
        from ..errors import StatusRejectedError
        from ..models import Board

        board = self._make(Board(slug="foo", title="Foo", status="locked"))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            topic_create_svc.create(
                board.slug, "Hello, world!", "Hello Eartians", "127.0.0.1"
            )

    def test_create_board_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board

        board = self._make(Board(slug="foo", title="Foo", status="archived"))
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            topic_create_svc.create(
                board.slug, "Hello, world!", "Hello Eartians", "127.0.0.1"
            )

    def test_create_with_user(self):
        from ..models import Board, User

        board = self._make(
            Board(slug="foo", title="Foo", settings={"name": "Nameless Foobar"})
        )
        user = self._make(
            User(
                username="root",
                encrypted_password="foobar",
                ident="fooident",
                ident_type="ident_admin",
                name="Root",
            )
        )
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create_with_user(
            board.slug, user.id, "Hello, world!", "Hello Eartians", "127.0.0.1"
        )
        self.assertEqual(topic.board, board)
        self.assertEqual(topic.title, "Hello, world!")
        self.assertEqual(topic.meta.post_count, 1)
        self.assertIsNotNone(topic.meta.bumped_at)
        self.assertEqual(topic.posts[0].number, 1)
        self.assertEqual(topic.posts[0].bumped, True)
        self.assertEqual(topic.posts[0].name, "Root")
        self.assertEqual(topic.posts[0].ip_address, "127.0.0.1")
        self.assertEqual(topic.posts[0].ident, "fooident")
        self.assertEqual(topic.posts[0].ident_type, "ident_admin")

    def test_create_with_user_without_ident(self):
        from ..models import Board, User

        board = self._make(
            Board(
                slug="foo",
                title="Foo",
                settings={"name": "Nameless Foobar", "use_ident": False},
            )
        )
        user = self._make(
            User(
                username="root",
                encrypted_password="foobar",
                ident="fooident",
                ident_type="ident_admin",
                name="Root",
            )
        )
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create_with_user(
            board.slug, user.id, "Hello, world!", "Hello Eartians", "127.0.0.1"
        )
        self.assertEqual(topic.posts[0].ident, "fooident")
        self.assertEqual(topic.posts[0].ident_type, "ident_admin")

    def test_create_with_user_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import User

        user = self._make(
            User(
                username="root",
                encrypted_password="foobar",
                ident="fooident",
                ident_type="ident_admin",
                name="Root",
            )
        )
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            topic_create_svc.create_with_user(
                "notexists", user.id, "Hello, world!", "Hello Eartians", "127.0.0.1"
            )

    def test_create_with_user_not_found_user(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import Board

        board = self._make(
            Board(
                slug="foo",
                title="Foo",
                settings={"name": "Nameless Foobar", "use_ident": False},
            )
        )
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            topic_create_svc.create_with_user(
                board.slug, -1, "Hello, world!", "Hello Eartians", "127.0.0.1"
            )

    def test_create_with_user_board_restricted(self):
        from ..models import Board, User

        board = self._make(Board(slug="foo", title="Foo", status="restricted"))
        user = self._make(
            User(
                username="root",
                encrypted_password="foobar",
                ident="fooident",
                ident_type="ident_admin",
                name="Root",
            )
        )
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create_with_user(
            board.slug, user.id, "Hello, world!", "Hello Eartians", "127.0.0.1"
        )
        self.assertEqual(topic.board, board)
        self.assertEqual(topic.title, "Hello, world!")
        self.assertEqual(topic.meta.post_count, 1)

    def test_create_with_user_board_locked(self):
        from ..models import Board, User

        board = self._make(Board(slug="foo", title="Foo", status="locked"))
        user = self._make(
            User(
                username="root",
                encrypted_password="foobar",
                ident="fooident",
                ident_type="ident_admin",
                name="Root",
            )
        )
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        topic = topic_create_svc.create_with_user(
            board.slug, user.id, "Hello, world!", "Hello Eartians", "127.0.0.1"
        )
        self.assertEqual(topic.board, board)
        self.assertEqual(topic.title, "Hello, world!")
        self.assertEqual(topic.meta.post_count, 1)

    def test_create_with_user_board_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board, User

        board = self._make(Board(slug="foo", title="Foo", status="archived"))
        user = self._make(
            User(
                username="root",
                encrypted_password="foobar",
                ident="fooident",
                ident_type="ident_admin",
                name="Root",
            )
        )
        self.dbsession.commit()
        topic_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            topic_create_svc.create_with_user(
                board.slug, user.id, "Hello, world!", "Hello Eartians", "127.0.0.1"
            )


class TestTopicDeleteService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import TopicDeleteService

        return TopicDeleteService

    def test_delete(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic, TopicMeta, Post

        board = self._make(Board(slug="foo", title="Foobar"))
        topic1 = self._make(Topic(board=board, title="Foobar Baz"))
        topic2 = self._make(Topic(board=board, title="Baz Bax"))
        topic_meta1 = self._make(TopicMeta(topic=topic1, post_count=2))
        topic_meta2 = self._make(TopicMeta(topic=topic2, post_count=1))
        post1 = self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Foobar",
                body="Body",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Foobar",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Foobar",
                body="Hi",
                ip_address="127.0.0.1",
            )
        )
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

    def _make_one(self):
        from fanboi2.models import Board

        _dbsession = self.dbsession

        class _DummyBoardQueryService(object):
            def board_from_slug(self, board_slug):
                return _dbsession.query(Board).filter_by(slug=board_slug).one()

        return self._get_target_class()(_dbsession, _DummyBoardQueryService())

    def test_list_from_board_slug(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import Board, Topic, TopicMeta

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
        topic_query_svc = self._make_one()
        self.assertEqual(
            topic_query_svc.list_from_board_slug("foo"),
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

    def test_list_from_board_slug_not_found(self):
        topic_query_svc = self._make_one()
        self.assertEqual(topic_query_svc.list_from_board_slug("notfound"), [])

    def test_list_recent_from_board_slug(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import Board, Topic, TopicMeta

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
        topic9 = _make_topic(hours=2, board=board1, title="Foo", status="archived")
        topic10 = _make_topic(days=7, board=board1, title="Foo")
        _make_topic(board=board2, title="Foo")
        _make_topic(days=7, hours=1, board=board1, title="Foo", status="archived")
        _make_topic(days=7, hours=1, board=board1, title="Foo", status="locked")
        _make_topic(days=8, board=board1, title="Foo")
        _make_topic(days=9, board=board1, title="Foo")
        self.dbsession.commit()
        topic_query_svc = self._make_one()
        self.assertEqual(
            topic_query_svc.list_recent_from_board_slug("foo"),
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
            ],
        )

    def test_list_recent_from_board_slug_not_found(self):
        topic_query_svc = self._make_one()
        self.assertEqual(topic_query_svc.list_recent_from_board_slug("notfound"), [])

    def test_list_expired_from_board_slug(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import Board, Topic, TopicMeta

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

        board1 = self._make(
            Board(title="Foo", slug="foo", settings={"expire_duration": 5})
        )
        board2 = self._make(
            Board(title="Bar", slug="bar", settings={"expire_duration": 5})
        )
        _make_topic(board=board1, title="Foo")
        _make_topic(days=1, board=board1, title="Foo")
        _make_topic(days=2, board=board1, title="Foo")
        _make_topic(days=3, board=board1, title="Foo")
        _make_topic(days=4, board=board1, title="Foo")
        topic6 = _make_topic(days=5, board=board1, title="Foo")
        topic7 = _make_topic(days=6, board=board1, title="Foo")
        _make_topic(days=7, board=board1, title="Foo", status="locked")
        _make_topic(days=6, board=board1, title="Foo", status="expired")
        _make_topic(days=6, board=board1, title="Foo", status="archived")
        topic11 = _make_topic(days=7, board=board1, title="Foo")
        _make_topic(days=7, board=board2, title="Foo")
        self.dbsession.commit()
        topic_query_svc = self._make_one()
        self.assertEqual(
            topic_query_svc.list_expired_from_board_slug("foo"),
            [topic6, topic7, topic11],
        )

    def test_list_expired_from_board_slug_posted_at(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import Board, Topic, TopicMeta

        def _make_topic(days=0, hours=0, **kwargs):
            topic = self._make(Topic(**kwargs))
            self._make(
                TopicMeta(
                    topic=topic,
                    post_count=0,
                    posted_at=func.now() - timedelta(days=days, hours=hours),
                    bumped_at=func.now(),
                )
            )
            return topic

        board1 = self._make(
            Board(title="Foo", slug="foo", settings={"expire_duration": 5})
        )
        board2 = self._make(
            Board(title="Bar", slug="bar", settings={"expire_duration": 5})
        )
        _make_topic(board=board1, title="Foo")
        _make_topic(days=1, board=board1, title="Foo")
        _make_topic(days=2, board=board1, title="Foo")
        _make_topic(days=3, board=board1, title="Foo")
        _make_topic(days=4, board=board1, title="Foo")
        _make_topic(days=5, board=board1, title="Foo")
        _make_topic(days=6, board=board1, title="Foo")
        _make_topic(days=7, board=board1, title="Foo", status="locked")
        _make_topic(days=6, board=board1, title="Foo", status="expired")
        _make_topic(days=6, board=board1, title="Foo", status="archived")
        _make_topic(days=7, board=board1, title="Foo")
        _make_topic(days=7, board=board2, title="Foo")
        self.dbsession.commit()
        topic_query_svc = self._make_one()
        self.assertEqual(topic_query_svc.list_expired_from_board_slug("foo"), [])

    def test_list_expired_from_board_slug_without_expiration(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import Board, Topic, TopicMeta

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

        board1 = self._make(
            Board(title="Foo", slug="foo", settings={"expire_duration": 0})
        )
        board2 = self._make(
            Board(title="Bar", slug="bar", settings={"expire_duration": 5})
        )
        _make_topic(board=board1, title="Foo")
        _make_topic(days=1, board=board1, title="Foo")
        _make_topic(days=2, board=board1, title="Foo")
        _make_topic(days=3, board=board1, title="Foo")
        _make_topic(days=4, board=board1, title="Foo")
        _make_topic(days=5, board=board1, title="Foo")
        _make_topic(days=6, board=board1, title="Foo")
        _make_topic(days=7, board=board1, title="Foo", status="locked")
        _make_topic(days=6, board=board1, title="Foo", status="expired")
        _make_topic(days=6, board=board1, title="Foo", status="archived")
        _make_topic(days=7, board=board1, title="Foo")
        _make_topic(days=7, board=board2, title="Foo")
        self.dbsession.commit()
        topic_query_svc = self._make_one()
        self.assertEqual(topic_query_svc.list_expired_from_board_slug("foo"), [])

    def test_list_expired_fom_board_slug_not_found(self):
        topic_query_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            topic_query_svc.list_expired_from_board_slug("notfound")

    def test_list_recent(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import Board, Topic, TopicMeta

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
        topic1 = _make_topic(hours=1, board=board1, title="Foo")
        topic2 = _make_topic(days=1, board=board1, title="Foo")
        topic3 = _make_topic(days=2, board=board1, title="Foo")
        topic4 = _make_topic(days=3, board=board1, title="Foo")
        topic5 = _make_topic(days=4, board=board1, title="Foo")
        topic6 = _make_topic(days=5, board=board1, title="Foo")
        topic7 = _make_topic(days=6, board=board1, title="Foo")
        topic8 = _make_topic(hours=2, board=board1, title="Foo", status="locked")
        topic9 = _make_topic(hours=3, board=board1, title="Foo", status="archived")
        topic10 = _make_topic(days=7, board=board1, title="Foo")
        topic11 = _make_topic(days=8, board=board1, title="Foo")
        topic12 = _make_topic(days=9, board=board1, title="Foo")
        topic13 = _make_topic(hours=4, board=board2, title="Foo")
        _make_topic(days=7, hours=1, board=board1, title="Foo", status="archived")
        _make_topic(days=7, hours=1, board=board1, title="Foo", status="locked")
        self.dbsession.commit()
        topic_query_svc = self._make_one()
        self.assertEqual(
            topic_query_svc.list_recent(_limit=20),
            [
                topic1,
                topic8,
                topic9,
                topic13,
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

    def test_topic_from_id(self):
        from ..models import Board, Topic

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self.dbsession.commit()
        topic_query_svc = self._make_one()
        self.assertEqual(topic_query_svc.topic_from_id(topic.id), topic)

    def test_topic_from_id_not_found(self):
        topic_query_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            topic_query_svc.topic_from_id(-1)


class TestTopicUpdateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import TopicUpdateService

        return TopicUpdateService

    def test_update(self):
        from ..models import Board, Topic

        board = self._make(Board(slug="foo", title="Foobar"))
        topic = self._make(Topic(board=board, title="Foobar Baz", status="open"))
        self.dbsession.commit()
        topic_update_svc = self._get_target_class()(self.dbsession)
        topic_update_svc.update(topic.id, status="locked")
        self.assertEqual(topic.status, "locked")

    def test_update_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound

        topic_update_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            topic_update_svc.update(-1, status="locked")
