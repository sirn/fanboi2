import unittest

from pyramid import testing


class _DummyUserLoginService(object):
    def __init__(self, groups):
        self.groups = groups
        self._groups_token = None
        self._groups_ip_address = None
        self._seen_token = None
        self._seen_ip_address = None

    def groups_from_token(self, token, ip_address):
        self._groups_token = token
        self._groups_ip_address = ip_address
        return self.groups

    def mark_seen(self, token, ip_address):
        self._seen_token = token
        self._seen_ip_address = ip_address
        return True


class TestGroupFinder(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry

    def tearDown(self):
        testing.tearDown()

    def _get_target_function(self):
        from ..auth import groupfinder

        return groupfinder

    def test_groupfinder(self):
        from ..interfaces import IUserLoginService
        from . import mock_service

        user_login_svc = _DummyUserLoginService(["mod", "admin"])
        request = mock_service(self.request, {IUserLoginService: user_login_svc})
        request.client_addr = "127.0.0.1"
        self.assertEqual(
            self._get_target_function()("foobar", request), ["g:mod", "g:admin"]
        )
        self.assertEqual(user_login_svc._groups_token, "foobar")
        self.assertEqual(user_login_svc._groups_ip_address, "127.0.0.1")
        self.assertEqual(user_login_svc._seen_token, "foobar")
        self.assertEqual(user_login_svc._seen_ip_address, "127.0.0.1")

    def test_groupfinder_none(self):
        from ..interfaces import IUserLoginService
        from . import mock_service

        user_login_svc = _DummyUserLoginService(None)
        request = mock_service(self.request, {IUserLoginService: user_login_svc})
        request.client_addr = "127.0.0.1"
        self.assertIsNone(self._get_target_function()("foobar", request))
        self.assertEqual(user_login_svc._groups_token, "foobar")
        self.assertEqual(user_login_svc._groups_ip_address, "127.0.0.1")
        self.assertIsNone(user_login_svc._seen_token)
        self.assertIsNone(user_login_svc._seen_ip_address)

    def test_groupfinder_no_groups(self):
        from ..interfaces import IUserLoginService
        from . import mock_service

        user_login_svc = _DummyUserLoginService([])
        request = mock_service(self.request, {IUserLoginService: user_login_svc})
        request.client_addr = "127.0.0.1"
        self.assertEqual(self._get_target_function()("foobar", request), [])
        self.assertEqual(user_login_svc._groups_token, "foobar")
        self.assertEqual(user_login_svc._groups_ip_address, "127.0.0.1")
        self.assertEqual(user_login_svc._seen_token, "foobar")
        self.assertEqual(user_login_svc._seen_ip_address, "127.0.0.1")

    def test_groupfinder_no_user(self):
        self.assertIsNone(self._get_target_function()(None, self.request))
