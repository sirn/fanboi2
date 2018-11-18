import unittest

from . import ModelSessionMixin


class TestGroupModel(ModelSessionMixin, unittest.TestCase):
    def test_relations(self):
        from ..models import Group, User

        group1 = self._make(Group(name="foo"))
        group2 = self._make(Group(name="bar"))
        user1 = self._make(
            User(
                username="foo",
                encrypted_password="dummy",
                ident="fooident",
                name="Nameless Foo",
                groups=[group1, group2],
            )
        )
        user2 = self._make(
            User(
                username="foo2",
                encrypted_password="dummy",
                ident="foo2ident",
                name="Nameless Foo2",
                groups=[group1],
            )
        )
        user3 = self._make(
            User(
                username="foo3",
                encrypted_password="dummy",
                ident="foo3ident",
                name="Nameless Foo3",
                groups=[group2],
            )
        )
        self.dbsession.commit()
        self.assertEqual(list(group1.users), [user1, user2])
        self.assertEqual(list(group2.users), [user1, user3])

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        from ..models import Group, User

        group = self._make(Group(name="foo"))
        user1 = self._make(
            User(
                username="foo",
                encrypted_password="dummy",
                ident="fooident",
                name="Nameless Foo",
                groups=[group],
            )
        )
        user2 = self._make(
            User(
                username="foo2",
                encrypted_password="dummy",
                ident="foo2ident",
                name="Nameless Foo2",
                groups=[group],
            )
        )
        self.dbsession.commit()
        self.dbsession.delete(group)
        self.dbsession.commit()
        self.assertTrue(inspect(group).was_deleted)
        self.assertFalse(inspect(user1).was_deleted)
        self.assertFalse(inspect(user2).was_deleted)
