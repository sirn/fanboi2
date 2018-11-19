import unittest
import unittest.mock

from sqlalchemy.orm.exc import NoResultFound

from . import ModelSessionMixin


class TestUserCreateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import UserCreateService

        return UserCreateService

    def _make_one(self):
        class _DummyIdentityService(object):
            def identity_for(self, **kwargs):
                return "id=" + ",".join("%s" % (v,) for k, v in sorted(kwargs.items()))

        return self._get_target_class()(self.dbsession, _DummyIdentityService())

    def test_create(self):
        from passlib.hash import argon2
        from ..models import User, Group

        group1 = self._make(Group(name="admin"))
        group2 = self._make(Group(name="mod"))
        user1 = self._make(
            User(
                username="root",
                encrypted_password="none",
                ident="fooident",
                ident_type="ident_admin",
                name="Root",
                groups=[group1],
            )
        )
        self.dbsession.commit()
        user_create_svc = self._make_one()
        user2 = user_create_svc.create(
            user1.id, "child", "passw0rd", "Child", ["mod", "janitor"]
        )
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(Group).count(), 3)
        group3 = self.dbsession.query(Group).filter_by(name="janitor").first()
        self.assertEqual(user2.parent, user1)
        self.assertEqual(user2.username, "child")
        self.assertEqual(user2.ident, "id=child")
        self.assertEqual(user2.ident_type, "ident")
        self.assertEqual(user2.name, "Child")
        self.assertEqual(user2.groups, [group3, group2])
        self.assertTrue(argon2.verify("passw0rd", user2.encrypted_password))

    def test_create_root(self):
        from ..models import Group

        user_create_svc = self._make_one()
        user = user_create_svc.create(None, "root", "passw0rd", "Root", ["admin"])
        self.assertEqual(self.dbsession.query(Group).count(), 1)
        group = self.dbsession.query(Group).filter_by(name="admin").first()
        self.assertIsNone(user.parent)
        self.assertEqual(user.username, "root")
        self.assertEqual(user.ident, "id=root")
        self.assertEqual(user.ident_type, "ident_admin")
        self.assertEqual(user.name, "Root")
        self.assertEqual(user.groups, [group])

    def test_create_without_group(self):
        from ..models import Group

        user_create_svc = self._make_one()
        user = user_create_svc.create(None, "root", "passw0rd", "Root", [])
        self.assertEqual(self.dbsession.query(Group).count(), 0)
        self.assertEqual(user.parent, None)
        self.assertEqual(user.username, "root")
        self.assertEqual(user.ident, "id=root")
        self.assertEqual(user.ident_type, "ident")
        self.assertEqual(user.name, "Root")
        self.assertEqual(user.groups, [])


