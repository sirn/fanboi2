import unittest
import unittest.mock

from . import ModelSessionMixin


class TestBanwordCreateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import BanwordCreateService

        return BanwordCreateService

    def test_create(self):
        banword_create_svc = self._get_target_class()(self.dbsession)
        banword = banword_create_svc.create(
            r"https?:\/\/bit\.ly",
            description="no shortlinks",
            scope="board:foo",
            active=True,
        )
        self.assertEqual(banword.expr, r"https?:\/\/bit\.ly")
        self.assertEqual(banword.description, "no shortlinks")
        self.assertEqual(banword.scope, "board:foo")
        self.assertTrue(banword.active)

    def test_create_without_optional_fields(self):
        banword_create_svc = self._get_target_class()(self.dbsession)
        banword = banword_create_svc.create(r"https?:\/\/bit\.ly")
        self.assertIsNone(banword.description)
        self.assertIsNone(banword.scope)
        self.assertTrue(banword.active)

    def test_create_with_empty_fields(self):
        banword_create_svc = self._get_target_class()(self.dbsession)
        banword = banword_create_svc.create("", description="", scope="", active="")
        self.assertIsNone(banword.expr)
        self.assertIsNone(banword.description)
        self.assertIsNone(banword.scope)
        self.assertFalse(banword.active)

    def test_create_deactivated(self):
        banword_create_svc = self._get_target_class()(self.dbsession)
        banword = banword_create_svc.create(r"https?:\/\/bit\.ly", active=False)
        self.assertFalse(banword.active)


class TestBanwordQueryService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import BanwordQueryService

        return BanwordQueryService

    def _make_one(self, retval=True):
        class _DummyScopeService(object):
            def evaluate(self, _scope, _obj):
                return retval

        return self._get_target_class()(self.dbsession, _DummyScopeService())

    def test_list_active(self):
        from ..models import Banword

        banword1 = self._make(Banword(expr=r"https?:\/\/bit\.ly"))
        banword2 = self._make(Banword(expr=r"https?:\/\/goo\.gl"))
        self._make(Banword(expr=r"https?:\/\/youtu\.be", active=False))
        self._make(Banword(expr=r"https?:\/\/example\.com", active=False))
        self.dbsession.commit()
        banword_query_svc = self._make_one()
        self.assertEqual(banword_query_svc.list_active(), [banword2, banword1])

    def test_list_inactive(self):
        from ..models import Banword

        self._make(Banword(expr=r"https?:\/\/bit\.ly"))
        self._make(Banword(expr=r"https?:\/\/goo\.gl"))
        banword3 = self._make(Banword(expr=r"https?:\/\/youtu\.be", active=False))
        banword4 = self._make(Banword(expr=r"https?:\/\/example\.com", active=False))
        self.dbsession.commit()
        banword_query_svc = self._make_one()
        self.assertEqual(banword_query_svc.list_inactive(), [banword4, banword3])

    def test_is_banned(self):
        from ..models import Banword

        self._make(Banword(expr=r"https?:\/\/bit\.ly", scope="foo:bar"))
        self._make(Banword(expr=r"https?:\/\/goo\.gl"))
        self.dbsession.commit()
        banword_query_svc = self._make_one(True)
        self.assertTrue(
            banword_query_svc.is_banned("a\nb\nhttps://bit.ly/Spam\nd", {"foo": "bar"})
        )
        self.assertTrue(banword_query_svc.is_banned("a\nb\nhttps://goo.gl/Spam\nd"))
        self.assertTrue(banword_query_svc.is_banned("a\nb\nhttps://bit.ly/Spam\nd"))

    def test_is_banned_non_scope(self):
        from ..models import Banword

        self._make(Banword(expr=r"https?:\/\/bit\.ly", scope="foo:bar"))
        self.dbsession.commit()
        banword_query_svc = self._make_one(False)
        self.assertFalse(
            banword_query_svc.is_banned("a\nb\nhttps://bit.ly/Spam\nd", {"foo": "bar"})
        )
        self.assertFalse(banword_query_svc.is_banned("a\nb\nhttps://bit.ly/Spam\nd"))
        self.assertFalse(banword_query_svc.is_banned("a\nb\nhttps://goo.gl/Spam\nd"))

    def test_is_banned_unset(self):
        from ..models import Banword

        self._make(Banword(expr=r"https?:\/\/goo\.gl"))
        self._make(Banword(expr=r"https?:\/\/bit\.ly"))
        self.dbsession.commit()
        banword_query_svc = self._make_one(True)
        self.assertTrue(
            banword_query_svc.is_banned("a\nb\nhttps://goo.gl/Spam\nd", {"foo": "bar"})
        )
        self.assertTrue(
            banword_query_svc.is_banned("a\nb\nhttps://bit.ly/Spam\nd", {"foo": "bar"})
        )

    def test_is_banned_inactive(self):
        from ..models import Banword

        self._make(Banword(expr=r"https?:\/\/bit\.ly", active=False))
        self._make(Banword(expr=r"https?:\/\/goo\.gl", active=False))
        self.dbsession.commit()
        banword_query_svc = self._make_one(True)
        self.assertFalse(banword_query_svc.is_banned("a\nb\nhttps://bit.ly/Spam\nd"))
        self.assertFalse(banword_query_svc.is_banned("a\nb\nhttps://goo.gl/Spam\nd"))

    def test_banword_from_id(self):
        from ..models import Banword

        banword = self._make(Banword(expr=r"https?:\/\/bit\.ly"))
        self.dbsession.commit()
        banword_query_svc = self._make_one()
        self.assertEqual(banword_query_svc.banword_from_id(banword.id), banword)


class TestBanwordUpdateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import BanwordUpdateService

        return BanwordUpdateService

    def test_update(self):
        from ..models import Banword

        banword = self._make(
            Banword(
                expr=r"https?:\/\/bit\.ly",
                description="no shortlinks",
                scope="board:foo",
                active=True,
            )
        )
        self.dbsession.commit()
        banword_update_svc = self._get_target_class()(self.dbsession)
        banword = banword_update_svc.update(
            banword.id,
            expr=r"https?:\/\/(bit\.ly|goo\.gl)",
            description="no any shortlinks",
            scope="board:bar",
            active=False,
        )
        self.assertEqual(banword.expr, r"https?:\/\/(bit\.ly|goo\.gl)")
        self.assertEqual(banword.description, "no any shortlinks")
        self.assertEqual(banword.scope, "board:bar")
        self.assertFalse(banword.active)

    def test_update_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound

        banword_update_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            banword_update_svc.update(-1, active=False)

    def test_update_none(self):
        from ..models import Banword

        banword = self._make(
            Banword(
                expr=r"https?:\/\/bit\.ly",
                description="no shortlinks",
                scope="board:foo",
                active=True,
            )
        )
        self.dbsession.commit()
        banword_update_svc = self._get_target_class()(self.dbsession)
        banword = banword_update_svc.update(
            banword.id, expr=None, description=None, scope=None, active=None
        )
        self.assertIsNone(banword.expr)
        self.assertIsNone(banword.description)
        self.assertIsNone(banword.scope)
        self.assertFalse(banword.active)

    def test_update_empty(self):
        from ..models import Banword

        banword = self._make(
            Banword(
                expr=r"https?:\/\/bit\.ly",
                description="no shortlinks",
                scope="board:foo",
                active=True,
            )
        )
        self.dbsession.commit()
        banword_update_svc = self._get_target_class()(self.dbsession)
        banword = banword_update_svc.update(
            banword.id, expr="", description="", scope="", active=""
        )
        self.assertIsNone(banword.expr)
        self.assertIsNone(banword.description)
        self.assertIsNone(banword.scope)
        self.assertFalse(banword.active)
