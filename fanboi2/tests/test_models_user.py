import unittest

from . import ModelSessionMixin


class TestUserModel(ModelSessionMixin, unittest.TestCase):
    def test_relations(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession, Group

        group1 = self._make(Group(name="foo"))
        group2 = self._make(Group(name="bar"))
        user1 = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="fooident",
                name="Nameless Foo",
                groups=[group1, group2],
            )
        )
        user2 = self._make(
            User(
                username="foo1",
                parent=user1,
                encrypted_password="none",
                ident="foo1ident",
                name="Nameless Foo1",
                groups=[group1],
            )
        )
        user3 = self._make(
            User(
                username="foo2",
                parent=user1,
                encrypted_password="none",
                ident="foo2ident",
                name="Nameless Foo2",
                groups=[group2],
            )
        )
        user4 = self._make(
            User(
                username="foo3",
                parent=user2,
                ident="foo3ident",
                name="Nameless Foo3",
                encrypted_password="none",
            )
        )
        session1 = self._make(
            UserSession(
                user=user1,
                token="test1",
                ip_address="127.0.0.1",
                created_at=datetime.now() - timedelta(days=1),
            )
        )
        session2 = self._make(
            UserSession(user=user1, token="test2", ip_address="127.0.0.1")
        )
        session3 = self._make(
            UserSession(user=user2, token="test3", ip_address="127.0.0.1")
        )
        self.dbsession.commit()
        self.assertEqual(list(user1.children), [user2, user3])
        self.assertEqual(list(user2.children), [user4])
        self.assertEqual(list(user3.children), [])
        self.assertEqual(list(user4.children), [])
        self.assertEqual(list(user1.sessions), [session2, session1])
        self.assertEqual(list(user2.sessions), [session3])
        self.assertEqual(list(user3.sessions), [])
        self.assertEqual(list(user4.sessions), [])
        self.assertEqual(list(user1.groups), [group2, group1])
        self.assertEqual(list(user2.groups), [group1])
        self.assertEqual(list(user3.groups), [group2])
        self.assertEqual(list(user4.groups), [])
        self.assertIsNone(user1.parent)
        self.assertEqual(user2.parent, user1)
        self.assertEqual(user3.parent, user1)

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        from ..models import User, UserSession, Group

        group1 = self._make(Group(name="foo1"))
        group2 = self._make(Group(name="foo2"))
        user1 = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="fooident",
                name="Nameless Foo",
                groups=[group1],
            )
        )
        user2 = self._make(
            User(
                username="foo1",
                parent=user1,
                encrypted_password="none",
                ident="foo1ident",
                name="Nameless Foo1",
                groups=[group2],
            )
        )
        user3 = self._make(
            User(
                username="foo2",
                parent=user1,
                encrypted_password="none",
                ident="foo2ident",
                name="Nameless Foo2",
            )
        )
        user4 = self._make(
            User(
                username="foo3",
                parent=user2,
                encrypted_password="none",
                ident="foo3ident",
                name="Nameless Foo3",
            )
        )
        session1 = self._make(
            UserSession(user=user1, token="test1", ip_address="127.0.0.1")
        )
        session2 = self._make(
            UserSession(user=user2, token="test2", ip_address="127.0.0.1")
        )
        session3 = self._make(
            UserSession(user=user2, token="test3", ip_address="127.0.0.1")
        )
        session4 = self._make(
            UserSession(user=user3, token="test4", ip_address="127.0.0.1")
        )
        session5 = self._make(
            UserSession(user=user4, token="test5", ip_address="127.0.0.1")
        )
        self.dbsession.commit()
        self.dbsession.delete(user2)
        self.dbsession.commit()
        self.assertTrue(inspect(user2).was_deleted)
        self.assertTrue(inspect(user4).was_deleted)
        self.assertTrue(inspect(session2).was_deleted)
        self.assertTrue(inspect(session3).was_deleted)
        self.assertTrue(inspect(session5).was_deleted)
        self.assertFalse(inspect(user1).was_deleted)
        self.assertFalse(inspect(user3).was_deleted)
        self.assertFalse(inspect(group1).was_deleted)
        self.assertFalse(inspect(group2).was_deleted)
        self.assertFalse(inspect(session1).was_deleted)
        self.assertFalse(inspect(session4).was_deleted)
