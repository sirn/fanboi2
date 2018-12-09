import unittest

from . import ModelSessionMixin


class TestUserSessionModel(ModelSessionMixin, unittest.TestCase):
    def test_relations(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="fooident",
                name="Nameless Foo",
            )
        )
        session1 = self._make(
            UserSession(
                user=user,
                token="test1",
                ip_address="127.0.0.1",
                created_at=func.now() - timedelta(days=1),
            )
        )
        session2 = self._make(
            UserSession(user=user, token="test2", ip_address="127.0.0.1")
        )
        self.dbsession.commit()
        self.assertEqual(session1.user, user)
        self.assertEqual(session2.user, user)
        self.assertEqual(list(user.sessions), [session2, session1])

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        from ..models import User, UserSession

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="fooident",
                name="Nameless Foo",
            )
        )
        session = self._make(
            UserSession(user=user, token="test1", ip_address="127.0.0.1")
        )
        self.dbsession.commit()
        self.dbsession.delete(session)
        self.dbsession.commit()
        self.assertTrue(inspect(session).was_deleted)
        self.assertFalse(inspect(user).was_deleted)