class TestUserLoginService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import UserLoginService

        return UserLoginService

    def test_authenticate(self):
        from passlib.hash import argon2
        from ..models import User

        self._make(
            User(
                username="foo",
                encrypted_password=argon2.hash("passw0rd"),
                ident="foo",
                name="Nameless User",
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertTrue(user_login_svc.authenticate("foo", "passw0rd"))
        self.assertFalse(user_login_svc.authenticate("foo", "password"))

    def test_authenticate_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertFalse(user_login_svc.authenticate("foo", "passw0rd"))

    def test_authenticate_deactivated(self):
        from passlib.hash import argon2
        from ..models import User

        self._make(
            User(
                username="foo",
                encrypted_password=argon2.hash("passw0rd"),
                ident="foo",
                name="Nameless User",
                deactivated=True,
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertFalse(user_login_svc.authenticate("foo", "passw0rd"))

    def test_authenticate_upgrade(self):
        from passlib.hash import argon2
        from ..models import User

        password = argon2.using(rounds=2).hash("passw0rd")
        user = self._make(
            User(
                username="foo",
                encrypted_password=password,
                ident="foo",
                name="Nameless User",
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertTrue(user_login_svc.authenticate("foo", "passw0rd"))
        self.assertNotEqual(password, user.encrypted_password)
        password_new = user.encrypted_password
        self.assertTrue(user_login_svc.authenticate("foo", "passw0rd"))
        self.assertEqual(password_new, user.encrypted_password)

    def test_user_from_token(self):
        from datetime import datetime
        from ..models import User, UserSession

        user1 = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
            )
        )
        user2 = self._make(
            User(
                username="bar",
                encrypted_password="none",
                ident="bar",
                name="Nameless Bar",
            )
        )
        self._make(
            UserSession(
                user=user1,
                token="foo_token1",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self._make(
            UserSession(
                user=user1,
                token="foo_token2",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self._make(
            UserSession(
                user=user2,
                token="bar_token1",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_login_svc.user_from_token("foo_token1", "127.0.0.1"), user1
        )
        self.assertEqual(
            user_login_svc.user_from_token("foo_token2", "127.0.0.1"), user1
        )
        self.assertEqual(
            user_login_svc.user_from_token("bar_token1", "127.0.0.1"), user2
        )

    def test_user_from_token_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.user_from_token("notexists", "127.0.0.1"))

    def test_user_from_token_never_seen(self):
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
                deactivated=True,
            )
        )
        self._make(
            UserSession(
                user=user, token="foo_token1", ip_address="127.0.0.1", last_seen_at=None
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.user_from_token("foo_token", "127.0.0.1"))

    def test_user_from_token_deactivated(self):
        from datetime import datetime
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
                deactivated=True,
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token1",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.user_from_token("foo_token", "127.0.0.1"))

    def test_user_from_token_wrong_ip(self):
        from datetime import datetime
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token1",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.user_from_token("foo_token", "127.0.0.2"))

    def test_user_from_token_revoked(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token1",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
                revoked_at=datetime.now() + timedelta(hours=1),
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token2",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now() - timedelta(hours=1, minutes=15),
                revoked_at=datetime.now() - timedelta(hours=1),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_login_svc.user_from_token("foo_token1", "127.0.0.1"), user
        )
        self.assertIsNone(user_login_svc.user_from_token("foo_token2", "127.0.0.1"))

    def test_groups_from_token(self):
        from datetime import datetime
        from ..models import User, UserSession, Group

        group1 = self._make(Group(name="foo"))
        group2 = self._make(Group(name="bar"))
        user1 = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
                groups=[group1, group2],
            )
        )
        user2 = self._make(
            User(
                username="bar",
                encrypted_password="none",
                ident="foo",
                name="Nameless Bar",
                groups=[group2],
            )
        )
        user3 = self._make(
            User(
                username="baz",
                encrypted_password="none",
                ident="baz",
                name="Nameless Baz",
                groups=[],
            )
        )
        self._make(
            UserSession(
                user=user1,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self._make(
            UserSession(
                user=user2,
                token="bar_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self._make(
            UserSession(
                user=user3,
                token="baz_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_login_svc.groups_from_token("foo_token", "127.0.0.1"), ["bar", "foo"]
        )
        self.assertEqual(
            user_login_svc.groups_from_token("bar_token", "127.0.0.1"), ["bar"]
        )
        self.assertEqual(user_login_svc.groups_from_token("baz_token", "127.0.0.1"), [])

    def test_groups_from_token_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.groups_from_token("notexists", "127.0.0.1"))

    def test_groups_from_token_wrong_ip(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession, Group

        group1 = self._make(Group(name="foo"))
        group2 = self._make(Group(name="bar"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
                groups=[group1, group2],
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
                revoked_at=datetime.now() + timedelta(hours=1),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.groups_from_token("foo_token", "127.0.0.2"))

    def test_groups_from_token_never_seen(self):
        from ..models import User, UserSession, Group

        group1 = self._make(Group(name="foo"))
        group2 = self._make(Group(name="bar"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
                groups=[group1, group2],
                deactivated=True,
            )
        )
        self._make(UserSession(user=user, token="foo_token", ip_address="127.0.0.1"))
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.groups_from_token("foo_token", "127.0.0.1"))

    def test_groups_from_token_deactivated(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession, Group

        group1 = self._make(Group(name="foo"))
        group2 = self._make(Group(name="bar"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
                groups=[group1, group2],
                deactivated=True,
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
                revoked_at=datetime.now() + timedelta(hours=1),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.groups_from_token("foo_token", "127.0.0.1"))

    def test_groups_from_token_revoked(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession, Group

        group1 = self._make(Group(name="foo"))
        group2 = self._make(Group(name="bar"))
        user1 = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
                groups=[group1, group2],
            )
        )
        user2 = self._make(
            User(
                username="bar",
                encrypted_password="none",
                ident="bar",
                name="Nameless Bar",
                groups=[group2],
            )
        )
        self._make(
            UserSession(
                user=user1,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
                revoked_at=datetime.now() + timedelta(hours=1),
            )
        )
        self._make(
            UserSession(
                user=user2,
                token="bar_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now() - timedelta(hours=1, minutes=15),
                revoked_at=datetime.now() - timedelta(hours=1),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_login_svc.groups_from_token("foo_token", "127.0.0.1"), ["bar", "foo"]
        )
        self.assertIsNone(user_login_svc.groups_from_token("bar_token", "127.0.0.1"))

    def test_revoke_token(self):
        from datetime import datetime
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
            )
        )
        user_session = self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self.dbsession.commit()
        self.assertIsNone(user_session.revoked_at)
        user_login_svc = self._get_target_class()(self.dbsession)
        user_login_svc.revoke_token("foo_token", "127.0.0.1")
        self.assertIsNotNone(user_session.revoked_at)

    def test_revoke_token_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.revoke_token("notexists", "127.0.0.1"))

    def test_revoke_token_wrong_ip(self):
        from datetime import datetime
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.revoke_token("notexists", "127.0.0.2"))

    def test_revoke_token_revoked(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now() - timedelta(hours=1, minutes=15),
                revoked_at=datetime.now() - timedelta(hours=1),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.revoke_token("foo_token", "127.0.0.1"))

    def test_mark_seen(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession

        anchor = datetime.now() - timedelta(minutes=15)
        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
            )
        )
        user_session = self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=anchor,
            )
        )
        self.dbsession.commit()
        self.assertIsNotNone(user_session.last_seen_at)
        self.assertIsNone(user_session.revoked_at)
        user_login_svc = self._get_target_class()(self.dbsession)
        user_login_svc.mark_seen("foo_token", "127.0.0.1", 3600)
        self.assertGreater(user_session.last_seen_at, anchor)
        self.assertIsNotNone(user_session.revoked_at)

    def test_mark_seen_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.mark_seen("notexists", "127.0.0.1", 3600))

    def test_mark_seen_wrong_ip(self):
        from datetime import datetime
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.mark_seen("foo_token", "127.0.0.2", 3600))

    def test_mark_seen_deactivated(self):
        from datetime import datetime
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
                deactivated=True,
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.mark_seen("foo_token", "127.0.0.1", 3600))

    def test_mark_seen_revoked(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
            )
        )
        self._make(
            UserSession(
                user=user,
                token="foo_token",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now() - timedelta(hours=1, minutes=15),
                revoked_at=datetime.now() - timedelta(hours=1),
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        self.assertIsNone(user_login_svc.mark_seen("foo_token", "127.0.0.1", 3600))

    def test_token_for(self):
        from ..models import User

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
            )
        )
        self.dbsession.commit()
        user_login_svc = self._get_target_class()(self.dbsession)
        user_token = user_login_svc.token_for("foo", "127.0.0.1")
        self.assertEqual(user_login_svc.user_from_token(user_token, "127.0.0.1"), user)

    def test_token_for_not_found(self):
        user_login_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            user_login_svc.token_for("notexists", "127.0.0.1")

    def test_token_for_deactivated(self):
        from ..models import User

        self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
                deactivated=True,
            )
        )
        user_login_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            user_login_svc.token_for("foo", "127.0.0.1")


