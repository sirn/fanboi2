import unittest
import unittest.mock

from . import IntegrationMixin


class TestIntegrationAdminDashboard(IntegrationMixin, unittest.TestCase):
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
