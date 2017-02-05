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
        request = self._makeRequest("10.0.1.1", "171.100.10.1, 127.0.0.1")
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

        request.matched_route = None
        if name is not None:
            request.matched_route = MockMatchedRoute(name)
        return request

    def test_route_name(self):
        request = self._makeRequest("foobar")
        self.assertEqual(self._getFunction()(request), "foobar")

    def test_route_name_not_exists(self):
        request = self._makeRequest(None)
        self.assertEqual(self._getFunction()(request), None)


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


class TestNormalizeSettings(unittest.TestCase):

    def _getFunction(self):
        from fanboi2 import normalize_settings
        return normalize_settings

    def _makeOne(self, settings=None, environ=None):
        if environ is None:
            environ = {}
        func = self._getFunction()
        return func(settings, environ)

    def test_defaults(self):
        result = self._makeOne({})
        self.assertEqual(result['sqlalchemy.url'], '')
        self.assertEqual(result['redis.url'], '')
        self.assertEqual(result['celery.broker'], '')
        self.assertEqual(result['dogpile.arguments.url'], '')
        self.assertEqual(result['session.url'], '')
        self.assertEqual(result['session.secret'], '')
        self.assertEqual(result['app.timezone'], '')
        self.assertEqual(result['app.secret'], '')
        self.assertEqual(result['app.akismet_key'], '')
        self.assertEqual(result['app.dnsbl_providers'], [])
        self.assertEqual(result['app.proxy_detect.providers'], [])
        self.assertEqual(result['app.proxy_detect.blackbox.url'], '')
        self.assertEqual(result['app.proxy_detect.getipintel.url'], '')
        self.assertEqual(result['app.proxy_detect.getipintel.email'], '')
        self.assertEqual(result['app.proxy_detect.getipintel.flags'], '')
        self.assertEqual(result['app.geoip2_database'], '')
        self.assertEqual(result['app.checklist'], [])

    def test_settings(self):
        r = self._makeOne({
            'sqlalchemy.url': 'postgresql://localhost:5432/foo',
            'redis.url': 'redis://127.0.0.1:6379/0',
            'celery.broker': 'redis://127.0.0.1:6379/1',
            'dogpile.arguments.url': '127.0.0.1:11211',
            'session.url': '127.0.0.1:11211',
            'session.secret': 'SESSION_SECRET',
            'app.timezone': 'Asia/Bangkok',
            'app.secret': 'APP_SECRET',
            'app.akismet_key': 'TEST_KEY',
            'app.dnsbl_providers': '1.example.com\n2.example.com 3.example.com',
            'app.proxy_detect.providers': 'blackbox getipintel',
            'app.proxy_detect.blackbox.url': 'http://www.example.com/foo',
            'app.proxy_detect.getipintel.url': 'http://www.example.com/bar',
            'app.proxy_detect.getipintel.email': 'test@example.com',
            'app.proxy_detect.getipintel.flags': 'm',
            'app.geoip2_database': '/var/geoip2/database',
            'app.checklist': 'country:th/\ncountry:jp/proxy_detect */*',
        })

        self.assertEqual(r['sqlalchemy.url'], 'postgresql://localhost:5432/foo')
        self.assertEqual(r['redis.url'], 'redis://127.0.0.1:6379/0')
        self.assertEqual(r['celery.broker'], 'redis://127.0.0.1:6379/1')
        self.assertEqual(r['dogpile.arguments.url'], '127.0.0.1:11211')
        self.assertEqual(r['session.url'], '127.0.0.1:11211')
        self.assertEqual(r['session.secret'], 'SESSION_SECRET')
        self.assertEqual(r['app.timezone'], 'Asia/Bangkok')
        self.assertEqual(r['app.secret'], 'APP_SECRET')
        self.assertEqual(r['app.akismet_key'], 'TEST_KEY')
        self.assertEqual(r['app.dnsbl_providers'], [
            '1.example.com',
            '2.example.com',
            '3.example.com',
        ])
        self.assertEqual(r['app.proxy_detect.providers'], [
            'blackbox',
            'getipintel',
        ])
        self.assertEqual(
            r['app.proxy_detect.blackbox.url'],
            'http://www.example.com/foo'
        )
        self.assertEqual(
            r['app.proxy_detect.getipintel.url'],
            'http://www.example.com/bar'
        )
        self.assertEqual(
            r['app.proxy_detect.getipintel.email'],
            'test@example.com'
        )
        self.assertEqual(r['app.proxy_detect.getipintel.flags'], 'm')
        self.assertEqual(r['app.geoip2_database'], '/var/geoip2/database')
        self.assertEqual(r['app.checklist'], [
            'country:th/',
            'country:jp/proxy_detect',
            '*/*',
        ])

    def test_environ(self):
        r = self._makeOne({}, environ={
            'SQLALCHEMY_URL': 'postgresql://localhost:5432/foo',
            'REDIS_URL': 'redis://127.0.0.1:6379/0',
            'CELERY_BROKER_URL': 'redis://127.0.0.1:6379/1',
            'DOGPILE_URL': '127.0.0.1:11211',
            'SESSION_URL': '127.0.0.1:11211',
            'SESSION_SECRET': 'SESSION_SECRET',
            'APP_TIMEZONE': 'Asia/Bangkok',
            'APP_SECRET': 'APP_SECRET',
            'APP_AKISMET_KEY': 'TEST_KEY',
            'APP_DNSBL_PROVIDERS': '1.example.com\n2.example.com 3.example.com',
            'APP_PROXY_DETECT_PROVIDERS': 'blackbox getipintel',
            'APP_PROXY_DETECT_BLACKBOX_URL': 'http://www.example.com/foo',
            'APP_PROXY_DETECT_GETIPINTEL_URL': 'http://www.example.com/bar',
            'APP_PROXY_DETECT_GETIPINTEL_EMAIL': 'test@example.com',
            'APP_PROXY_DETECT_GETIPINTEL_FLAGS': 'm',
            'APP_GEOIP2_DATABASE': '/var/geoip2/database',
            'APP_CHECKLIST': 'country:th/\ncountry:jp/proxy_detect */*',
        })

        self.assertEqual(r['sqlalchemy.url'], 'postgresql://localhost:5432/foo')
        self.assertEqual(r['redis.url'], 'redis://127.0.0.1:6379/0')
        self.assertEqual(r['celery.broker'], 'redis://127.0.0.1:6379/1')
        self.assertEqual(r['dogpile.arguments.url'], '127.0.0.1:11211')
        self.assertEqual(r['session.url'], '127.0.0.1:11211')
        self.assertEqual(r['session.secret'], 'SESSION_SECRET')
        self.assertEqual(r['app.timezone'], 'Asia/Bangkok')
        self.assertEqual(r['app.secret'], 'APP_SECRET')
        self.assertEqual(r['app.akismet_key'], 'TEST_KEY')
        self.assertEqual(r['app.dnsbl_providers'], [
            '1.example.com',
            '2.example.com',
            '3.example.com',
        ])
        self.assertEqual(r['app.proxy_detect.providers'], [
            'blackbox',
            'getipintel',
        ])
        self.assertEqual(
            r['app.proxy_detect.blackbox.url'],
            'http://www.example.com/foo'
        )
        self.assertEqual(
            r['app.proxy_detect.getipintel.url'],
            'http://www.example.com/bar'
        )
        self.assertEqual(
            r['app.proxy_detect.getipintel.email'],
            'test@example.com'
        )
        self.assertEqual(r['app.proxy_detect.getipintel.flags'], 'm')
        self.assertEqual(r['app.geoip2_database'], '/var/geoip2/database')
        self.assertEqual(r['app.checklist'], [
            'country:th/',
            'country:jp/proxy_detect',
            '*/*',
        ])

    def test_override(self):
        r = self._makeOne({
            'sqlalchemy.url': 'postgresql://localhost:5432/foo',
            'redis.url': 'redis://127.0.0.1:6379/0',
            'celery.broker': 'redis://127.0.0.1:6379/1',
            'dogpile.arguments.url': '127.0.0.1:11211',
            'session.url': '127.0.0.1:11211',
            'session.secret': 'SESSION_SECRET',
            'app.timezone': 'Asia/Bangkok',
            'app.secret': 'APP_SECRET',
            'app.akismet_key': 'TEST_KEY',
            'app.dnsbl_providers': '1.example.com\n2.example.com 3.example.com',
            'app.proxy_detect.providers': 'blackbox',
            'app.proxy_detect.blackbox.url': 'http://www.example.com/foo',
            'app.proxy_detect.getipintel.url': 'http://www.example.com/bar',
            'app.proxy_detect.getipintel.email': 'test@example.com',
            'app.proxy_detect.getipintel.flags': 'm',
            'app.geoip2_database': '/var/geoip2/database1',
            'app.checklist': '*/*',
        }, environ={
            'SQLALCHEMY_URL': 'postgresql://localhost:5432/baz',
            'REDIS_URL': 'redis://127.0.0.2:6379/0',
            'CELERY_BROKER_URL': 'redis://127.0.0.2:6379/1',
            'DOGPILE_URL': '127.0.0.2:11211',
            'SESSION_URL': '127.0.0.2:11211',
            'SESSION_SECRET': 'SESSION_SECRET_2',
            'APP_TIMEZONE': 'Asia/Tokyo',
            'APP_SECRET': 'APP_SECRET_2',
            'APP_AKISMET_KEY': 'TEST_KEY_2',
            'APP_DNSBL_PROVIDERS': '4.example.com\n5.example.com 6.example.com',
            'APP_PROXY_DETECT_PROVIDERS': 'blackbox getipintel',
            'APP_PROXY_DETECT_BLACKBOX_URL': 'http://www.example.com/bax',
            'APP_PROXY_DETECT_GETIPINTEL_URL': 'http://www.example.com/buz',
            'APP_PROXY_DETECT_GETIPINTEL_EMAIL': 'fuzz@example.com',
            'APP_PROXY_DETECT_GETIPINTEL_FLAGS': 'f',
            'APP_GEOIP2_DATABASE': '/var/geoip2/database2',
            'APP_CHECKLIST': 'country:th/\ncountry:jp/proxy_detect */*',
        })

        self.assertEqual(r['sqlalchemy.url'], 'postgresql://localhost:5432/baz')
        self.assertEqual(r['redis.url'], 'redis://127.0.0.2:6379/0')
        self.assertEqual(r['celery.broker'], 'redis://127.0.0.2:6379/1')
        self.assertEqual(r['dogpile.arguments.url'], '127.0.0.2:11211')
        self.assertEqual(r['session.url'], '127.0.0.2:11211')
        self.assertEqual(r['session.secret'], 'SESSION_SECRET_2')
        self.assertEqual(r['app.timezone'], 'Asia/Tokyo')
        self.assertEqual(r['app.secret'], 'APP_SECRET_2')
        self.assertEqual(r['app.akismet_key'], 'TEST_KEY_2')
        self.assertEqual(r['app.dnsbl_providers'], [
            '4.example.com',
            '5.example.com',
            '6.example.com',
        ])
        self.assertEqual(r['app.proxy_detect.providers'], [
            'blackbox',
            'getipintel',
        ])
        self.assertEqual(
            r['app.proxy_detect.blackbox.url'],
            'http://www.example.com/bax'
        )
        self.assertEqual(
            r['app.proxy_detect.getipintel.url'],
            'http://www.example.com/buz'
        )
        self.assertEqual(
            r['app.proxy_detect.getipintel.email'],
            'fuzz@example.com'
        )
        self.assertEqual(r['app.proxy_detect.getipintel.flags'], 'f')
        self.assertEqual(r['app.geoip2_database'], '/var/geoip2/database2')
        self.assertEqual(r['app.checklist'], [
            'country:th/',
            'country:jp/proxy_detect',
            '*/*',
        ])
