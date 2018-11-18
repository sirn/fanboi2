import unittest
import unittest.mock

from webob.multidict import MultiDict

from . import IntegrationMixin


class TestIntegrationAdminSettings(IntegrationMixin, unittest.TestCase):
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
