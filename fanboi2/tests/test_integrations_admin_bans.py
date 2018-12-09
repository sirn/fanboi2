import unittest
import unittest.mock

from webob.multidict import MultiDict

from . import IntegrationMixin


class TestIntegrationAdminBans(IntegrationMixin, unittest.TestCase):
    def test_bans_get(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..interfaces import IBanQueryService
        from ..models import Ban
        from ..services import BanQueryService
        from ..views.admin import bans_get
        from . import mock_service

        ban1 = self._make(
            Ban(ip_address="10.0.1.0/24", active_until=func.now() + timedelta(hours=1))
        )
        self._make(
            Ban(ip_address="10.0.2.0/24", active_until=func.now() - timedelta(hours=1))
        )
        ban3 = self._make(Ban(ip_address="10.0.3.0/24"))
        self._make(Ban(ip_address="10.0.3.0/24", active=False))
        ban5 = self._make(
            Ban(ip_address="10.0.3.0/24", active_until=func.now() + timedelta(hours=2))
        )
        ban6 = self._make(
            Ban(ip_address="10.0.3.0/24", created_at=func.now() + timedelta(minutes=5))
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBanQueryService: BanQueryService(self.dbsession)}
        )
        request.method = "GET"
        response = bans_get(request)
        self.assertEqual(response["bans"], [ban6, ban3, ban5, ban1])

    def test_bans_inactive_get(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..interfaces import IBanQueryService
        from ..models import Ban
        from ..services import BanQueryService
        from ..views.admin import bans_inactive_get
        from . import mock_service

        self._make(
            Ban(ip_address="10.0.1.0/24", active_until=func.now() + timedelta(hours=1))
        )
        ban2 = self._make(
            Ban(ip_address="10.0.2.0/24", active_until=func.now() - timedelta(hours=1))
        )
        self._make(Ban(ip_address="10.0.3.0/24"))
        ban4 = self._make(Ban(ip_address="10.0.3.0/24", active=False))
        ban5 = self._make(
            Ban(ip_address="10.0.3.0/24", active_until=func.now() - timedelta(hours=2))
        )
        ban6 = self._make(
            Ban(
                ip_address="10.0.3.0/24",
                created_at=func.now() + timedelta(minutes=5),
                active=False,
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBanQueryService: BanQueryService(self.dbsession)}
        )
        request.method = "GET"
        response = bans_inactive_get(request)
        self.assertEqual(response["bans"], [ban6, ban4, ban2, ban5])

    def test_ban_new_get(self):
        from ..forms import AdminBanForm
        from ..views.admin import ban_new_get

        self.request.method = "GET"
        response = ban_new_get(self.request)
        self.assertIsInstance(response["form"], AdminBanForm)

    def test_ban_new_post(self):
        import pytz
        from datetime import datetime, timedelta
        from ..interfaces import IBanCreateService
        from ..models import Ban
        from ..services import BanCreateService
        from ..views.admin import ban_new_post
        from . import mock_service

        request = mock_service(
            self.request,
            {"db": self.dbsession, IBanCreateService: BanCreateService(self.dbsession)},
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["ip_address"] = "10.0.1.0/24"
        request.POST["description"] = "Violation of galactic law"
        request.POST["duration"] = "30"
        request.POST["scope"] = "galaxy_far_away"
        request.POST["active"] = "1"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_ban", "/admin/bans/{ban}")
        response = ban_new_post(request)
        ban = self.dbsession.query(Ban).first()
        self.assertEqual(response.location, "/admin/bans/%s" % ban.id)
        self.assertEqual(self.dbsession.query(Ban).count(), 1)
        self.assertEqual(ban.ip_address, "10.0.1.0/24")
        self.assertEqual(ban.description, "Violation of galactic law")
        self.assertGreaterEqual(
            ban.active_until, datetime.now(pytz.utc) + timedelta(days=29, hours=23)
        )
        self.assertEqual(ban.scope, "galaxy_far_away")
        self.assertTrue(ban.active)

    def test_ban_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import ban_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["ip_address"] = "10.0.1.0/24"
        self.request.POST["description"] = "Violation of galactic law"
        self.request.POST["duration"] = 30
        self.request.POST["scope"] = "galaxy_far_away"
        self.request.POST["active"] = "1"
        with self.assertRaises(BadCSRFToken):
            ban_new_post(self.request)

    def test_ban_new_post_invalid_ip_address(self):
        from ..interfaces import IBanCreateService
        from ..models import Ban
        from ..services import BanCreateService
        from ..views.admin import ban_new_post
        from . import mock_service

        request = mock_service(
            self.request, {IBanCreateService: BanCreateService(self.dbsession)}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["ip_address"] = "foobar"
        request.POST["description"] = "Violation of galactic law"
        request.POST["duration"] = "30"
        request.POST["scope"] = "galaxy_far_away"
        request.POST["active"] = "1"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = ban_new_post(request)
        self.assertEqual(self.dbsession.query(Ban).count(), 0)
        self.assertEqual(response["form"].ip_address.data, "foobar")
        self.assertDictEqual(
            response["form"].errors, {"ip_address": ["Must be a valid IP address."]}
        )

    def test_ban_get(self):
        from ..models import Ban
        from ..interfaces import IBanQueryService
        from ..services import BanQueryService
        from ..views.admin import ban_get
        from . import mock_service

        ban = self._make(Ban(ip_address="10.0.0.0/24"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBanQueryService: BanQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["ban"] = str(ban.id)
        response = ban_get(request)
        self.assertEqual(response["ban"], ban)

    def test_ban_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBanQueryService
        from ..services import BanQueryService
        from ..views.admin import ban_get
        from . import mock_service

        request = mock_service(
            self.request, {IBanQueryService: BanQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["ban"] = "-1"
        with self.assertRaises(NoResultFound):
            ban_get(request)

    def test_ban_edit_get(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import Ban
        from ..interfaces import IBanQueryService
        from ..services import BanQueryService
        from ..views.admin import ban_edit_get
        from . import mock_service

        now = func.now()
        ban = self._make(
            Ban(
                ip_address="10.0.0.0/24",
                description="Violation of galactic law",
                active_until=now + timedelta(days=30),
                scope="galaxy_far_away",
                active=True,
                created_at=now,
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBanQueryService: BanQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["ban"] = str(ban.id)
        response = ban_edit_get(request)
        self.assertEqual(response["ban"], ban)
        self.assertEqual(response["form"].ip_address.data, "10.0.0.0/24")
        self.assertEqual(response["form"].description.data, "Violation of galactic law")
        self.assertEqual(response["form"].duration.data, 30)
        self.assertEqual(response["form"].scope.data, "galaxy_far_away")
        self.assertTrue(response["form"].active.data)

    def test_ban_edit_get_no_duration(self):
        from ..models import Ban
        from ..interfaces import IBanQueryService
        from ..services import BanQueryService
        from ..views.admin import ban_edit_get
        from . import mock_service

        ban = self._make(Ban(ip_address="10.0.0.0/24"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBanQueryService: BanQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["ban"] = str(ban.id)
        response = ban_edit_get(request)
        self.assertEqual(response["form"].duration.data, 0)

    def test_ban_edit_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBanQueryService
        from ..services import BanQueryService
        from ..views.admin import ban_edit_get
        from . import mock_service

        request = mock_service(
            self.request, {IBanQueryService: BanQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["ban"] = "-1"
        with self.assertRaises(NoResultFound):
            ban_edit_get(request)

    def test_ban_edit_post(self):
        import pytz
        from datetime import datetime, timedelta
        from ..models import Ban
        from ..interfaces import IBanQueryService, IBanUpdateService
        from ..services import BanQueryService, BanUpdateService
        from ..views.admin import ban_edit_post
        from . import mock_service

        ban = self._make(Ban(ip_address="10.0.0.0/24"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBanQueryService: BanQueryService(self.dbsession),
                IBanUpdateService: BanUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["ban"] = str(ban.id)
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["ip_address"] = "10.0.1.0/24"
        request.POST["description"] = "Violation of galactic law"
        request.POST["duration"] = 30
        request.POST["scope"] = "galaxy_far_away"
        request.POST["active"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_ban", "/admin/bans/{ban}")
        response = ban_edit_post(request)
        self.assertEqual(response.location, "/admin/bans/%s" % ban.id)
        self.assertEqual(ban.ip_address, "10.0.1.0/24")
        self.assertEqual(ban.description, "Violation of galactic law")
        self.assertGreaterEqual(
            ban.active_until, datetime.now(pytz.utc) + timedelta(days=29, hours=23)
        )
        self.assertEqual(ban.scope, "galaxy_far_away")
        self.assertFalse(ban.active)

    def test_ban_edit_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBanQueryService
        from ..services import BanQueryService
        from ..views.admin import ban_edit_post
        from . import mock_service

        request = mock_service(
            self.request, {IBanQueryService: BanQueryService(self.dbsession)}
        )
        request.method = "POST"
        request.matchdict["ban"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            ban_edit_post(request)

    def test_ban_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..models import Ban
        from ..views.admin import ban_edit_post

        ban = self._make(Ban(ip_address="10.0.0.0/24"))
        self.request.method = "POST"
        self.request.matchdict["ban"] = str(ban.id)
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["ip_address"] = "10.0.1.0/24"
        self.request.POST["description"] = "Violation of galactic law"
        self.request.POST["duration"] = 30
        self.request.POST["scope"] = "galaxy_far_away"
        self.request.POST["active"] = ""
        with self.assertRaises(BadCSRFToken):
            ban_edit_post(self.request)

    def test_ban_edit_post_duration(self):
        import pytz
        from datetime import datetime, timedelta
        from sqlalchemy.sql import func
        from ..models import Ban
        from ..interfaces import IBanQueryService, IBanUpdateService
        from ..services import BanQueryService, BanUpdateService
        from ..views.admin import ban_edit_post
        from . import mock_service

        past_now = func.now() - timedelta(days=30)
        ban = self._make(
            Ban(
                ip_address="10.0.0.0/24",
                created_at=past_now,
                active_until=past_now + timedelta(days=7),
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBanQueryService: BanQueryService(self.dbsession),
                IBanUpdateService: BanUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["ban"] = str(ban.id)
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["ip_address"] = "10.0.0.0/24"
        request.POST["description"] = ""
        request.POST["duration"] = "14"
        request.POST["scope"] = ""
        request.POST["active"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_ban", "/admin/bans/{ban}")
        active_until = ban.active_until
        response = ban_edit_post(request)
        self.assertEqual(response.location, "/admin/bans/%s" % ban.id)
        self.assertEqual(ban.duration, 14)
        self.assertGreater(ban.active_until, active_until)
        self.assertLess(ban.active_until, datetime.now(pytz.utc))

    def test_ban_edit_post_duration_no_change(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import Ban
        from ..interfaces import IBanQueryService, IBanUpdateService
        from ..services import BanQueryService, BanUpdateService
        from ..views.admin import ban_edit_post
        from . import mock_service

        past_now = func.now() - timedelta(days=30)
        ban = self._make(
            Ban(
                ip_address="10.0.0.0/24",
                created_at=past_now,
                active_until=past_now + timedelta(days=7),
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBanQueryService: BanQueryService(self.dbsession),
                IBanUpdateService: BanUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["ban"] = str(ban.id)
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["ip_address"] = "10.0.0.0/24"
        request.POST["description"] = ""
        request.POST["duration"] = "7"
        request.POST["scope"] = ""
        request.POST["active"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_ban", "/admin/bans/{ban}")
        active_until = ban.active_until
        response = ban_edit_post(request)
        self.assertEqual(response.location, "/admin/bans/%s" % ban.id)
        self.assertEqual(ban.active_until, active_until)

    def test_ban_edit_post_invalid_ip_address(self):
        from ..models import Ban
        from ..interfaces import IBanQueryService, IBanUpdateService
        from ..services import BanQueryService, BanUpdateService
        from ..views.admin import ban_edit_post
        from . import mock_service

        ban = self._make(Ban(ip_address="10.0.0.0/24"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBanQueryService: BanQueryService(self.dbsession),
                IBanUpdateService: BanUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["ban"] = str(ban.id)
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["ip_address"] = "foobar"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = ban_edit_post(request)
        self.assertEqual(ban.ip_address, "10.0.0.0/24")
        self.assertEqual(response["ban"], ban)
        self.assertEqual(response["form"].ip_address.data, "foobar")
        self.assertDictEqual(
            response["form"].errors, {"ip_address": ["Must be a valid IP address."]}
        )
