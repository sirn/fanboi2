import unittest

from pyramid import testing

from ..interfaces import IUserLoginService


class _DummyUserLoginService(object):
    def __init__(self, groups):
        self.groups = groups

    def groups_from_token(self, token):
        return self.groups


class TestGroupFinder(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()

    def tearDown(self):
        testing.tearDown()

    def _get_target_function(self):
        from ..auth import groupfinder
        return groupfinder

    def test_groupfinder(self):
        from . import mock_service
        request = mock_service(self.request, {
            IUserLoginService: _DummyUserLoginService(['mod', 'admin'])})
        self.assertEqual(
            self._get_target_function()('foobar', request),
            ['g:mod', 'g:admin'])

    def test_groupfinder_none(self):
        from . import mock_service
        request = mock_service(self.request, {
            IUserLoginService: _DummyUserLoginService(None)})
        self.assertIsNone(self._get_target_function()('foobar', request))

    def test_groupfinder_no_groups(self):
        from . import mock_service
        request = mock_service(self.request, {
            IUserLoginService: _DummyUserLoginService([])})
        self.assertEqual(
            self._get_target_function()('foobar', request),
            [])

    def test_groupfinder_no_user(self):
        self.assertIsNone(self._get_target_function()(
            None,
            self.request))
