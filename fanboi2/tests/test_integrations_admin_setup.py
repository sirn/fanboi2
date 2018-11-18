import unittest
import unittest.mock

from webob.multidict import MultiDict

from . import IntegrationMixin


class TestIntegrationAdminSetup(IntegrationMixin, unittest.TestCase):
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
