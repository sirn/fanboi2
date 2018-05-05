import unittest

from pyramid import testing


class _DummyUserLoginService(object):
    def __init__(self, groups):
        self.groups = groups
        self._called_token = None
        self._called_ip_address = None

    def groups_from_token(self, token, ip_address):
        self._called_token = token
        self._called_ip_address = ip_address
        return self.groups

    def mark_seen(self, token, ip_address):
        self._called_token = token
        self._called_ip_address = ip_address
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
        user_login_svc = _DummyUserLoginService(['mod', 'admin'])
        request = mock_service(self.request, {
            IUserLoginService: user_login_svc})
        request.client_addr = '127.0.0.1'
        self.assertEqual(
            self._get_target_function()('foobar', request),
            ['g:mod', 'g:admin'])
        self.assertEqual(user_login_svc._called_token, 'foobar')
        self.assertEqual(user_login_svc._called_ip_address, '127.0.0.1')

    def test_groupfinder_none(self):
        from ..interfaces import IUserLoginService
        from . import mock_service
        request = mock_service(self.request, {
            IUserLoginService: _DummyUserLoginService(None)})
        request.client_addr = '127.0.0.1'
        self.assertIsNone(self._get_target_function()('foobar', request))

    def test_groupfinder_no_groups(self):
        from ..interfaces import IUserLoginService
        from . import mock_service
        request = mock_service(self.request, {
            IUserLoginService: _DummyUserLoginService([])})
        request.client_addr = '127.0.0.1'
        self.assertEqual(
            self._get_target_function()('foobar', request),
            [])

    def test_groupfinder_no_user(self):
        self.assertIsNone(self._get_target_function()(
            None,
            self.request))


class TestMarkUserSeen(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry

    def tearDown(self):
        testing.tearDown()

    def _get_target_function(self):
        from ..auth import mark_user_seen
        return mark_user_seen

    def test_mark_user_seen(self):
        from pyramid.events import NewRequest
        from ..interfaces import IUserLoginService
        from . import mock_service
        user_login_svc = _DummyUserLoginService(['admin'])
        self.config.testing_securitypolicy('foo')
        request = mock_service(self.request, {
            IUserLoginService: user_login_svc})
        request.client_addr = '127.0.0.1'
        event = NewRequest(request)
        self._get_target_function()(event)
        self.assertEqual(user_login_svc._called_token, 'foo')
        self.assertEqual(user_login_svc._called_ip_address, '127.0.0.1')
