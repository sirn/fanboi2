import unittest
import unittest.mock

from pyramid import testing
from webob.multidict import MultiDict

from . import ModelSessionMixin


class TestIntegrationAdmin(ModelSessionMixin, unittest.TestCase):
    def setUp(self):
        super(TestIntegrationAdmin, self).setUp()
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry
        self.request.user_agent = "Mock/1.0"
        self.request.client_addr = "127.0.0.1"
        self.request.referrer = "https://www.example.com/referer"
        self.request.url = "https://www.example.com/url"
        self.request.application_url = "https://www.example.com"

    def tearDown(self):
        super(TestIntegrationAdmin, self).tearDown()
        testing.tearDown()

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

    def test_logout_get(self):
        from ..interfaces import IUserLoginService
        from ..models import User, UserSession
        from ..services import UserLoginService
        from ..views.admin import logout_get
        from . import mock_service

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="fooident",
                ident_type="ident",
                name="Foo",
            )
        )
        user_session = self._make(
            UserSession(user=user, token="foo_token1", ip_address="127.0.0.1")
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IUserLoginService: UserLoginService(self.dbsession)}
        )
        request.method = "GET"
        request.client_addr = "127.0.0.1"
        self.config.testing_securitypolicy(
            userid="foo_token1", forget_result=[("Set-Cookie", "foobar")]
        )
        self.config.add_route("admin_root", "/admin")
        self.assertIsNone(user_session.revoked_at)
        response = logout_get(request)
        self.assertEqual(response.location, "/admin")
        self.assertIn("Set-Cookie", response.headers)
        self.assertIsNotNone(user_session.revoked_at)

    def test_logout_get_not_logged_in(self):
        from ..views.admin import logout_get

        self.request.method = "GET"
        self.request.client_addr = "127.0.0.1"
        self.config.testing_securitypolicy(userid=None)
        self.config.add_route("admin_root", "/admin")
        response = logout_get(self.request)
        self.assertEqual(response.location, "/admin")

    def test_setup_get(self):
        from ..forms import AdminSetupForm
        from ..interfaces import ISettingQueryService
        from ..views.admin import setup_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "GET"
        response = setup_get(request)
        self.assertIsInstance(response["form"], AdminSetupForm)

    def test_setup_get_already_setup(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import ISettingQueryService
        from ..views.admin import setup_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {"setup.version": "0.30.0"}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "GET"
        with self.assertRaises(HTTPNotFound):
            setup_get(request)

    def test_setup_post(self):
        from ..interfaces import (
            ISettingQueryService,
            ISettingUpdateService,
            IUserCreateService,
        )
        from ..models import User, UserSession, Group
        from ..services import (
            SettingQueryService,
            SettingUpdateService,
            UserCreateService,
        )
        from ..version import __VERSION__
        from ..views.admin import setup_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region()
        setting_query_svc = SettingQueryService(self.dbsession, cache_region)

        class _DummyIdentityService(object):
            def identity_for(self, **kwargs):
                return "id=" + ",".join("%s" % (v,) for k, v in sorted(kwargs.items()))

        request = mock_service(
            self.request,
            {
                IUserCreateService: UserCreateService(
                    self.dbsession, _DummyIdentityService()
                ),
                ISettingQueryService: setting_query_svc,
                ISettingUpdateService: SettingUpdateService(
                    self.dbsession, cache_region
                ),
            },
        )
        self.assertIsNone(setting_query_svc.value_from_key("setup.version"))
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["username"] = "root"
        request.POST["password"] = "passw0rd"
        request.POST["password_confirm"] = "passw0rd"
        request.POST["name"] = "Root"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_root", "/admin")
        response = setup_post(request)
        user = self.dbsession.query(User).one()
        group = self.dbsession.query(Group).one()
        self.assertEqual(response.location, "/admin")
        self.assertIsNone(user.parent)
        self.assertEqual(user.username, "root")
        self.assertEqual(user.groups, [group])
        self.assertEqual(user.ident_type, "ident_admin")
        self.assertEqual(user.ident, "id=root")
        self.assertEqual(user.name, "Root")
        self.assertNotEqual(user.encrypted_password, "passw0rd")
        self.assertEqual(self.dbsession.query(UserSession).count(), 0)
        self.assertEqual(setting_query_svc.value_from_key("setup.version"), __VERSION__)

    def test_setup_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["username"] = "root"
        request.POST["password"] = "passw0rd"
        request.POST["password_confirm"] = "passw0rd"
        with self.assertRaises(BadCSRFToken):
            setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)

    def test_setup_post_already_setup(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {"setup.version": "0.30.0"}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        with self.assertRaises(HTTPNotFound):
            setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)

    def test_setup_post_invalid_username(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["username"] = ""
        request.POST["password"] = "passw0rd"
        request.POST["password_confirm"] = "passw0rd"
        request.POST["name"] = "Root"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response["form"].username.data, "")
        self.assertEqual(response["form"].password.data, "passw0rd")
        self.assertEqual(response["form"].password_confirm.data, "passw0rd")
        self.assertEqual(response["form"].name.data, "Root")
        self.assertDictEqual(
            response["form"].errors, {"username": ["This field is required."]}
        )

    def test_setup_post_invalid_username_shorter(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["username"] = "r"
        request.POST["password"] = "passw0rd"
        request.POST["password_confirm"] = "passw0rd"
        request.POST["name"] = "Root"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response["form"].username.data, "r")
        self.assertEqual(response["form"].password.data, "passw0rd")
        self.assertEqual(response["form"].password_confirm.data, "passw0rd")
        self.assertEqual(response["form"].name.data, "Root")
        self.assertDictEqual(
            response["form"].errors,
            {"username": ["Field must be between 2 and 32 characters long."]},
        )

    def test_setup_post_invalid_username_longer(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["username"] = "r" * 65
        request.POST["password"] = "passw0rd"
        request.POST["password_confirm"] = "passw0rd"
        request.POST["name"] = "Root"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response["form"].username.data, "r" * 65)
        self.assertEqual(response["form"].password.data, "passw0rd")
        self.assertEqual(response["form"].password_confirm.data, "passw0rd")
        self.assertEqual(response["form"].name.data, "Root")
        self.assertDictEqual(
            response["form"].errors,
            {"username": ["Field must be between 2 and 32 characters long."]},
        )

    def test_setup_post_invalid_password(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["username"] = "root"
        request.POST["password"] = ""
        request.POST["password_confirm"] = "passw0rd"
        request.POST["name"] = "Root"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response["form"].username.data, "root")
        self.assertEqual(response["form"].password.data, "")
        self.assertEqual(response["form"].password_confirm.data, "passw0rd")
        self.assertEqual(response["form"].name.data, "Root")
        self.assertDictEqual(
            response["form"].errors,
            {
                "password": ["This field is required."],
                "password_confirm": ["Password must match."],
            },
        )

    def test_setup_post_invalid_password_shorter(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["username"] = "root"
        request.POST["password"] = "passw0r"
        request.POST["password_confirm"] = "passw0r"
        request.POST["name"] = "Root"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response["form"].username.data, "root")
        self.assertEqual(response["form"].password.data, "passw0r")
        self.assertEqual(response["form"].password_confirm.data, "passw0r")
        self.assertEqual(response["form"].name.data, "Root")
        self.assertDictEqual(
            response["form"].errors,
            {"password": ["Field must be between 8 and 64 characters long."]},
        )

    def test_setup_post_invalid_password_longer(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["username"] = "root"
        request.POST["password"] = "p" * 65
        request.POST["password_confirm"] = "p" * 65
        request.POST["name"] = "Root"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response["form"].username.data, "root")
        self.assertEqual(response["form"].password.data, "p" * 65)
        self.assertEqual(response["form"].password_confirm.data, "p" * 65)
        self.assertEqual(response["form"].name.data, "Root")
        self.assertDictEqual(
            response["form"].errors,
            {"password": ["Field must be between 8 and 64 characters long."]},
        )

    def test_setup_post_invalid_name(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["username"] = "root"
        request.POST["password"] = "passw0rd"
        request.POST["password_confirm"] = "passw0rd"
        request.POST["name"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response["form"].username.data, "root")
        self.assertEqual(response["form"].password.data, "passw0rd")
        self.assertEqual(response["form"].password_confirm.data, "passw0rd")
        self.assertEqual(response["form"].name.data, "")
        self.assertDictEqual(
            response["form"].errors, {"name": ["This field is required."]}
        )

    def test_setup_post_invalid_name_shorter(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["username"] = "root"
        request.POST["password"] = "passw0rd"
        request.POST["password_confirm"] = "passw0rd"
        request.POST["name"] = "R"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response["form"].username.data, "root")
        self.assertEqual(response["form"].password.data, "passw0rd")
        self.assertEqual(response["form"].password_confirm.data, "passw0rd")
        self.assertEqual(response["form"].name.data, "R")
        self.assertDictEqual(
            response["form"].errors,
            {"name": ["Field must be between 2 and 64 characters long."]},
        )

    def test_setup_post_invalid_name_longer(self):
        from ..interfaces import ISettingQueryService
        from ..models import User
        from ..views.admin import setup_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["username"] = "root"
        request.POST["password"] = "passw0rd"
        request.POST["password_confirm"] = "passw0rd"
        request.POST["name"] = "R" * 65
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = setup_post(request)
        self.assertEqual(self.dbsession.query(User).count(), 0)
        self.assertEqual(response["form"].username.data, "root")
        self.assertEqual(response["form"].password.data, "passw0rd")
        self.assertEqual(response["form"].password_confirm.data, "passw0rd")
        self.assertEqual(response["form"].name.data, "R" * 65)
        self.assertDictEqual(
            response["form"].errors,
            {"name": ["Field must be between 2 and 64 characters long."]},
        )

    def test_dashboard_get(self):
        from datetime import datetime, timedelta
        from ..interfaces import IUserSessionQueryService, IUserLoginService
        from ..models import User, UserSession
        from ..services import UserSessionQueryService, UserLoginService
        from ..views.admin import dashboard_get
        from . import mock_service

        user = self._make(
            User(
                username="foo",
                encrypted_password="none",
                ident="foo",
                ident_type="ident_admin",
                name="Nameless Foo",
            )
        )
        user_session1 = self._make(
            UserSession(
                user=user,
                token="user1_token1",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now() - timedelta(days=2),
            )
        )
        user_session2 = self._make(
            UserSession(
                user=user,
                token="user1_token2",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now() - timedelta(days=3),
            )
        )
        user_session3 = self._make(
            UserSession(
                user=user,
                token="user1_token3",
                ip_address="127.0.0.1",
                last_seen_at=datetime.now() - timedelta(days=1),
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IUserLoginService: UserLoginService(self.dbsession),
                IUserSessionQueryService: UserSessionQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        self.config.testing_securitypolicy(userid="user1_token3")
        response = dashboard_get(request)
        self.assertEqual(response["user"], user)
        self.assertEqual(
            response["sessions"], [user_session3, user_session1, user_session2]
        )

    def test_bans_get(self):
        from datetime import datetime, timedelta
        from ..interfaces import IBanQueryService
        from ..models import Ban
        from ..services import BanQueryService
        from ..views.admin import bans_get
        from . import mock_service

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
        request = mock_service(
            self.request, {IBanQueryService: BanQueryService(self.dbsession)}
        )
        request.method = "GET"
        response = bans_get(request)
        self.assertEqual(response["bans"], [ban6, ban3, ban5, ban1])

    def test_bans_inactive_get(self):
        from datetime import datetime, timedelta
        from ..interfaces import IBanQueryService
        from ..models import Ban
        from ..services import BanQueryService
        from ..views.admin import bans_inactive_get
        from . import mock_service

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
        from datetime import datetime, timedelta
        from ..models import Ban
        from ..interfaces import IBanQueryService
        from ..services import BanQueryService
        from ..views.admin import ban_edit_get
        from . import mock_service

        now = datetime.now()
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
        from ..models import Ban
        from ..interfaces import IBanQueryService, IBanUpdateService
        from ..services import BanQueryService, BanUpdateService
        from ..views.admin import ban_edit_post
        from . import mock_service

        past_now = datetime.now() - timedelta(days=30)
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
        from datetime import datetime, timedelta
        from ..models import Ban
        from ..interfaces import IBanQueryService, IBanUpdateService
        from ..services import BanQueryService, BanUpdateService
        from ..views.admin import ban_edit_post
        from . import mock_service

        past_now = datetime.now() - timedelta(days=30)
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

    def test_banwords_get(self):
        from ..interfaces import IBanwordQueryService
        from ..models import Banword
        from ..services import BanwordQueryService
        from ..views.admin import banwords_get
        from . import mock_service

        banword1 = self._make(Banword(expr="https?:\\/\\/bit\\.ly"))
        banword2 = self._make(Banword(expr="https?:\\/\\/goo\\.gl"))
        self._make(Banword(expr="https?:\\/\\/youtu\\.be", active=False))
        self._make(Banword(expr="https?:\\/\\/example\\.com", active=False))
        request = mock_service(
            self.request, {IBanwordQueryService: BanwordQueryService(self.dbsession)}
        )
        request.method = "GET"
        response = banwords_get(request)
        self.assertEqual(response["banwords"], [banword2, banword1])

    def test_banwords_inactive_get(self):
        from ..interfaces import IBanwordQueryService
        from ..models import Banword
        from ..services import BanwordQueryService
        from ..views.admin import banwords_inactive_get
        from . import mock_service

        self._make(Banword(expr="https?:\\/\\/bit\\.ly"))
        self._make(Banword(expr="https?:\\/\\/goo\\.gl"))
        banword3 = self._make(Banword(expr="https?:\\/\\/youtu\\.be", active=False))
        banword4 = self._make(Banword(expr="https?:\\/\\/example\\.com", active=False))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBanwordQueryService: BanwordQueryService(self.dbsession)}
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
        from ..services import BanwordQueryService
        from ..views.admin import banword_get
        from . import mock_service

        banword = self._make(Banword(expr="https?:\\/\\/bit\\.ly"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBanwordQueryService: BanwordQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["banword"] = str(banword.id)
        response = banword_get(request)
        self.assertEqual(response["banword"], banword)

    def test_banword_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBanwordQueryService
        from ..services import BanwordQueryService
        from ..views.admin import banword_get
        from . import mock_service

        request = mock_service(
            self.request, {IBanwordQueryService: BanwordQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["banword"] = "-1"
        with self.assertRaises(NoResultFound):
            banword_get(request)

    def test_banword_edit_get(self):
        from ..models import Banword
        from ..interfaces import IBanwordQueryService
        from ..services import BanwordQueryService
        from ..views.admin import banword_edit_get
        from . import mock_service

        banword = self._make(
            Banword(
                expr="https?:\\/\\/bit\\.ly", description="no shortlinks", active=True
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBanwordQueryService: BanwordQueryService(self.dbsession)}
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
        from ..services import BanwordQueryService
        from ..views.admin import banword_edit_get
        from . import mock_service

        request = mock_service(
            self.request, {IBanwordQueryService: BanwordQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["banword"] = "-1"
        with self.assertRaises(NoResultFound):
            banword_edit_get(request)

    def test_banword_edit_post(self):
        from ..models import Banword
        from ..interfaces import IBanwordQueryService, IBanwordUpdateService
        from ..services import BanwordQueryService, BanwordUpdateService
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
                IBanwordQueryService: BanwordQueryService(self.dbsession),
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
        from ..services import BanwordQueryService
        from ..views.admin import banword_edit_post
        from . import mock_service

        request = mock_service(
            self.request, {IBanwordQueryService: BanwordQueryService(self.dbsession)}
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
        from ..services import BanwordQueryService, BanwordUpdateService
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
                IBanwordQueryService: BanwordQueryService(self.dbsession),
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

    def test_boards_get(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.admin import boards_get
        from . import mock_service

        board1 = self._make(Board(slug="foo", title="Foo", status="open"))
        board2 = self._make(Board(slug="baz", title="Baz", status="restricted"))
        board3 = self._make(Board(slug="bax", title="Bax", status="locked"))
        board4 = self._make(Board(slug="wel", title="Wel", status="open"))
        board5 = self._make(Board(slug="bar", title="Bar", status="archived"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        response = boards_get(request)
        self.assertEqual(response["boards"], [board5, board3, board2, board1, board4])

    def test_board_new_get(self):
        from ..forms import AdminBoardNewForm
        from ..views.admin import board_new_get

        self.request.method = "GET"
        response = board_new_get(self.request)
        self.assertIsInstance(response["form"], AdminBoardNewForm)

    def test_board_new_post(self):
        from ..interfaces import IBoardCreateService
        from ..models import Board
        from ..services import BoardCreateService
        from ..views.admin import board_new_post
        from . import mock_service

        request = mock_service(
            self.request, {IBoardCreateService: BoardCreateService(self.dbsession)}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["slug"] = "foobar"
        request.POST["title"] = "Foobar"
        request.POST["status"] = "open"
        request.POST["description"] = "Foobar"
        request.POST["agreements"] = "I agree"
        request.POST["settings"] = '{"name":"Nameless Foobar"}'
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_board", "/admin/boards/{board}")
        response = board_new_post(request)
        board = self.dbsession.query(Board).first()
        self.assertEqual(response.location, "/admin/boards/foobar")
        self.assertEqual(self.dbsession.query(Board).count(), 1)
        self.assertEqual(board.slug, "foobar")
        self.assertEqual(board.title, "Foobar")
        self.assertEqual(board.description, "Foobar")
        self.assertEqual(board.agreements, "I agree")
        self.assertEqual(
            board.settings,
            {
                "max_posts": 1000,
                "name": "Nameless Foobar",
                "post_delay": 10,
                "use_ident": True,
            },
        )

    def test_board_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["slug"] = "foobar"
        self.request.POST["title"] = "Foobar"
        self.request.POST["status"] = "open"
        self.request.POST["description"] = "Foobar"
        self.request.POST["agreements"] = "I agree"
        self.request.POST["settings"] = "{}"
        with self.assertRaises(BadCSRFToken):
            board_new_post(self.request)

    def test_board_new_post_invalid_status(self):
        from ..models import Board
        from ..views.admin import board_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["slug"] = "foobar"
        self.request.POST["title"] = "Foobar"
        self.request.POST["status"] = "foobar"
        self.request.POST["description"] = "Foobar"
        self.request.POST["agreements"] = "I agree"
        self.request.POST["settings"] = "{}"
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = board_new_post(self.request)
        self.assertEqual(self.dbsession.query(Board).count(), 0)
        self.assertEqual(response["form"].slug.data, "foobar")
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].status.data, "foobar")
        self.assertEqual(response["form"].description.data, "Foobar")
        self.assertEqual(response["form"].agreements.data, "I agree")
        self.assertEqual(response["form"].settings.data, "{}")
        self.assertDictEqual(
            response["form"].errors, {"status": ["Not a valid choice"]}
        )

    def test_board_new_post_invalid_settings(self):
        from ..models import Board
        from ..views.admin import board_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["slug"] = "foobar"
        self.request.POST["title"] = "Foobar"
        self.request.POST["status"] = "open"
        self.request.POST["description"] = "Foobar"
        self.request.POST["agreements"] = "I agree"
        self.request.POST["settings"] = "foobar"
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = board_new_post(self.request)
        self.assertEqual(self.dbsession.query(Board).count(), 0)
        self.assertEqual(response["form"].slug.data, "foobar")
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].status.data, "open")
        self.assertEqual(response["form"].description.data, "Foobar")
        self.assertEqual(response["form"].agreements.data, "I agree")
        self.assertEqual(response["form"].settings.data, "foobar")
        self.assertDictEqual(
            response["form"].errors, {"settings": ["Must be a valid JSON."]}
        )

    def test_board_get(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.admin import board_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "foobar"
        response = board_get(request)
        self.assertEqual(response["board"], board)

    def test_board_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_get
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "foobar"
        with self.assertRaises(NoResultFound):
            board_get(request)

    def test_board_edit_get(self):
        from ..forms import AdminBoardForm
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.admin import board_edit_get
        from . import mock_service

        board = self._make(
            Board(
                title="Foobar",
                slug="foobar",
                description="Foobar",
                agreements="I agree",
                settings={"name": "Nameless Foobar"},
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "foobar"
        response = board_edit_get(request)
        self.assertEqual(response["board"], board)
        self.assertIsInstance(response["form"], AdminBoardForm)
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].status.data, "open")
        self.assertEqual(response["form"].description.data, "Foobar")
        self.assertEqual(response["form"].agreements.data, "I agree")
        self.assertEqual(
            response["form"].settings.data,
            "{\n"
            + '    "max_posts": 1000,\n'
            + '    "name": "Nameless Foobar",\n'
            + '    "post_delay": 10,\n'
            + '    "use_ident": true\n'
            + "}",
        )

    def test_board_edit_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_edit_get
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "foobar"
        with self.assertRaises(NoResultFound):
            board_edit_get(request)

    def test_board_edit_post(self):
        from ..interfaces import IBoardQueryService, IBoardUpdateService
        from ..models import Board
        from ..services import BoardQueryService, BoardUpdateService
        from ..views.admin import board_edit_post
        from . import mock_service

        board = self._make(Board(slug="baz", title="Baz"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IBoardUpdateService: BoardUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "baz"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["title"] = "Foobar"
        request.POST["status"] = "locked"
        request.POST["description"] = "Foobar"
        request.POST["agreements"] = "I agree"
        request.POST["settings"] = '{"name":"Nameless Foobar"}'
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_board", "/admin/boards/{board}")
        response = board_edit_post(request)
        self.assertEqual(response.location, "/admin/boards/baz")
        self.assertEqual(board.title, "Foobar")
        self.assertEqual(board.status, "locked")
        self.assertEqual(board.description, "Foobar")
        self.assertEqual(board.agreements, "I agree")
        self.assertEqual(
            board.settings,
            {
                "max_posts": 1000,
                "name": "Nameless Foobar",
                "post_delay": 10,
                "use_ident": True,
            },
        )

    def test_board_edit_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_edit_post
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "POST"
        request.matchdict["board"] = "notexists"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_edit_post(request)

    def test_board_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..models import Board
        from ..views.admin import board_edit_post

        board = self._make(Board(slug="baz", title="Baz"))
        self.dbsession.commit()
        self.request.method = "POST"
        self.request.matchdict["board"] = board.slug
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["title"] = "Foobar"
        self.request.POST["status"] = "open"
        self.request.POST["description"] = "Foobar"
        self.request.POST["agreements"] = "I agree"
        self.request.POST["settings"] = "{}"
        with self.assertRaises(BadCSRFToken):
            board_edit_post(self.request)

    def test_board_edit_post_invalid_status(self):
        from ..interfaces import IBoardQueryService, IBoardUpdateService
        from ..models import Board
        from ..services import BoardQueryService, BoardUpdateService
        from ..views.admin import board_edit_post
        from . import mock_service

        board = self._make(Board(slug="baz", title="Baz"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IBoardUpdateService: BoardUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "baz"
        request.POST = MultiDict([])
        request.POST["title"] = "Foobar"
        request.POST["status"] = "foobar"
        request.POST["description"] = "Foobar"
        request.POST["agreements"] = "I agree"
        request.POST["settings"] = '{"name":"Nameless Foobar"}'
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_board", "/admin/boards/{board}")
        response = board_edit_post(request)
        self.assertEqual(board.status, "open")
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].status.data, "foobar")
        self.assertEqual(response["form"].description.data, "Foobar")
        self.assertEqual(response["form"].agreements.data, "I agree")
        self.assertEqual(response["form"].settings.data, '{"name":"Nameless Foobar"}')
        self.assertDictEqual(
            response["form"].errors, {"status": ["Not a valid choice"]}
        )

    def test_board_edit_post_invalid_settings(self):
        from ..interfaces import IBoardQueryService, IBoardUpdateService
        from ..models import Board
        from ..services import BoardQueryService, BoardUpdateService
        from ..views.admin import board_edit_post
        from . import mock_service

        board = self._make(Board(slug="baz", title="Baz"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IBoardUpdateService: BoardUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "baz"
        request.POST = MultiDict([])
        request.POST["title"] = "Foobar"
        request.POST["status"] = "locked"
        request.POST["description"] = "Foobar"
        request.POST["agreements"] = "I agree"
        request.POST["settings"] = "invalid"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_board", "/admin/boards/{board}")
        response = board_edit_post(request)
        self.assertEqual(board.status, "open")
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].status.data, "locked")
        self.assertEqual(response["form"].description.data, "Foobar")
        self.assertEqual(response["form"].agreements.data, "I agree")
        self.assertEqual(response["form"].settings.data, "invalid")
        self.assertDictEqual(
            response["form"].errors, {"settings": ["Must be a valid JSON."]}
        )

    def test_board_topics_get(self):
        from datetime import datetime, timedelta
        from ..interfaces import ITopicQueryService, IBoardQueryService
        from ..models import Board, Topic, TopicMeta
        from ..services import TopicQueryService, BoardQueryService
        from ..views.admin import board_topics_get
        from . import mock_service

        def _make_topic(days=0, **kwargs):
            topic = self._make(Topic(**kwargs))
            self._make(
                TopicMeta(
                    topic=topic,
                    post_count=0,
                    posted_at=datetime.now(),
                    bumped_at=datetime.now() - timedelta(days=days),
                )
            )
            return topic

        board1 = self._make(Board(title="Foo", slug="foo"))
        board2 = self._make(Board(title="Bar", slug="bar"))
        topic1 = _make_topic(0.1, board=board1, title="Foo")
        topic2 = _make_topic(1, board=board1, title="Foo")
        topic3 = _make_topic(2, board=board1, title="Foo")
        topic4 = _make_topic(3, board=board1, title="Foo")
        topic5 = _make_topic(4, board=board1, title="Foo")
        topic6 = _make_topic(5, board=board1, title="Foo")
        topic7 = _make_topic(6, board=board1, title="Foo")
        _make_topic(6.1, board=board2, title="Foo")
        topic9 = _make_topic(6.2, board=board1, title="Foo", status="locked")
        topic10 = _make_topic(6.3, board=board1, title="Foo", status="archived")
        topic11 = _make_topic(7, board=board1, title="Foo")
        topic12 = _make_topic(8, board=board1, title="Foo")
        topic13 = _make_topic(9, board=board1, title="Foo")
        _make_topic(0.2, board=board2, title="Foo")
        topic15 = _make_topic(0.2, board=board1, title="Foo")
        _make_topic(7, board=board1, title="Foo", status="archived")
        _make_topic(7, board=board1, title="Foo", status="locked")
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = "foo"
        response = board_topics_get(request)
        self.assertEqual(response["board"], board1)
        self.assertEqual(
            response["topics"],
            [
                topic1,
                topic15,
                topic2,
                topic3,
                topic4,
                topic5,
                topic6,
                topic7,
                topic9,
                topic10,
                topic11,
                topic12,
                topic13,
            ],
        )

    def test_board_topics_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import ITopicQueryService, IBoardQueryService
        from ..services import TopicQueryService, BoardQueryService
        from ..views.admin import board_topics_get
        from . import mock_service

        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        with self.assertRaises(NoResultFound):
            board_topics_get(request)

    def test_board_topic_new_get(self):
        from ..forms import TopicForm
        from ..models import Board, User, UserSession
        from ..interfaces import IBoardQueryService, IUserLoginService
        from ..services import BoardQueryService, UserLoginService
        from ..views.admin import board_topic_new_get
        from . import mock_service

        board = self._make(Board(slug="foo", title="Foobar"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(UserSession(user=user, token="foo_token", ip_address="127.0.0.1"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = "foo"
        request.client_addr = "127.0.0.1"
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_new_get(request)
        self.assertEqual(response["user"], user)
        self.assertEqual(response["board"], board)
        self.assertIsInstance(response["form"], TopicForm)

    def test_board_topic_new_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, IUserLoginService
        from ..models import User, UserSession
        from ..services import BoardQueryService, UserLoginService
        from ..views.admin import board_topic_new_get
        from . import mock_service

        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(UserSession(user=user, token="foo_token", ip_address="127.0.0.1"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.client_addr = "127.0.0.1"
        self.config.testing_securitypolicy(userid="foo_token")
        with self.assertRaises(NoResultFound):
            board_topic_new_get(request)

    def test_board_topic_new_post(self):
        from ..models import Board, Topic, User, UserSession
        from ..interfaces import (
            IBoardQueryService,
            IUserLoginService,
            ITopicCreateService,
        )
        from ..services import (
            BoardQueryService,
            UserLoginService,
            TopicCreateService,
            IdentityService,
            SettingQueryService,
            UserQueryService,
        )
        from ..views.admin import board_topic_new_post
        from . import mock_service, make_cache_region, DummyRedis

        board = self._make(Board(slug="foo", title="Foobar"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(UserSession(user=user, token="foo_token", ip_address="127.0.0.1"))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        request = mock_service(
            self.request,
            {
                "db": self.dbsession,
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
                ITopicCreateService: TopicCreateService(
                    self.dbsession,
                    IdentityService(redis_conn, 10),
                    SettingQueryService(self.dbsession, cache_region),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "foo"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["title"] = "Foobar"
        request.POST["body"] = "Hello, world"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        self.config.add_route("admin_board_topic", "/admin/boards/{board}/{topic}")
        response = board_topic_new_post(request)
        topic = self.dbsession.query(Topic).one()
        self.assertEqual(response.location, "/admin/boards/foo/%s" % topic.id)
        self.assertEqual(topic.board, board)
        self.assertEqual(topic.title, "Foobar")
        self.assertEqual(topic.posts[0].body, "Hello, world")
        self.assertEqual(topic.posts[0].ip_address, "127.0.0.1")
        self.assertEqual(topic.posts[0].ident, "fooident")
        self.assertEqual(topic.posts[0].ident_type, "ident_admin")
        self.assertEqual(topic.posts[0].name, "Foo")
        self.assertTrue(topic.posts[0].bumped)

    def test_board_topic_new_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import Topic, User, UserSession
        from ..interfaces import IBoardQueryService, IUserLoginService
        from ..services import BoardQueryService, UserLoginService
        from ..views.admin import board_topic_new_post
        from . import mock_service

        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(UserSession(user=user, token="foo_token", ip_address="127.0.0.1"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "notfound"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["title"] = "Foobar"
        request.POST["body"] = "Hello, world"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        with self.assertRaises(NoResultFound):
            board_topic_new_post(request)
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topic_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_topic_new_post

        self.request.method = "POST"
        self.request.matchdict["board"] = "foo"
        self.request.client_addr = "127.0.0.1"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["title"] = "Foobar"
        self.request.POST["body"] = "Hello, world"
        with self.assertRaises(BadCSRFToken):
            board_topic_new_post(self.request)

    def test_board_topic_new_post_invalid_title(self):
        from ..forms import TopicForm
        from ..interfaces import IBoardQueryService, IUserLoginService
        from ..models import Board, Topic, User, UserSession
        from ..services import BoardQueryService, UserLoginService
        from ..views.admin import board_topic_new_post
        from . import mock_service

        board = self._make(Board(slug="foo", title="Foobar"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(UserSession(user=user, token="foo_token", ip_address="127.0.0.1"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "foo"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["title"] = ""
        request.POST["body"] = "Hello, world"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_new_post(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["user"], user)
        self.assertIsInstance(response["form"], TopicForm)
        self.assertEqual(response["form"].title.data, "")
        self.assertEqual(response["form"].body.data, "Hello, world")
        self.assertDictEqual(
            response["form"].errors, {"title": ["This field is required."]}
        )
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topic_new_post_invalid_body(self):
        from ..forms import TopicForm
        from ..interfaces import IBoardQueryService, IUserLoginService
        from ..models import Board, Topic, User, UserSession
        from ..services import BoardQueryService, UserLoginService
        from ..views.admin import board_topic_new_post
        from . import mock_service

        board = self._make(Board(slug="foo", title="Foobar"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(UserSession(user=user, token="foo_token", ip_address="127.0.0.1"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "foo"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["title"] = "Foobar"
        request.POST["body"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_new_post(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["user"], user)
        self.assertIsInstance(response["form"], TopicForm)
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].body.data, "")
        self.assertDictEqual(
            response["form"].errors, {"body": ["This field is required."]}
        )
        self.assertEqual(self.dbsession.query(Topic).count(), 0)

    def test_board_topic_get(self):
        from ..forms import PostForm
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostQueryService,
            IUserLoginService,
        )
        from ..models import Board, Topic, Post, User, UserSession
        from ..services import (
            BoardQueryService,
            TopicQueryService,
            PostQueryService,
            UserLoginService,
        )
        from ..views.admin import board_topic_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(UserSession(user=user, token="foo_token", ip_address="127.0.0.1"))
        post1 = self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Fanboi",
                body="Lorem ipsum",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Fanboi",
                body="Dolor sit",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
                IPostQueryService: PostQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_get(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic1)
        self.assertEqual(response["posts"], [post1, post2])
        self.assertEqual(response["user"], user)
        self.assertIsInstance(response["form"], PostForm)

    def test_board_topic_get_query(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostQueryService,
            IUserLoginService,
        )
        from ..models import Board, Topic, Post, User, UserSession
        from ..services import (
            BoardQueryService,
            TopicQueryService,
            PostQueryService,
            UserLoginService,
        )
        from ..views.admin import board_topic_get
        from . import mock_service

        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(UserSession(user=user, token="foo_token", ip_address="127.0.0.1"))
        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        posts = []
        for i in range(50):
            posts.append(
                self._make(
                    Post(
                        topic=topic1,
                        number=i + 1,
                        name="Nameless Fanboi",
                        body="Lorem ipsum",
                        ip_address="127.0.0.1",
                    )
                )
            )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
                IPostQueryService: PostQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        request.matchdict["query"] = "1"
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_get(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic1)
        self.assertEqual(response["posts"], posts[0:1])
        request.matchdict["query"] = "50"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[49:50])
        request.matchdict["query"] = "51"
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)
        request.matchdict["query"] = "1-50"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts)
        request.matchdict["query"] = "10-20"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[9:20])
        request.matchdict["query"] = "51-99"
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)
        request.matchdict["query"] = "0-51"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts)
        request.matchdict["query"] = "-0"
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)
        request.matchdict["query"] = "-5"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[:5])
        request.matchdict["query"] = "45-"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[44:])
        request.matchdict["query"] = "100-"
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)
        request.matchdict["query"] = "recent"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[20:])
        request.matchdict["query"] = "l30"
        response = board_topic_get(request)
        self.assertEqual(response["posts"], posts[20:])

    def test_board_topic_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_get(request)

    def test_board_topic_get_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_get
        from . import mock_service

        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_get(request)

    def test_board_topic_get_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)

    def test_board_topic_get_wrong_board_query(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        request.matchdict["query"] = "l10"
        with self.assertRaises(HTTPNotFound):
            board_topic_get(request)

    def test_board_topic_post(self):
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IUserLoginService,
            IPostCreateService,
        )
        from ..models import Board, Topic, TopicMeta, Post, User, UserSession
        from ..services import (
            BoardQueryService,
            TopicQueryService,
            UserLoginService,
            PostCreateService,
            IdentityService,
            SettingQueryService,
            UserQueryService,
        )
        from ..views.admin import board_topic_post
        from . import mock_service, make_cache_region, DummyRedis

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
        self._make(TopicMeta(topic=topic, post_count=0))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(UserSession(user=user, token="foo_token", ip_address="127.0.0.1"))
        self.dbsession.commit()
        redis_conn = DummyRedis()
        cache_region = make_cache_region()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
                IPostCreateService: PostCreateService(
                    self.dbsession,
                    IdentityService(redis_conn, 10),
                    SettingQueryService(self.dbsession, cache_region),
                    UserQueryService(self.dbsession),
                ),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "foobar"
        request.matchdict["topic"] = topic.id
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["body"] = "Hello, world"
        request.POST["bumped"] = "t"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        self.config.add_route(
            "admin_board_topic_posts", "/admin/boards/{board}/{topic}/{query}"
        )
        response = board_topic_post(request)
        post = self.dbsession.query(Post).one()
        self.assertEqual(response.location, "/admin/boards/foobar/%s/recent" % topic.id)
        self.assertEqual(post.body, "Hello, world")
        self.assertEqual(post.ip_address, "127.0.0.1")
        self.assertEqual(post.ident, "fooident")
        self.assertEqual(post.ident_type, "ident_admin")
        self.assertEqual(post.name, "Foo")
        self.assertTrue(post.bumped)

    def test_board_topic_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Post
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_post
        from . import mock_service

        self._make(Board(title="Foobar", slug="foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "foobar"
        request.matchdict["topic"] = "-1"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["body"] = "Hello, world"
        request.POST["bumped"] = "t"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_board_topic_post_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..models import Post
        from ..services import BoardQueryService
        from ..views.admin import board_topic_post
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "POST"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["body"] = "Hello, world"
        request.POST["bumped"] = "t"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_post(request)
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_board_topic_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_topic_post

        self.request.method = "POST"
        self.request.matchdict["board"] = "foobar"
        self.request.matchdict["topic"] = "1"
        self.request.client_addr = "127.0.0.1"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["body"] = "Hello, world"
        self.request.POST["bumped"] = "t"
        with self.assertRaises(BadCSRFToken):
            board_topic_post(self.request)

    def test_board_topic_post_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_post
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        self._make(Board(title="Baz", slug="baz"))
        topic = self._make(Topic(board=board1, title="Demo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "baz"
        request.matchdict["topic"] = topic.id
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["body"] = "Hello, world"
        request.POST["bumped"] = "t"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_post(request)

    def test_board_topic_post_invalid_body(self):
        from ..forms import PostForm
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IUserLoginService,
        )
        from ..models import Board, Topic, Post, User, UserSession
        from ..services import BoardQueryService, TopicQueryService, UserLoginService
        from ..views.admin import board_topic_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
        user = self._make(
            User(
                username="foo",
                encrypted_password="bar",
                ident="fooident",
                ident_type="ident_admin",
                name="Foo",
            )
        )
        self._make(UserSession(user=user, token="foo_token", ip_address="127.0.0.1"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
                IUserLoginService: UserLoginService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "foobar"
        request.matchdict["topic"] = topic.id
        request.client_addr = "127.0.0.1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["body"] = ""
        request.POST["bumped"] = "t"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.testing_securitypolicy(userid="foo_token")
        response = board_topic_post(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)
        self.assertEqual(response["user"], user)
        self.assertIsInstance(response["form"], PostForm)
        self.assertEqual(response["form"].body.data, "")
        self.assertTrue(response["form"].bumped.data)
        self.assertDictEqual(
            response["form"].errors, {"body": ["This field is required."]}
        )
        self.assertEqual(self.dbsession.query(Post).count(), 0)

    def test_board_topic_edit_get(self):
        from ..forms import AdminTopicForm
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic.id
        response = board_topic_edit_get(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)
        self.assertIsInstance(response["form"], AdminTopicForm)
        self.assertEqual(response["form"].status.data, "open")

    def test_board_topic_edit_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_edit_get(request)

    def test_board_topic_edit_get_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_edit_get
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_edit_get(request)

    def test_board_topic_edit_get_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        self._make(Board(title="Baz", slug="baz"))
        topic = self._make(Topic(board=board1, title="Demo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = "baz"
        request.matchdict["topic"] = topic.id
        with self.assertRaises(HTTPNotFound):
            board_topic_edit_get(request)

    def test_board_topic_edit_post(self):
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            ITopicUpdateService,
        )
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService, TopicUpdateService
        from ..views.admin import board_topic_edit_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
                ITopicUpdateService: TopicUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["status"] = "locked"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route(
            "admin_board_topic_posts", "/admin/boards/{board}/{topic}/{query}"
        )
        self.assertEqual(topic.status, "open")
        response = board_topic_edit_post(request)
        self.assertEqual(response.location, "/admin/boards/foobar/%s/recent" % topic.id)
        self.assertEqual(topic.status, "locked")

    def test_board_topic_edit_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["status"] = "locked"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_edit_post(request)

    def test_board_topic_edit_post_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_edit_post
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "POST"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["status"] = "locked"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_edit_post(request)

    def test_board_topic_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_topic_edit_post

        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.method = "POST"
        self.request.matchdict["board"] = "foobar"
        self.request.matchdict["topic"] = "-1"
        with self.assertRaises(BadCSRFToken):
            board_topic_edit_post(self.request)

    def test_board_topic_edit_post_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_post
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        self._make(Board(title="Baz", slug="baz"))
        topic = self._make(Topic(board=board1, title="Demo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "baz"
        request.matchdict["topic"] = topic.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["status"] = "locked"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_edit_post(request)

    def test_board_topic_edit_post_invalid_status(self):
        from ..forms import AdminTopicForm
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_edit_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["status"] = "foobar"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = board_topic_edit_post(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)
        self.assertIsInstance(response["form"], AdminTopicForm)
        self.assertEqual(response["form"].status.data, "foobar")
        self.assertDictEqual(
            response["form"].errors, {"status": ["Not a valid choice"]}
        )

    def test_board_topic_delete_get(self):
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_delete_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Demo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic.id
        response = board_topic_delete_get(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)

    def test_board_topic_delete_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_delete_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_delete_get(request)

    def test_board_topic_delete_get_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_delete_get
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_delete_get(request)

    def test_board_topic_delete_get_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_delete_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        self._make(Board(title="Baz", slug="baz"))
        topic = self._make(Topic(board=board1, title="Demo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = "baz"
        request.matchdict["topic"] = topic.id
        with self.assertRaises(HTTPNotFound):
            board_topic_delete_get(request)

    def test_board_topic_delete_post(self):
        from sqlalchemy import inspect
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            ITopicDeleteService,
        )
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import BoardQueryService, TopicQueryService, TopicDeleteService
        from ..views.admin import board_topic_delete_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        topic_meta1 = self._make(TopicMeta(topic=topic1, post_count=2))
        topic_meta2 = self._make(TopicMeta(topic=topic2, post_count=1))
        post1 = self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Foo",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Foo",
                body="Foobar 2",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Foo",
                body="Foobar 3",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
                ITopicDeleteService: TopicDeleteService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_board_topics", "/admin/boards/{board}/topics")
        response = board_topic_delete_post(request)
        self.assertEqual(response.location, "/admin/boards/foobar/topics")
        self.dbsession.flush()
        self.assertTrue(inspect(topic1).was_deleted)
        self.assertFalse(inspect(topic2).was_deleted)
        self.assertTrue(inspect(topic_meta1).was_deleted)
        self.assertFalse(inspect(topic_meta2).was_deleted)
        self.assertTrue(inspect(post1).was_deleted)
        self.assertTrue(inspect(post2).was_deleted)
        self.assertFalse(inspect(post3).was_deleted)

    def test_board_topic_delete_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_delete_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_delete_post(request)

    def test_board_topic_delete_post_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_delete_post
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_delete_post(request)

    def test_board_topic_delete_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_topic_delete_post

        self.request.method = "GET"
        self.request.matchdict["board"] = "foobar"
        self.request.matchdict["topic"] = "-1"
        with self.assertRaises(BadCSRFToken):
            board_topic_delete_post(self.request)

    def test_board_topic_delete_post_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from sqlalchemy import inspect
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic, TopicMeta, Post
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_delete_post
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobar Baz", slug="baz"))
        topic1 = self._make(Topic(board=board1, title="Demo"))
        topic2 = self._make(Topic(board=board2, title="Demo 2"))
        topic_meta1 = self._make(TopicMeta(topic=topic1, post_count=2))
        topic_meta2 = self._make(TopicMeta(topic=topic2, post_count=1))
        post1 = self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Foo",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Foo",
                body="Foobar 2",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Foo",
                body="Foobar 3",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic1.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_delete_post(request)
        self.dbsession.flush()
        self.assertFalse(inspect(topic1).was_deleted)
        self.assertFalse(inspect(topic2).was_deleted)
        self.assertFalse(inspect(topic_meta1).was_deleted)
        self.assertFalse(inspect(topic_meta2).was_deleted)
        self.assertFalse(inspect(post1).was_deleted)
        self.assertFalse(inspect(post2).was_deleted)
        self.assertFalse(inspect(post3).was_deleted)

    def test_board_topic_posts_delete_get(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostQueryService,
        )
        from ..models import Board, Topic, Post
        from ..services import BoardQueryService, TopicQueryService, PostQueryService
        from ..views.admin import board_topic_posts_delete_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        posts = []
        for i in range(50):
            posts.append(
                self._make(
                    Post(
                        topic=topic1,
                        number=i + 1,
                        name="Nameless Fanboi",
                        body="Lorem ipsum",
                        ip_address="127.0.0.1",
                    )
                )
            )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
                IPostQueryService: PostQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        request.matchdict["query"] = "2"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic1)
        self.assertEqual(response["posts"], posts[1:2])
        request.matchdict["query"] = "50"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[49:50])
        request.matchdict["query"] = "51"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)
        request.matchdict["query"] = "2-50"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[1:])
        request.matchdict["query"] = "10-20"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[9:20])
        request.matchdict["query"] = "51-99"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)
        request.matchdict["query"] = "-0"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)
        request.matchdict["query"] = "45-"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[44:])
        request.matchdict["query"] = "100-"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)
        request.matchdict["query"] = "recent"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[20:])
        request.matchdict["query"] = "l30"
        response = board_topic_posts_delete_get(request)
        self.assertEqual(response["posts"], posts[20:])

    def test_board_topic_posts_delete_get_with_first_post(self):
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostQueryService,
        )
        from ..models import Board, Topic, Post
        from ..services import BoardQueryService, TopicQueryService, PostQueryService
        from ..views.admin import board_topic_posts_delete_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        posts = []
        for i in range(30):
            posts.append(
                self._make(
                    Post(
                        topic=topic1,
                        number=i + 1,
                        name="Nameless Fanboi",
                        body="Lorem ipsum",
                        ip_address="127.0.0.1",
                    )
                )
            )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
                IPostQueryService: PostQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        renderer = self.config.testing_add_renderer(
            "admin/boards/topics/posts/delete_error.mako"
        )
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts, query=None
        )
        request.matchdict["query"] = "1"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts[0:1], query="1"
        )
        request.matchdict["query"] = "1-30"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts, query="1-30"
        )
        request.matchdict["query"] = "0-31"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts, query="0-31"
        )
        request.matchdict["query"] = "-5"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts[:5], query="-5"
        )
        request.matchdict["query"] = "recent"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts, query="recent"
        )
        request.matchdict["query"] = "l30"
        board_topic_posts_delete_get(request)
        renderer.assert_(
            request=request, board=board, topic=topic1, posts=posts, query="l30"
        )

    def test_board_topic_posts_delete_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_posts_delete_get(request)

    def test_board_topic_posts_delete_get_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_posts_delete_get
        from . import mock_service

        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        with self.assertRaises(NoResultFound):
            board_topic_posts_delete_get(request)

    def test_board_topic_posts_delete_get_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)

    def test_board_topic_posts_delete_get_wrong_board_query(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_get
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        request.matchdict["query"] = "l10"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_get(request)

    def test_board_topic_posts_delete_post(self):
        from sqlalchemy import inspect
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostDeleteService,
            IPostQueryService,
        )
        from ..models import Board, Topic, Post
        from ..services import (
            BoardQueryService,
            TopicQueryService,
            PostDeleteService,
            PostQueryService,
        )
        from ..views.admin import board_topic_posts_delete_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        posts = []
        for i in range(50):
            posts.append(
                self._make(
                    Post(
                        topic=topic1,
                        number=i + 1,
                        name="Nameless Fanboi",
                        body="Lorem ipsum",
                        ip_address="127.0.0.1",
                    )
                )
            )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )

        def assert_posts_deleted(begin, end):
            if begin is not None:
                for p in posts[:begin]:
                    print(p.number, "f")
                    self.assertFalse(inspect(p).was_deleted)
            for p in posts[begin:end]:
                print(p.number, "t")
                self.assertTrue(inspect(p).was_deleted)
            if end is not None:
                for p in posts[end:]:
                    print(p.number, "f")
                    self.assertFalse(inspect(p).was_deleted)

        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
                IPostQueryService: PostQueryService(self.dbsession),
                IPostDeleteService: PostDeleteService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        request.matchdict["query"] = "2"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route(
            "admin_board_topic_posts", "/admin/boards/{board}/{topic}/{query}"
        )
        response = board_topic_posts_delete_post(request)
        self.dbsession.flush()
        self.assertEqual(
            response.location, "/admin/boards/foobar/%s/recent" % topic1.id
        )
        assert_posts_deleted(1, 2)
        self.dbsession.rollback()
        request.matchdict["query"] = "50"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(49, 50)
        self.dbsession.rollback()
        request.matchdict["query"] = "51"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "2-50"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(1, None)
        self.dbsession.rollback()
        request.matchdict["query"] = "10-20"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(9, 20)
        self.dbsession.rollback()
        request.matchdict["query"] = "51-99"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "-0"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "45-"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(44, None)
        self.dbsession.rollback()
        request.matchdict["query"] = "100-"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "recent"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(20, None)
        self.dbsession.rollback()
        request.matchdict["query"] = "l30"
        board_topic_posts_delete_post(request)
        self.dbsession.flush()
        assert_posts_deleted(20, None)

    def test_board_topic_posts_delete_post_first_post(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import (
            IBoardQueryService,
            ITopicQueryService,
            IPostQueryService,
        )
        from ..models import Board, Topic, Post
        from ..services import BoardQueryService, TopicQueryService, PostQueryService
        from ..views.admin import board_topic_posts_delete_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Demo"))
        topic2 = self._make(Topic(board=board, title="Demo 2"))
        posts = []
        for i in range(30):
            posts.append(
                self._make(
                    Post(
                        topic=topic1,
                        number=i + 1,
                        name="Nameless Fanboi",
                        body="Lorem ipsum",
                        ip_address="127.0.0.1",
                    )
                )
            )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
                IPostQueryService: PostQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = topic1.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "1"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "1-30"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "0-31"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "-5"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "recent"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)
        request.matchdict["query"] = "l30"
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)

    def test_board_topic_posts_delete_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_post
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board.slug
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_posts_delete_post(request)

    def test_board_topic_posts_delete_post_not_found_board(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_topic_posts_delete_post
        from . import mock_service

        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "notexists"
        request.matchdict["topic"] = "-1"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_topic_posts_delete_post(request)

    def test_board_topic_posts_delete_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_topic_posts_delete_post

        self.request.method = "GET"
        self.request.matchdict["board"] = "foobar"
        self.request.matchdict["topic"] = "1"
        with self.assertRaises(BadCSRFToken):
            board_topic_posts_delete_post(self.request)

    def test_board_topic_posts_delete_post_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_post
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)

    def test_board_topic_posts_delete_post_wrong_board_query(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IBoardQueryService, ITopicQueryService
        from ..models import Board, Topic
        from ..services import BoardQueryService, TopicQueryService
        from ..views.admin import board_topic_posts_delete_post
        from . import mock_service

        board1 = self._make(Board(title="Foobar", slug="foobar"))
        board2 = self._make(Board(title="Foobaz", slug="foobaz"))
        topic = self._make(Topic(board=board1, title="Foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                ITopicQueryService: TopicQueryService(self.dbsession),
            },
        )
        request.method = "GET"
        request.matchdict["board"] = board2.slug
        request.matchdict["topic"] = topic.id
        request.matchdict["query"] = "l10"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            board_topic_posts_delete_post(request)

    def test_pages_get(self):
        from sqlalchemy import inspect
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import pages_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        internal_pages = (("foo", "none"), ("bar", "markdown"), ("baz", "html"))

        class _WrappedPageQueryService(PageQueryService):
            def list_internal(self):
                return super(_WrappedPageQueryService, self).list_internal(
                    _internal_pages=internal_pages
                )

        page1 = self._make(
            Page(title="Foo", body="Hi", slug="test1", namespace="public")
        )
        page2 = self._make(
            Page(
                title="Bar",
                body="Hi",
                slug="test2",
                formatter="html",
                namespace="public",
            )
        )
        page3 = self._make(
            Page(
                title="Baz",
                body="Hi",
                slug="test3",
                formatter="none",
                namespace="public",
            )
        )
        self._make(
            Page(
                title="Test",
                body="Hi",
                slug="test4",
                formatter="markdown",
                namespace="internal",
            )
        )
        self._make(Page(title="bar", slug="bar", body="Hello", namespace="internal"))
        self._make(Page(title="hoge", slug="hoge", body="Hoge", namespace="internal"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        response = pages_get(request)
        self.assertEqual(response["pages"], [page2, page3, page1])
        self.assertEqual(response["pages_internal"][0].slug, "bar")
        self.assertEqual(response["pages_internal"][1].slug, "baz")
        self.assertEqual(response["pages_internal"][2].slug, "foo")
        self.assertEqual(response["pages_internal"][3].slug, "hoge")
        self.assertTrue(inspect(response["pages_internal"][0]).persistent)
        self.assertFalse(inspect(response["pages_internal"][1]).persistent)
        self.assertFalse(inspect(response["pages_internal"][2]).persistent)
        self.assertTrue(inspect(response["pages_internal"][3]).persistent)

    def test_page_new_get(self):
        from ..forms import AdminPublicPageNewForm
        from ..views.admin import page_new_get

        self.request.method = "GET"
        response = page_new_get(self.request)
        self.assertIsInstance(response["form"], AdminPublicPageNewForm)

    def test_page_new_post(self):
        from ..interfaces import IPageCreateService
        from ..models import Page
        from ..services import PageCreateService
        from ..views.admin import page_new_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageCreateService: PageCreateService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["title"] = "Foobar"
        request.POST["slug"] = "foobar"
        request.POST["body"] = "**Hello, world!**"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page", "/admin/pages/{page}")
        response = page_new_post(request)
        page = self.dbsession.query(Page).first()
        self.assertEqual(response.location, "/admin/pages/foobar")
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        self.assertEqual(page.slug, "foobar")
        self.assertEqual(page.title, "Foobar")
        self.assertEqual(page.body, "**Hello, world!**")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_page_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["title"] = "Foobar"
        self.request.POST["slug"] = "foobar"
        self.request.POST["body"] = "**Hello, world!**"
        with self.assertRaises(BadCSRFToken):
            page_new_post(self.request)

    def test_page_new_post_invalid_title(self):
        from ..forms import AdminPublicPageNewForm
        from ..models import Page
        from ..views.admin import page_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["title"] = ""
        self.request.POST["slug"] = "foobar"
        self.request.POST["body"] = "**Hello, world!**"
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = page_new_post(self.request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)
        self.assertIsInstance(response["form"], AdminPublicPageNewForm)
        self.assertEqual(response["form"].title.data, "")
        self.assertEqual(response["form"].slug.data, "foobar")
        self.assertEqual(response["form"].body.data, "**Hello, world!**")
        self.assertDictEqual(
            response["form"].errors, {"title": ["This field is required."]}
        )

    def test_page_new_post_invalid_slug(self):
        from ..forms import AdminPublicPageNewForm
        from ..models import Page
        from ..views.admin import page_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["title"] = "Foobar"
        self.request.POST["slug"] = ""
        self.request.POST["body"] = "**Hello, world!**"
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = page_new_post(self.request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)
        self.assertIsInstance(response["form"], AdminPublicPageNewForm)
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].slug.data, "")
        self.assertEqual(response["form"].body.data, "**Hello, world!**")
        self.assertDictEqual(
            response["form"].errors, {"slug": ["This field is required."]}
        )

    def test_page_new_post_invalid_body(self):
        from ..forms import AdminPublicPageNewForm
        from ..models import Page
        from ..views.admin import page_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["title"] = "Foobar"
        self.request.POST["slug"] = "foobar"
        self.request.POST["body"] = ""
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = page_new_post(self.request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)
        self.assertIsInstance(response["form"], AdminPublicPageNewForm)
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].slug.data, "foobar")
        self.assertEqual(response["form"].body.data, "")
        self.assertDictEqual(
            response["form"].errors, {"body": ["This field is required."]}
        )

    def test_page_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "foobar"
        response = page_get(request)
        self.assertEqual(response["page"], page)

    def test_page_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "notexists"
        with self.assertRaises(NoResultFound):
            page_get(request)

    def test_page_edit_get(self):
        from ..forms import AdminPublicPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_edit_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "foobar"
        response = page_edit_get(request)
        self.assertEqual(response["page"], page)
        self.assertIsInstance(response["form"], AdminPublicPageForm)
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].body.data, "**Hello**")

    def test_page_edit_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_edit_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "notexists"
        with self.assertRaises(NoResultFound):
            page_edit_get(request)

    def test_page_edit_post(self):
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IPageQueryService: PageQueryService(self.dbsession, cache_region),
                IPageUpdateService: PageUpdateService(self.dbsession, cache_region),
            },
        )
        request.method = "POST"
        request.matchdict["page"] = "foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["title"] = "Baz"
        request.POST["body"] = "**Baz**"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page", "/admin/pages/{page}")
        response = page_edit_post(request)
        self.assertEqual(response.location, "/admin/pages/foobar")
        self.assertEqual(page.slug, "foobar")
        self.assertEqual(page.title, "Baz")
        self.assertEqual(page.body, "**Baz**")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_page_edit_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "notexists"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            page_edit_post(request)

    def test_page_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..models import Page
        from ..views.admin import page_edit_post

        self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        self.request.method = "POST"
        self.request.matchdict["page"] = "notexists"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["title"] = "Baz"
        self.request.POST["body"] = "**Baz**"
        with self.assertRaises(BadCSRFToken):
            page_edit_post(self.request)

    def test_page_edit_post_invalid_title(self):
        from ..forms import AdminPublicPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["title"] = ""
        request.POST["body"] = "**Baz**"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = page_edit_post(request)
        self.assertIsInstance(response["form"], AdminPublicPageForm)
        self.assertEqual(response["form"].title.data, "")
        self.assertEqual(response["form"].body.data, "**Baz**")
        self.assertEqual(page.slug, "foobar")
        self.assertEqual(page.title, "Foobar")
        self.assertEqual(page.body, "**Hello**")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_page_edit_post_invalid_body(self):
        from ..forms import AdminPublicPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["title"] = "Baz"
        request.POST["body"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = page_edit_post(request)
        self.assertIsInstance(response["form"], AdminPublicPageForm)
        self.assertEqual(response["form"].title.data, "Baz")
        self.assertEqual(response["form"].body.data, "")
        self.assertEqual(page.slug, "foobar")
        self.assertEqual(page.title, "Foobar")
        self.assertEqual(page.body, "**Hello**")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_page_delete_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_delete_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "foobar"
        response = page_delete_get(request)
        self.assertEqual(response["page"], page)

    def test_page_delete_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_delete_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "notexists"
        with self.assertRaises(NoResultFound):
            page_delete_get(request)

    def test_page_delete_post(self):
        from ..interfaces import IPageDeleteService
        from ..models import Page
        from ..services import PageDeleteService
        from ..views.admin import page_delete_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageDeleteService: PageDeleteService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_pages", "/admin/pages")
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        response = page_delete_post(request)
        self.assertEqual(response.location, "/admin/pages")
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_delete_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageDeleteService
        from ..services import PageDeleteService
        from ..views.admin import page_delete_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageDeleteService: PageDeleteService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "notexists"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            page_delete_post(request)

    def test_page_delete_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_delete_post

        self.request.method = "POST"
        self.request.matchdict["page"] = "notexists"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        with self.assertRaises(BadCSRFToken):
            page_delete_post(self.request)

    def test_page_internal_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page = self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        response = page_internal_get(request)
        self.assertEqual(response["page_slug"], "global/foobar")
        self.assertEqual(response["page"], page)

    def test_page_internal_get_not_found(self):
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/notexists", "none"),)
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/notexists"
        response = page_internal_get(request)
        self.assertEqual(response["page_slug"], "global/notexists")
        self.assertIsNone(response["page"])

    def test_page_internal_get_not_allowed(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=tuple()
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        with self.assertRaises(HTTPNotFound):
            page_internal_get(request)

    def test_page_internal_edit_get(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page = self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        response = page_internal_edit_get(request)
        self.assertIsInstance(response["form"], AdminPageForm)
        self.assertEqual(response["form"].body.data, "<em>Hello</em>")
        self.assertEqual(response["page_slug"], "global/foobar")
        self.assertEqual(response["page"], page)

    def test_page_internal_edit_get_auto_create(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        response = page_internal_edit_get(request)
        self.assertIsInstance(response["form"], AdminPageForm)
        self.assertEqual(response["form"].body.data, None)
        self.assertEqual(response["page_slug"], "global/foobar")
        self.assertIsNone(response["page"])

    def test_page_internal_edit_not_allowed(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=tuple()
                )

        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/notallowed"
        with self.assertRaises(HTTPNotFound):
            page_internal_edit_get(request)

    def test_page_internal_edit_post(self):
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region()

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page = self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IPageQueryService: _WrappedPageQueryService(
                    self.dbsession, cache_region
                ),
                IPageUpdateService: PageUpdateService(self.dbsession, cache_region),
            },
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = "<em>World</em>"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page_internal", "/admin/pages_i/{page}")
        response = page_internal_edit_post(request)
        self.assertEqual(response.location, "/admin/pages_i/global/foobar")
        self.assertEqual(page.slug, "global/foobar")
        self.assertEqual(page.title, "global/foobar")
        self.assertEqual(page.body, "<em>World</em>")
        self.assertEqual(page.namespace, "internal")
        self.assertEqual(page.formatter, "html")

    def test_page_internal_edit_post_auto_create(self):
        from ..interfaces import IPageQueryService, IPageCreateService
        from ..models import Page
        from ..services import PageQueryService, PageCreateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageCreateService(PageCreateService):
            def create_internal(self, slug, body):
                return super(_WrappedPageCreateService, self).create_internal(
                    slug, body, _internal_pages=(("global/foobar", "html"),)
                )

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        request = mock_service(
            self.request,
            {
                IPageQueryService: _WrappedPageQueryService(
                    self.dbsession, cache_region
                ),
                IPageCreateService: _WrappedPageCreateService(
                    self.dbsession, cache_region
                ),
            },
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = "<em>World</em>"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page_internal", "/admin/pages_i/{page}")
        response = page_internal_edit_post(request)
        self.assertEqual(response.location, "/admin/pages_i/global/foobar")
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        page = self.dbsession.query(Page).first()
        self.assertEqual(page.slug, "global/foobar")
        self.assertEqual(page.title, "global/foobar")
        self.assertEqual(page.body, "<em>World</em>")
        self.assertEqual(page.namespace, "internal")
        self.assertEqual(page.formatter, "html")

    def test_page_internal_edit_post_not_allowed(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=tuple()
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = "<em>World</em>"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            page_internal_edit_post(request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_internal_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_internal_edit_post

        self.request.method = "GET"
        self.request.matchdict["page"] = "global/foobar"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["body"] = "<em>World</em>"
        with self.assertRaises(BadCSRFToken):
            page_internal_edit_post(self.request)

    def test_page_internal_edit_post_invalid_body(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page = self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IPageQueryService: _WrappedPageQueryService(
                    self.dbsession, cache_region
                ),
                IPageUpdateService: PageUpdateService(self.dbsession, cache_region),
            },
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = page_internal_edit_post(request)
        self.assertIsInstance(response["form"], AdminPageForm)
        self.assertEqual(response["form"].body.data, "")
        self.assertEqual(response["form"].errors, {"body": ["This field is required."]})
        self.assertEqual(response["page_slug"], "global/foobar")
        self.assertEqual(response["page"], page)
        self.assertEqual(page.slug, "global/foobar")
        self.assertEqual(page.title, "global/foobar")
        self.assertEqual(page.body, "<em>Hello</em>")
        self.assertEqual(page.namespace, "internal")
        self.assertEqual(page.formatter, "html")

    def test_page_internal_edit_post_auto_create_invalid_body(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = page_internal_edit_post(request)
        self.assertIsInstance(response["form"], AdminPageForm)
        self.assertEqual(response["form"].body.data, "")
        self.assertEqual(response["form"].errors, {"body": ["This field is required."]})
        self.assertEqual(response["page_slug"], "global/foobar")
        self.assertIsNone(response["page"])
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_internal_edit_post_cache(self):
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region()

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page_query_svc = PageQueryService(self.dbsession, cache_region)
        self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            ),
            "<em>Hello</em>",
        )
        request = mock_service(
            self.request,
            {
                IPageQueryService: _WrappedPageQueryService(
                    self.dbsession, cache_region
                ),
                IPageUpdateService: PageUpdateService(self.dbsession, cache_region),
            },
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = "<em>World</em>"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page_internal", "/admin/pages_i/{page}")
        response = page_internal_edit_post(request)
        self.assertEqual(response.location, "/admin/pages_i/global/foobar")
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            ),
            "<em>World</em>",
        )

    def test_page_internal_edit_post_auto_create_cache(self):
        from ..interfaces import IPageQueryService, IPageCreateService
        from ..services import PageQueryService, PageCreateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageCreateService(PageCreateService):
            def create_internal(self, slug, body):
                return super(_WrappedPageCreateService, self).create_internal(
                    slug, body, _internal_pages=(("global/foobar", "html"),)
                )

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page_query_svc = PageQueryService(self.dbsession, cache_region)
        self.assertIsNone(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            )
        )
        request = mock_service(
            self.request,
            {
                IPageQueryService: _WrappedPageQueryService(
                    self.dbsession, cache_region
                ),
                IPageCreateService: _WrappedPageCreateService(
                    self.dbsession, cache_region
                ),
            },
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = "<em>World</em>"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page_internal", "/admin/pages_i/{page}")
        response = page_internal_edit_post(request)
        self.assertEqual(response.location, "/admin/pages_i/global/foobar")
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            ),
            "<em>World</em>",
        )

    def test_page_internal_delete_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_delete_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page = self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        response = page_internal_delete_get(request)
        self.assertEqual(response["page"], page)

    def test_page_internal_delete_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_delete_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/notexists", "none"),)
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/notexists"
        with self.assertRaises(NoResultFound):
            page_internal_delete_get(request)

    def test_page_internal_delete_get_not_allowed(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_delete_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=tuple()
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        with self.assertRaises(HTTPNotFound):
            page_internal_delete_get(request)

    def test_page_internal_delete_post(self):
        from ..interfaces import IPageDeleteService
        from ..models import Page
        from ..services import PageDeleteService
        from ..views.admin import page_internal_delete_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageDeleteService: PageDeleteService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_pages", "/admin/pages")
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        response = page_internal_delete_post(request)
        self.assertEqual(response.location, "/admin/pages")
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_internal_delete_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageDeleteService
        from ..services import PageDeleteService
        from ..views.admin import page_internal_delete_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageDeleteService: PageDeleteService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "global/notexists"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            page_internal_delete_post(request)

    def test_page_internal_delete_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_internal_delete_post

        self.request.method = "POST"
        self.request.matchdict["page"] = "global/notexists"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        with self.assertRaises(BadCSRFToken):
            page_internal_delete_post(self.request)

    def test_page_internal_delete_post_cache(self):
        from ..interfaces import IPageDeleteService
        from ..models import Page
        from ..services import PageDeleteService, PageQueryService
        from ..views.admin import page_internal_delete_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        page_query_svc = PageQueryService(self.dbsession, cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            ),
            "<em>Hello</em>",
        )
        request = mock_service(
            self.request,
            {IPageDeleteService: PageDeleteService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_pages", "/admin/pages")
        response = page_internal_delete_post(request)
        self.assertEqual(response.location, "/admin/pages")
        self.assertIsNone(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            )
        )

    def test_settings_get(self):
        from ..interfaces import ISettingQueryService
        from ..views.admin import settings_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def list_all(self):
                return [("foo", "bar"), ("baz", "bax")]

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "GET"
        response = settings_get(request)
        self.assertEqual(response["settings"], [("foo", "bar"), ("baz", "bax")])

    def test_setting_get(self):
        from ..forms import AdminSettingForm
        from ..interfaces import ISettingQueryService
        from ..views.admin import setting_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return "foobar"

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "GET"
        request.matchdict["setting"] = "foo.bar"
        response = setting_get(request)
        self.assertEqual(response["key"], "foo.bar")
        self.assertIsInstance(response["form"], AdminSettingForm)
        self.assertEqual(response["form"].value.data, '"foobar"')

    def test_setting_get_unsafe(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import ISettingQueryService
        from ..views.admin import setting_get
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                raise KeyError(key)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "GET"
        request.matchdict["setting"] = "unsafekey"
        with self.assertRaises(HTTPNotFound):
            setting_get(request)

    def test_setting_post(self):
        from ..interfaces import ISettingQueryService, ISettingUpdateService
        from ..views.admin import setting_post
        from . import mock_service

        updated_key = None
        updated_value = None

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return "foobar"

        class _DummySettingUpdateService(object):
            def update(self, key, value):
                nonlocal updated_key
                nonlocal updated_value
                updated_key = key
                updated_value = value
                return True

        request = mock_service(
            self.request,
            {
                ISettingQueryService: _DummySettingQueryService(),
                ISettingUpdateService: _DummySettingUpdateService(),
            },
        )
        request.method = "POST"
        request.matchdict["setting"] = "foo.bar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["value"] = '{"bar":"baz"}'
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_settings", "/admin/settings")
        response = setting_post(request)
        self.assertEqual(response.location, "/admin/settings")
        self.assertEqual(updated_key, "foo.bar")
        self.assertEqual(updated_value, {"bar": "baz"})

    def test_setting_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import setting_post

        self.request.method = "POST"
        self.request.matchdict["setting"] = "foo.bar"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["value"] = '{"bar":"baz"}'
        self.config.add_route("admin_settings", "/admin/settings")
        with self.assertRaises(BadCSRFToken):
            setting_post(self.request)

    def test_setting_post_unsafe(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import ISettingQueryService
        from ..views.admin import setting_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                raise KeyError(key)

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.matchdict["setting"] = "foo.bar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["value"] = '{"bar":"baz"}'
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_settings", "/admin/settings")
        with self.assertRaises(HTTPNotFound):
            setting_post(request)

    def test_setting_post_invalid_value(self):
        from ..interfaces import ISettingQueryService
        from ..views.admin import setting_post
        from . import mock_service

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return "foobar"

        request = mock_service(
            self.request, {ISettingQueryService: _DummySettingQueryService()}
        )
        request.method = "POST"
        request.matchdict["setting"] = "foo.bar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["value"] = "invalid"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_settings", "/admin/settings")
        response = setting_post(request)
        self.assertEqual(response["form"].value.data, "invalid")
        self.assertDictEqual(
            response["form"].errors, {"value": ["Must be a valid JSON."]}
        )
