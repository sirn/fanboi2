import unittest
import unittest.mock

from webob.multidict import MultiDict

from . import IntegrationMixin


class TestIntegrationAdminBanwords(IntegrationMixin, unittest.TestCase):
    def test_banwords_get(self):
        from ..interfaces import IBanwordQueryService
        from ..models import Banword
        from ..services import BanwordQueryService, ScopeService
        from ..views.admin import banwords_get
        from . import mock_service

        banword1 = self._make(Banword(expr="https?:\\/\\/bit\\.ly"))
        banword2 = self._make(Banword(expr="https?:\\/\\/goo\\.gl"))
        self._make(Banword(expr="https?:\\/\\/youtu\\.be", active=False))
        self._make(Banword(expr="https?:\\/\\/example\\.com", active=False))
        request = mock_service(
            self.request,
            {IBanwordQueryService: BanwordQueryService(self.dbsession, ScopeService())},
        )
        request.method = "GET"
        response = banwords_get(request)
        self.assertEqual(response["banwords"], [banword2, banword1])

    def test_banwords_inactive_get(self):
        from ..interfaces import IBanwordQueryService
        from ..models import Banword
        from ..services import BanwordQueryService, ScopeService
        from ..views.admin import banwords_inactive_get
        from . import mock_service

        self._make(Banword(expr="https?:\\/\\/bit\\.ly"))
        self._make(Banword(expr="https?:\\/\\/goo\\.gl"))
        banword3 = self._make(Banword(expr="https?:\\/\\/youtu\\.be", active=False))
        banword4 = self._make(Banword(expr="https?:\\/\\/example\\.com", active=False))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IBanwordQueryService: BanwordQueryService(self.dbsession, ScopeService())},
        )
        request.method = "GET"
        response = banwords_inactive_get(request)
        self.assertEqual(response["banwords"], [banword4, banword3])

    def test_banword_new_get(self):
        from ..forms import AdminBanwordForm
        from ..views.admin import banword_new_get

        self.request.method = "GET"
        response = banword_new_get(self.request)
        self.assertIsInstance(response["form"], AdminBanwordForm)

    def test_banword_new_post(self):
        from ..interfaces import IBanwordCreateService
        from ..models import Banword
        from ..services import BanwordCreateService
        from ..views.admin import banword_new_post
        from . import mock_service

        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IBanwordCreateService: BanwordCreateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["expr"] = "https?:\\/\\/bit\\.ly/"
        request.POST["description"] = "Violation of galactic law"
        request.POST["active"] = "1"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_banword", "/admin/banwords/{banword}")
        response = banword_new_post(request)
        banword = self.dbsession.query(Banword).first()
        self.assertEqual(response.location, "/admin/banwords/%s" % banword.id)
        self.assertEqual(self.dbsession.query(Banword).count(), 1)
        self.assertEqual(banword.expr, "https?:\\/\\/bit\\.ly/")
        self.assertEqual(banword.description, "Violation of galactic law")
        self.assertTrue(banword.active)

    def test_banword_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import banword_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["ip_address"] = "10.0.1.0/24"
        self.request.POST["description"] = "Violation of galactic law"
        self.request.POST["duration"] = 30
        self.request.POST["scope"] = "galaxy_far_away"
        self.request.POST["active"] = "1"
        with self.assertRaises(BadCSRFToken):
            banword_new_post(self.request)

    def test_banword_new_post_invalid_expr(self):
        from ..interfaces import IBanwordCreateService
        from ..models import Banword
        from ..services import BanwordCreateService
        from ..views.admin import banword_new_post
        from . import mock_service

        request = mock_service(
            self.request, {IBanwordCreateService: BanwordCreateService(self.dbsession)}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["expr"] = "(?y)"
        request.POST["description"] = "Violation of galactic law"
        request.POST["active"] = "1"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = banword_new_post(request)
        self.assertEqual(self.dbsession.query(Banword).count(), 0)
        self.assertEqual(response["form"].expr.data, "(?y)")
        self.assertDictEqual(
            response["form"].errors, {"expr": ["Must be a valid regular expression."]}
        )

    def test_banword_get(self):
        from ..models import Banword
        from ..interfaces import IBanwordQueryService
        from ..services import BanwordQueryService, ScopeService
        from ..views.admin import banword_get
        from . import mock_service

        banword = self._make(Banword(expr="https?:\\/\\/bit\\.ly"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IBanwordQueryService: BanwordQueryService(self.dbsession, ScopeService())},
        )
        request.method = "GET"
        request.matchdict["banword"] = str(banword.id)
        response = banword_get(request)
        self.assertEqual(response["banword"], banword)

    def test_banword_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBanwordQueryService
        from ..services import BanwordQueryService, ScopeService
        from ..views.admin import banword_get
        from . import mock_service

        request = mock_service(
            self.request,
            {IBanwordQueryService: BanwordQueryService(self.dbsession, ScopeService())},
        )
        request.method = "GET"
        request.matchdict["banword"] = "-1"
        with self.assertRaises(NoResultFound):
            banword_get(request)

    def test_banword_edit_get(self):
        from ..models import Banword
        from ..interfaces import IBanwordQueryService
        from ..services import BanwordQueryService, ScopeService
        from ..views.admin import banword_edit_get
        from . import mock_service

        banword = self._make(
            Banword(
                expr="https?:\\/\\/bit\\.ly", description="no shortlinks", active=True
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IBanwordQueryService: BanwordQueryService(self.dbsession, ScopeService())},
        )
        request.method = "GET"
        request.matchdict["banword"] = str(banword.id)
        response = banword_edit_get(request)
        self.assertEqual(response["banword"], banword)
        self.assertEqual(response["form"].expr.data, "https?:\\/\\/bit\\.ly")
        self.assertEqual(response["form"].description.data, "no shortlinks")
        self.assertTrue(response["form"].active.data)

    def test_banword_edit_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBanwordQueryService
        from ..services import BanwordQueryService, ScopeService
        from ..views.admin import banword_edit_get
        from . import mock_service

        request = mock_service(
            self.request,
            {IBanwordQueryService: BanwordQueryService(self.dbsession, ScopeService())},
        )
        request.method = "GET"
        request.matchdict["banword"] = "-1"
        with self.assertRaises(NoResultFound):
            banword_edit_get(request)

    def test_banword_edit_post(self):
        from ..models import Banword
        from ..interfaces import IBanwordQueryService, IBanwordUpdateService
        from ..services import BanwordQueryService, BanwordUpdateService, ScopeService
        from ..views.admin import banword_edit_post
        from . import mock_service

        banword = self._make(
            Banword(
                expr="https?:\\/\\/bit\\.ly", description="no shortlinks", active=True
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBanwordQueryService: BanwordQueryService(
                    self.dbsession, ScopeService()
                ),
                IBanwordUpdateService: BanwordUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["banword"] = str(banword.id)
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["expr"] = "https?:\\/\\/(bit\\.ly|goo\\.gl)"
        request.POST["description"] = "violation of galactic law"
        request.POST["active"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_banword", "/admin/banwords/{banword}")
        response = banword_edit_post(request)
        self.assertEqual(response.location, "/admin/banwords/%s" % banword.id)
        self.assertEqual(banword.expr, "https?:\\/\\/(bit\\.ly|goo\\.gl)")
        self.assertEqual(banword.description, "violation of galactic law")
        self.assertFalse(banword.active)

    def test_banword_edit_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBanwordQueryService
        from ..services import BanwordQueryService, ScopeService
        from ..views.admin import banword_edit_post
        from . import mock_service

        request = mock_service(
            self.request,
            {IBanwordQueryService: BanwordQueryService(self.dbsession, ScopeService())},
        )
        request.method = "POST"
        request.matchdict["banword"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            banword_edit_post(request)

    def test_banword_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..models import Banword
        from ..views.admin import banword_edit_post

        banword = self._make(Banword(expr="https?:\\/\\/bit\\.ly"))
        self.request.method = "POST"
        self.request.matchdict["banword"] = str(banword.id)
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["expr"] = "https?:\\/\\/(bit\\.ly|goo\\.gl)"
        self.request.POST["description"] = "violation of galactic law"
        self.request.POST["active"] = ""
        with self.assertRaises(BadCSRFToken):
            banword_edit_post(self.request)

    def test_banword_edit_post_invalid_banword(self):
        from ..models import Banword
        from ..interfaces import IBanwordQueryService, IBanwordUpdateService
        from ..services import BanwordQueryService, BanwordUpdateService, ScopeService
        from ..views.admin import banword_edit_post
        from . import mock_service

        banword = self._make(
            Banword(
                expr="https?:\\/\\/bit\\.ly", description="no shortlinks", active=True
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBanwordQueryService: BanwordQueryService(
                    self.dbsession, ScopeService()
                ),
                IBanwordUpdateService: BanwordUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["banword"] = str(banword.id)
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["expr"] = "(?y)"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = banword_edit_post(request)
        self.assertEqual(banword.expr, "https?:\\/\\/bit\\.ly")
        self.assertEqual(response["banword"], banword)
        self.assertEqual(response["form"].expr.data, "(?y)")
        self.assertDictEqual(
            response["form"].errors, {"expr": ["Must be a valid regular expression."]}
        )
