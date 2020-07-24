from collections import namedtuple
import unittest

from pyramid import testing


class TestRouteName(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry

    def tearDown(self):
        testing.tearDown()

    def _get_function(self):
        from .. import route_name

        return route_name

    def test_route_name(self):
        _MockMatchedRule = namedtuple("MatchedRule", ["name"])
        self.request.matched_route = _MockMatchedRule("foobar")
        self.assertEqual(self._get_function()(self.request), "foobar")

    def test_route_name_not_exists(self):
        self.request.matched_route = None
        self.assertEqual(self._get_function()(self.request), None)


class TestSettingsFromEnv(unittest.TestCase):
    def _getFunction(self):
        from .. import settings_from_env

        return settings_from_env

    def _make_one(self, environ, settings_map=None):
        from .. import NO_VALUE

        if settings_map is None:
            settings_map = (
                ("ENV_FOO", "test.foo", None, None),
                ("ENV_BAR", "test.bar", NO_VALUE, None),
                ("ENV_BAZ", "test.baz", "demo", None),
                ("ENV_BAX", "test.bax", "42", int),
            )
        func = self._getFunction()
        return func(settings_map, environ)

    def test_environ(self):
        result = self._make_one({"ENV_FOO": "foo", "ENV_BAR": "bar"})
        self.assertEqual(result["test.foo"], "foo")
        self.assertEqual(result["test.bar"], "bar")
        self.assertEqual(result["test.baz"], "demo")
        self.assertEqual(result["test.bax"], 42)

    def test_environ_missing(self):
        with self.assertRaises(RuntimeError):
            self._make_one({})


class TestTmMaybeActivate(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry

    def tearDown(self):
        testing.tearDown()

    def _get_function(self):
        from .. import tm_maybe_activate

        return tm_maybe_activate

    def test_paths(self):
        self.request.path_info = "/"
        self.assertTrue(self._get_function()(self.request))

    def test_static(self):
        self.request.path_info = "/static/"
        self.assertFalse(self._get_function()(self.request))