class TestUserQueryService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import UserQueryService

        return UserQueryService

    def test_user_from_id(self):
        from ..models import User

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                name="Nameless User",
            )
        )
        self.dbsession.commit()
        user_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(user_query_svc.user_from_id(user.id), user)

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

        user1 = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                ident_type="ident_admin",
                name="Nameless Foo",
            )
        )
        user2 = self._make(
            User(
                username="baz",
                encrypted_password="none",
                ident="baz",
                ident_type="ident_admin",
                name="Nameless Baz",
            )
        )
        user_session1 = self._make(
            UserSession(
                user=user1,
                token="user1_token1",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now() - timedelta(days=2),
            )
        )
        user_session2 = self._make(
            UserSession(
                user=user1,
                token="user1_token2",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now() - timedelta(days=3),
            )
        )
        user_session3 = self._make(
            UserSession(
                user=user1,
                token="user1_token3",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now() - timedelta(days=1),
            )
        )
        self._make(
            UserSession(
                user=user2,
                token="user2_token1",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now(),
            )
        )
        self.dbsession.commit()
        user_session_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            user_session_query_svc.list_recent_from_user_id(user1.id),
            [user_session3, user_session1, user_session2],
        )

    def test_list_recent_from_user_id_empty(self):
        from ..models import User

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                ident_type="ident_admin",
                name="Nameless Foo",
            )
        )
        self.dbsession.commit()
        user_session_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(user_session_query_svc.list_recent_from_user_id(user.id), [])

    def test_list_recent_from_user_id_not_found(self):
        user_session_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(user_session_query_svc.list_recent_from_user_id(-1), [])
