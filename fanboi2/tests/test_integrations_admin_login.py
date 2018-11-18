import unittest
import unittest.mock

from pyramid import testing
from webob.multidict import MultiDict

from . import IntegrationMixin


class TestIntegrationAdminLogin(IntegrationMixin, unittest.TestCase):
    def test_login_get(self):
        from ..forms import AdminLoginForm
        from ..interfaces import ISettingQueryService
        from ..views.admin import login_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {"setup.version": "0.30.0"}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "GET"
        response = login_get(request)
        self.assertIsInstance(response["form"], AdminLoginForm)

    def test_login_get_logged_in(self):
        from ..views.admin import login_get

        self.request.method = "GET"
        self.config.testing_securitypolicy(userid="foo")
        self.config.add_route("admin_dashboard", "/admin/dashboard")
        response = login_get(self.request)
        self.assertEqual(response.location, "/admin/dashboard")

    def test_login_get_not_installed(self):
        from ..interfaces import ISettingQueryService
        from ..views.admin import login_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "GET"
        self.config.add_route("admin_setup", "/setup")
        response = login_get(request)
        self.assertEqual(response.location, "/setup")

    def test_login_post(self):
        from passlib.hash import argon2
        from ..interfaces import IUserLoginService
        from ..models import User, UserSession
        from ..services import UserLoginService
        from ..views.admin import login_post
        from . import mock_service

        self._make(
            User(
                username="foo",
                encrypted_password=argon2.hash("passw0rd"),
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IUserLoginService: UserLoginService(self.dbsession)}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST["username"] = "foo"
        request.POST["password"] = "passw0rd"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(
            userid=None, remember_result=[("Set-Cookie", "foobar")]
        )
        self.config.add_route("admin_dashboard", "/admin/dashboard")
        response = login_post(request)
        self.assertEqual(response.location, "/admin/dashboard")
        self.assertEqual(self.dbsession.query(UserSession).count(), 1)
        self.assertIn("Set-Cookie", response.headers)

    def test_login_post_logged_in(self):
        from pyramid.httpexceptions import HTTPForbidden
        from ..views.admin import login_post

        self.request.method = "POST"
        self.config.testing_securitypolicy(userid="foo")
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST["username"] = "foo"
        self.request.POST["password"] = "password"
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        with self.assertRaises(HTTPForbidden):
            login_post(self.request)

    def test_login_post_wrong_password(self):
        from passlib.hash import argon2
        from ..forms import AdminLoginForm
        from ..interfaces import IUserLoginService
        from ..models import User, UserSession
        from ..services import UserLoginService
        from ..views.admin import login_post
        from . import mock_service

        self._make(
            User(
                username="foo",
                encrypted_password=argon2.hash("passw0rd"),
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IUserLoginService: UserLoginService(self.dbsession)}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST["username"] = "foo"
        request.POST["password"] = "password"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = login_post(request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertIsInstance(response["form"], AdminLoginForm)

    def test_login_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..models import UserSession
        from ..views.admin import login_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.session = testing.DummySession()
        self.request.POST = MultiDict({})
        self.request.POST["username"] = "foo"
        self.request.POST["password"] = "passw0rd"
        with self.assertRaises(BadCSRFToken):
            login_post(self.request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)

    def test_login_post_deactivated(self):
        from passlib.hash import argon2
        from ..forms import AdminLoginForm
        from ..interfaces import IUserLoginService
        from ..models import User, UserSession
        from ..services import UserLoginService
        from ..views.admin import login_post
        from . import mock_service

        self._make(
            User(
                username="foo",
                encrypted_password=argon2.hash("passw0rd"),
                ident="fooident",
                ident_type="ident",
                name="Foo",
                deactivated=True,
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IUserLoginService: UserLoginService(self.dbsession)}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST["username"] = "foo"
        request.POST["password"] = "passw0rd"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = login_post(request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertIsInstance(response["form"], AdminLoginForm)

    def test_login_post_not_found(self):
        from ..forms import AdminLoginForm
        from ..interfaces import IUserLoginService
        from ..models import UserSession
        from ..services import UserLoginService
        from ..views.admin import login_post
        from . import mock_service

        request = mock_service(
            self.request, {IUserLoginService: UserLoginService(self.dbsession)}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.session = testing.DummySession()
        request.POST = MultiDict({})
        request.POST["username"] = "foo"
        request.POST["password"] = "passw0rd"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = login_post(request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertIsInstance(response["form"], AdminLoginForm)

    def test_login_post_invalid_username(self):
        from ..models import UserSession
        from ..views.admin import login_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.session = testing.DummySession()
        self.request.POST = MultiDict({})
        self.request.POST["username"] = ""
        self.request.POST["password"] = "passw0rd"
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = login_post(self.request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertEqual(response["form"].username.data, "")
        self.assertEqual(response["form"].password.data, "passw0rd")
        self.assertDictEqual(
            response["form"].errors, {"username": ["This field is required."]}
        )

    def test_login_post_invalid_password(self):
        from ..models import UserSession
        from ..views.admin import login_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.session = testing.DummySession()
        self.request.POST = MultiDict({})
        self.request.POST["username"] = "foo"
        self.request.POST["password"] = ""
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = login_post(self.request)
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertEqual(response["form"].username.data, "foo")
        self.assertEqual(response["form"].password.data, "")
        self.assertDictEqual(
            response["form"].errors, {"password": ["This field is required."]}
        )
