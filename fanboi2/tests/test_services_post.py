import unittest
import unittest.mock

from sqlalchemy.orm.exc import NoResultFound

from . import ModelSessionMixin


class TestPostCreateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import PostCreateService

        return PostCreateService

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
        from ..models import Board, Topic, TopicMeta

        board = self._make(
            Board(slug="foo", title="Foo", settings={"name": "Nameless Foobar"})
        )
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create(topic.id, "Hello!", True, "127.0.0.1")
        self.assertEqual(post.number, 1)
        self.assertEqual(post.topic, topic)
        self.assertTrue(post.bumped)
        self.assertEqual(post.name, "Nameless Foobar")
        self.assertEqual(post.ip_address, "127.0.0.1")
        self.assertEqual(post.ident, "foo,127.0.0.1")
        self.assertEqual(post.ident_type, "ident")
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(topic_meta.post_count, 1)
        self.assertIsNotNone(topic_meta.bumped_at)

    def test_create_ipv6(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post1 = post_create_svc.create(topic.id, "Hello!", True, "fe80:c9cd::1")
        self.assertEqual(post1.ip_address, "fe80:c9cd::1")
        self.assertEqual(post1.ident, "foo,fe80:c9cd::/64")
        self.assertEqual(post1.ident_type, "ident_v6")
        post2 = post_create_svc.create(topic.id, "Hello!", True, "fe80:c9cd::96f0:1111")
        self.assertEqual(post2.ip_address, "fe80:c9cd::96f0:1111")
        self.assertEqual(post2.ident, "foo,fe80:c9cd::/64")
        self.assertEqual(post2.ident_type, "ident_v6")

    def test_create_without_bumped(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create(topic.id, "Hello!", False, "127.0.0.1")
        self.assertFalse(post.bumped)
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertIsNone(topic_meta.bumped_at)

    def test_create_without_ident(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(
            Board(slug="foo", title="Foo", settings={"use_ident": False})
        )
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create(topic.id, "Hello!", True, "127.0.0.1")
        self.assertIsNone(post.ident)
        self.assertEqual(post.ident_type, "none")

    def test_create_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound

        post_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            post_create_svc.create(-1, "Hello!", True, "127.0.0.1")

    def test_create_topic_limit(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(slug="foo", title="Foo", settings={"max_posts": 10}))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=9))
        self.dbsession.commit()
        self.assertEqual(topic.status, "open")
        post_create_svc = self._make_one()
        post = post_create_svc.create(topic.id, "Hello!", True, "127.0.0.1")
        topic = self.dbsession.query(Topic).get(topic.id)
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(post.number, 10)
        self.assertEqual(topic_meta.post_count, 10)
        self.assertEqual(topic.status, "archived")

    def test_create_topic_locked(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Hello", status="locked"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create(topic.id, "Hello!", True, "127.0.0.1")

    def test_create_topic_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Hello", status="archived"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create(topic.id, "Hello!", True, "127.0.0.1")

    def test_create_board_restricted(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(slug="foo", title="Foo", status="restricted"))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create(topic.id, "Hello!", True, "127.0.0.1")
        self.assertEqual(post.number, 1)

    def test_create_board_locked(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(slug="foo", title="Foo", status="locked"))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create(topic.id, "Hello!", True, "127.0.0.1")

    def test_create_board_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(slug="foo", title="Foo", status="archived"))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create(topic.id, "Hello!", True, "127.0.0.1")

    def test_create_with_user(self):
        from ..models import Board, Topic, TopicMeta, User

        board = self._make(
            Board(slug="foo", title="Foo", settings={"name": "Nameless Foobar"})
        )
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
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
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id, user.id, "Hello!", True, "127.0.0.1"
        )
        self.assertEqual(post.number, 1)
        self.assertEqual(post.topic, topic)
        self.assertTrue(post.bumped)
        self.assertEqual(post.name, "Root")
        self.assertEqual(post.ip_address, "127.0.0.1")
        self.assertEqual(post.ident, "fooident")
        self.assertEqual(post.ident_type, "ident_admin")
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(topic_meta.post_count, 1)
        self.assertIsNotNone(topic_meta.bumped_at)

    def test_create_with_user_without_bumped(self):
        from ..models import Board, Topic, TopicMeta, User

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
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
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id, user.id, "Hello!", False, "127.0.0.1"
        )
        self.assertFalse(post.bumped)
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertIsNone(topic_meta.bumped_at)

    def test_create_with_user_without_ident(self):
        from ..models import Board, Topic, TopicMeta, User

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
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id, user.id, "Hello!", True, "127.0.0.1"
        )
        self.assertEqual(post.ident, "fooident")
        self.assertEqual(post.ident_type, "ident_admin")

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
        post_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            post_create_svc.create_with_user(-1, user.id, "Hello!", True, "127.0.0.1")

    def test_create_with_user_not_found_user(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_create_svc = self._make_one()
        with self.assertRaises(NoResultFound):
            post_create_svc.create_with_user(topic.id, -1, "Hello!", True, "127.0.0.1")

    def test_create_with_user_topic_limit(self):
        from ..models import Board, Topic, TopicMeta, User

        board = self._make(Board(slug="foo", title="Foo", settings={"max_posts": 10}))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=9))
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
        self.assertEqual(topic.status, "open")
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id, user.id, "Hello!", True, "127.0.0.1"
        )
        topic = self.dbsession.query(Topic).get(topic.id)
        topic_meta = self.dbsession.query(TopicMeta).get(topic.id)
        self.assertEqual(post.number, 10)
        self.assertEqual(topic_meta.post_count, 10)
        self.assertEqual(topic.status, "archived")

    def test_create_with_user_topic_locked(self):
        from ..models import Board, Topic, TopicMeta, User

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Hello", status="locked"))
        self._make(TopicMeta(topic=topic, post_count=0))
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
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id, user.id, "Hello!", True, "127.0.0.1"
        )
        self.assertEqual(post.number, 1)

    def test_create_with_user_topic_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta, User

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Hello", status="archived"))
        self._make(TopicMeta(topic=topic, post_count=0))
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
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create_with_user(
                topic.id, user.id, "Hello!", True, "127.0.0.1"
            )

    def test_create_with_user_board_restricted(self):
        from ..models import Board, Topic, TopicMeta, User

        board = self._make(Board(slug="foo", title="Foo", status="restricted"))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
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
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id, user.id, "Hello!", True, "127.0.0.1"
        )
        self.assertEqual(post.number, 1)

    def test_create_with_user_board_locked(self):
        from ..models import Board, Topic, TopicMeta, User

        board = self._make(Board(slug="foo", title="Foo", status="locked"))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
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
        post_create_svc = self._make_one()
        post = post_create_svc.create_with_user(
            topic.id, user.id, "Hello!", True, "127.0.0.1"
        )
        self.assertEqual(post.number, 1)

    def test_create_with_user_board_archived(self):
        from ..errors import StatusRejectedError
        from ..models import Board, Topic, TopicMeta, User

        board = self._make(Board(slug="foo", title="Foo", status="archived"))
        topic = self._make(Topic(board=board, title="Hello", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
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
        post_create_svc = self._make_one()
        with self.assertRaises(StatusRejectedError):
            post_create_svc.create_with_user(
                topic.id, user.id, "Hello!", True, "127.0.0.1"
            )


class TestPostDeleteService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import PostDeleteService

        return PostDeleteService

    def test_delete_from_topic_id(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic, TopicMeta, Post

        board = self._make(Board(slug="foo", title="Foobar"))
        topic = self._make(Topic(board=board, title="Foobar Baz"))
        self._make(TopicMeta(topic=topic, post_count=2))
        post1 = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Foobar",
                body="Foobar Baz",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic,
                number=2,
                name="Nameless Foobar",
                body="Second Post",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic,
                number=3,
                name="Nameless Foobar",
                body="Third time the charm",
                ip_address="127.0.0.1",
            )
        )
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

        board = self._make(Board(slug="foo", title="Foobar"))
        topic = self._make(Topic(board=board, title="Foobar Baz"))
        self._make(TopicMeta(topic=topic, post_count=2))
        self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Foobar",
                body="Foobar Baz",
                ip_address="127.0.0.1",
            )
        )
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

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Foo", status="open"))
        self._make(TopicMeta(topic=topic, post_count=50))
        posts = []
        for i in range(50):
            posts.append(
                self._make(
                    Post(
                        topic=topic,
                        number=i + 1,
                        name="Nameless Fanboi",
                        body="Foobar",
                        ip_address="127.0.0.1",
                    )
                )
            )
        topic2 = self._make(Topic(board=board, title="Bar", status="open"))
        self._make(TopicMeta(topic=topic2, post_count=1))
        post2 = self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Hi",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        post_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id), posts)
        self.assertEqual(post_query_svc.list_from_topic_id(topic2.id), [post2])
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id, "1"), posts[0:1])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, "50"), posts[49:50]
        )
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id, "51"), [])
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id, "1-50"), posts)
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, "10-20"), posts[9:20]
        )
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id, "51-99"), [])
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id, "0-51"), posts)
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id, "-0"), [])
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id, "-5"), posts[:5])
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id, "45-"), posts[44:])
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id, "100-"), [])
        self.assertEqual(
            post_query_svc.list_from_topic_id(topic.id, "recent"), posts[20:]
        )
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id, "l30"), posts[20:])

    def test_list_from_topic_id_without_posts(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Foo", status="open"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        post_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(post_query_svc.list_from_topic_id(topic.id), [])

    def test_list_from_topic_id_not_found(self):
        post_query_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            post_query_svc.list_from_topic_id(-1)

    def test_was_recently_seen(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import Board, Topic, TopicMeta, Post

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Foo", status="open"))
        self._make(TopicMeta(topic=topic, post_count=1))
        self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Hi",
                ip_address="127.0.0.1",
                created_at=func.now() - timedelta(days=2),
            )
        )
        self.dbsession.commit()
        post_query_svc = self._get_target_class()(self.dbsession)
        self.assertTrue(post_query_svc.was_recently_seen("127.0.0.1"))

    def test_was_recently_seen_not_recent(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import Board, Topic, TopicMeta, Post

        board = self._make(Board(slug="foo", title="Foo"))
        topic = self._make(Topic(board=board, title="Foo", status="open"))
        self._make(TopicMeta(topic=topic, post_count=1))
        self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Hi",
                ip_address="127.0.0.1",
                created_at=func.now() - timedelta(days=4),
            )
        )
        self.dbsession.commit()
        post_query_svc = self._get_target_class()(self.dbsession)
        self.assertFalse(post_query_svc.was_recently_seen("127.0.0.1"))
