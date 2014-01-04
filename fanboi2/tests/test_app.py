import unittest
from pyramid import testing


class TestRemoteAddr(unittest.TestCase):

    def _getFunction(self):
        from fanboi2 import remote_addr
        return remote_addr

    def _makeRequest(self, ipaddr, forwarded=None):
        request = testing.DummyRequest()
        request.environ = {'REMOTE_ADDR': ipaddr}
        if forwarded:
            request.environ['HTTP_X_FORWARDED_FOR'] = forwarded
        return request

    def test_remote_addr(self):
        request = self._makeRequest("171.100.10.1")
        self.assertEqual(self._getFunction()(request), "171.100.10.1")

    def test_private_fallback(self):
        request = self._makeRequest("10.0.1.1", "171.100.10.1")
        self.assertEqual(self._getFunction()(request), "171.100.10.1")

    def test_loopback_fallback(self):
        request = self._makeRequest("127.0.0.1", "171.100.10.1")
        self.assertEqual(self._getFunction()(request), "171.100.10.1")

    def test_private_without_fallback(self):
        request = self._makeRequest("10.0.1.1")
        self.assertEqual(self._getFunction()(request), "10.0.1.1")

    def test_loopback_without_fallback(self):
        request = self._makeRequest("127.0.0.1")
        self.assertEqual(self._getFunction()(request), "127.0.0.1")

    def test_remote_fallback(self):
        request = self._makeRequest("171.100.10.1", "8.8.8.8")
        self.assertEqual(self._getFunction()(request), "171.100.10.1")


class TestRouteName(unittest.TestCase):

    def _getFunction(self):
        from fanboi2 import route_name
        return route_name

    def _makeRequest(self, name):
        request = testing.DummyRequest()

        class MockMatchedRoute(object):

            def __init__(self, name):
                self.name = name

        request.matched_route = MockMatchedRoute(name)
        return request

    def test_route_name(self):
        request = self._makeRequest("foobar")
        self.assertEqual(self._getFunction()(request), "foobar")


class DummyStaticURLInfo:

    def __init__(self, result):
        self.result = result

    def generate(self, path, request, **kw):
        self.args = path, request, kw
        return self.result


class TestTaggedStaticUrl(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeRequest(self):
        from pyramid.url import URLMethodsMixin

        class Request(URLMethodsMixin):
            application_url = 'http://example.com:5432'
            script_name = ''

            def __init__(self, environ):
                self.environ = environ
                self.registry = None

        request = Request({})
        request.registry = self.config.registry
        return request

    def _getFunction(self):
        from fanboi2 import tagged_static_path
        return tagged_static_path

    def _getHash(self, package, path):
        import hashlib
        from pyramid.path import AssetResolver
        abspath = AssetResolver(package).resolve(path).abspath()
        with open(abspath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()[:8]

    def test_tagged_static_path(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo('foobar')
        request = self._makeRequest()
        request.registry.registerUtility(info, IStaticURLInfo)
        result = self._getFunction()(request, 'fanboi2:tests/test_app.py')
        self.assertEqual(result, 'foobar')
        self.assertEqual(
            info.args, ('fanboi2:tests/test_app.py', request, {
                '_app_url': '',
                '_query': {'h': self._getHash('fanboi2', 'tests/test_app.py')}
            }))

    def test_tagged_static_path_non_exists(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo('foobar')
        request = self._makeRequest()
        request.registry.registerUtility(info, IStaticURLInfo)
        with self.assertRaises(IOError):
            self._getFunction()(request, 'fanboi2:static/notexists')

    def test_tagged_static_path_non_package(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo('foobar')
        request = self._makeRequest()
        request.registry.registerUtility(info, IStaticURLInfo)
        result = self._getFunction()(request, 'tests/test_app.py')
        self.assertEqual(result, 'foobar')
        self.assertEqual(
            info.args, ('fanboi2:tests/test_app.py', request, {
                '_app_url': '',
                '_query': {'h': self._getHash('fanboi2', 'tests/test_app.py')}
            }))

    def test_tagged_static_path_non_package_non_exists(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo('foobar')
        request = self._makeRequest()
        request.registry.registerUtility(info, IStaticURLInfo)
        with self.assertRaises(IOError):
            self._getFunction()(request, 'static/notexists')
