import unittest
import unittest.mock

from . import IntegrationMixin


class TestIntegrationAdminLogout(IntegrationMixin, unittest.TestCase):
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
