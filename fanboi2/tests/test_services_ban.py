import unittest
import unittest.mock

from . import ModelSessionMixin


class TestBanCreateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import BanCreateService

        return BanCreateService

    def test_create(self):
        from datetime import datetime, timedelta

        ban_create_svc = self._get_target_class()(self.dbsession)
        ban = ban_create_svc.create(
            "10.0.1.0/24",
            description="Violation of galactic law.",
            duration=30,
            scope="galaxy_far_away",
            active=True,
        )
        self.assertEqual(ban.ip_address, "10.0.1.0/24")
        self.assertEqual(ban.description, "Violation of galactic law.")
        self.assertEqual(ban.scope, "galaxy_far_away")
        self.assertGreaterEqual(
            ban.active_until, datetime.now() + timedelta(days=29, hours=23)
        )
        self.assertTrue(ban.active)

    def test_create_without_optional_fields(self):
        ban_create_svc = self._get_target_class()(self.dbsession)
        ban = ban_create_svc.create("10.0.1.0/24")
        self.assertEqual(ban.ip_address, "10.0.1.0/24")
        self.assertIsNone(ban.description)
        self.assertIsNone(ban.scope)
        self.assertIsNone(ban.active_until)
        self.assertTrue(ban.active)

    def test_create_with_empty_fields(self):
        ban_create_svc = self._get_target_class()(self.dbsession)
        ban = ban_create_svc.create(
            "10.0.1.0/24", description="", duration="", scope="", active=""
        )
        self.assertIsNone(ban.scope)
        self.assertIsNone(ban.active_until)
        self.assertIsNone(ban.scope)
        self.assertFalse(ban.active)

    def test_create_deactivated(self):
        ban_create_svc = self._get_target_class()(self.dbsession)
        ban = ban_create_svc.create("10.0.1.0/24", active=False)
        self.assertFalse(ban.active)


class TestBanQueryService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import BanQueryService

        return BanQueryService

    def test_list_active(self):
        from datetime import datetime, timedelta
        from ..models import Ban

        ban1 = self._make(
            Ban(
                ip_address="10.0.1.0/24",
                active_until=datetime.now() + timedelta(hours=1),
            )
        )
        self._make(
            Ban(
                ip_address="10.0.2.0/24",
                active_until=datetime.now() - timedelta(hours=1),
            )
        )
        ban3 = self._make(Ban(ip_address="10.0.3.0/24"))
        self._make(Ban(ip_address="10.0.3.0/24", active=False))
        ban5 = self._make(
            Ban(
                ip_address="10.0.3.0/24",
                active_until=datetime.now() + timedelta(hours=2),
            )
        )
        ban6 = self._make(
            Ban(
                ip_address="10.0.3.0/24",
                created_at=datetime.now() + timedelta(minutes=5),
            )
        )
        self.dbsession.commit()
        ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(ban_query_svc.list_active(), [ban6, ban3, ban5, ban1])

    def test_list_inactive(self):
        from datetime import datetime, timedelta
        from ..models import Ban

        self._make(
            Ban(
                ip_address="10.0.1.0/24",
                active_until=datetime.now() + timedelta(hours=1),
            )
        )
        ban2 = self._make(
            Ban(
                ip_address="10.0.2.0/24",
                active_until=datetime.now() - timedelta(hours=1),
            )
        )
        self._make(Ban(ip_address="10.0.3.0/24"))
        ban4 = self._make(Ban(ip_address="10.0.3.0/24", active=False))
        ban5 = self._make(
            Ban(
                ip_address="10.0.3.0/24",
                active_until=datetime.now() - timedelta(hours=2),
            )
        )
        ban6 = self._make(
            Ban(
                ip_address="10.0.3.0/24",
                created_at=datetime.now() + timedelta(minutes=5),
                active=False,
            )
        )
        self.dbsession.commit()
        ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(ban_query_svc.list_inactive(), [ban6, ban4, ban2, ban5])

    def test_is_banned(self):
        from ..models import Ban

        self._make(Ban(ip_address="10.0.1.0/24"))
        self.dbsession.commit()
        ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertTrue(ban_query_svc.is_banned("10.0.1.1"))
        self.assertTrue(ban_query_svc.is_banned("10.0.1.255"))
        self.assertTrue(ban_query_svc.is_banned("10.0.1.1", scopes=["foo:bar"]))
        self.assertTrue(ban_query_svc.is_banned("10.0.1.255", scopes=["foo:bar"]))
        self.assertFalse(ban_query_svc.is_banned("10.0.2.1"))

    def test_is_banned_scoped(self):
        from ..models import Ban

        self._make(Ban(ip_address="10.0.4.0/24", scope="foo:bar"))
        self.dbsession.commit()
        ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertTrue(ban_query_svc.is_banned("10.0.4.1", scopes=["foo:bar"]))
        self.assertTrue(ban_query_svc.is_banned("10.0.4.255", scopes=["foo:bar"]))
        self.assertFalse(ban_query_svc.is_banned("10.0.4.1"))
        self.assertFalse(ban_query_svc.is_banned("10.0.4.255"))
        self.assertFalse(ban_query_svc.is_banned("10.0.5.1"))

    def test_is_banned_inactive(self):
        from ..models import Ban

        self._make(Ban(ip_address="10.0.6.0/24", active=False))
        self.dbsession.commit()
        ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertFalse(ban_query_svc.is_banned("10.0.6.1"))
        self.assertFalse(ban_query_svc.is_banned("10.0.6.255"))
        self.assertFalse(ban_query_svc.is_banned("10.0.7.1"))

    def test_is_banned_expired(self):
        from datetime import datetime, timedelta
        from ..models import Ban

        self._make(
            Ban(
                ip_address="10.0.7.0/24",
                active_until=datetime.now() - timedelta(days=1),
            )
        )
        self.dbsession.commit()
        ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertFalse(ban_query_svc.is_banned("10.0.7.1"))
        self.assertFalse(ban_query_svc.is_banned("10.0.7.255"))
        self.assertFalse(ban_query_svc.is_banned("10.0.8.1"))

    def test_ban_from_id(self):
        from ..models import Ban

        ban = self._make(Ban(ip_address="10.0.1.0/24"))
        self.dbsession.commit()
        ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(ban_query_svc.ban_from_id(ban.id), ban)

    def test_ban_from_id_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound

        ban_query_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            ban_query_svc.ban_from_id(-1)

    def test_ban_from_id_string(self):
        from ..models import Ban

        ban = self._make(Ban(ip_address="10.0.1.0/24"))
        self.dbsession.commit()
        ban_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(ban_query_svc.ban_from_id(str(ban.id)), ban)


class TestBanUpdateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import BanUpdateService

        return BanUpdateService

    def test_update(self):
        import pytz
        from datetime import datetime, timedelta
        from ..models import Ban

        ban = self._make(Ban(ip_address="10.0.1.0/24"))
        self.dbsession.commit()
        ban_update_svc = self._get_target_class()(self.dbsession)
        ban = ban_update_svc.update(
            ban.id,
            ip_address="10.0.2.0/24",
            description="Violation of galactic law",
            duration=30,
            scope="galaxy_far_away",
            active=False,
        )
        self.assertEqual(ban.ip_address, "10.0.2.0/24")
        self.assertEqual(ban.description, "Violation of galactic law")
        self.assertGreaterEqual(
            ban.active_until, datetime.now(pytz.utc) + timedelta(days=29, hours=23)
        )
        self.assertEqual(ban.scope, "galaxy_far_away")
        self.assertFalse(ban.active)

    def test_update_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound

        ban_update_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            ban_update_svc.update(-1, active=False)

    def test_update_duration(self):
        import pytz
        from datetime import datetime, timedelta
        from ..models import Ban

        past_now = datetime.now() - timedelta(days=30)
        ban = self._make(
            Ban(
                ip_address="10.0.1.0/24",
                created_at=past_now,
                active_until=past_now + timedelta(days=7),
            )
        )
        self.dbsession.commit()
        active_until = ban.active_until
        ban_update_svc = self._get_target_class()(self.dbsession)
        ban = ban_update_svc.update(ban.id, duration=14)
        self.assertEqual(ban.duration, 14)
        self.assertGreater(ban.active_until, active_until)
        self.assertLess(ban.active_until, datetime.now(pytz.utc))

    def test_update_duration_no_change(self):
        from datetime import datetime, timedelta
        from ..models import Ban

        past_now = datetime.now() - timedelta(days=30)
        ban = self._make(
            Ban(
                ip_address="10.0.1.0/24",
                created_at=past_now,
                active_until=past_now + timedelta(days=7),
            )
        )
        self.dbsession.commit()
        active_until = ban.active_until
        ban_update_svc = self._get_target_class()(self.dbsession)
        ban = ban_update_svc.update(ban.id, duration=7)
        self.assertEqual(ban.active_until, active_until)

    def test_update_none(self):
        from ..models import Ban

        ban = self._make(
            Ban(ip_address="10.0.1.0/24", description="In a galaxy far away")
        )
        self.dbsession.commit()
        ban_update_svc = self._get_target_class()(self.dbsession)
        ban = ban_update_svc.update(ban.id, description=None)
        self.assertIsNone(ban.description)

    def test_update_empty(self):
        from datetime import datetime, timedelta
        from ..models import Ban

        ban = self._make(
            Ban(
                ip_address="10.0.1.0/24",
                description="Violation of galactic law",
                active_until=datetime.now() + timedelta(days=7),
                scope="galaxy_far_away",
            )
        )
        self.dbsession.commit()
        ban_update_svc = self._get_target_class()(self.dbsession)
        ban = ban_update_svc.update(
            ban.id, description="", duration="", scope="", active=""
        )
        self.assertIsNone(ban.description)
        self.assertIsNone(ban.active_until)
        self.assertIsNone(ban.scope)
        self.assertFalse(ban.active)
