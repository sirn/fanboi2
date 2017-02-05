import unittest
import unittest.mock
from fanboi2.models import redis_conn
from fanboi2.tests import DummyRedis, RegistryMixin, CacheMixin
from pyramid import testing


class TestRequestSerializer(unittest.TestCase):

    def _getTargetFunction(self):
        from fanboi2.utils import serialize_request
        return serialize_request

    def test_serialize(self):
        request = testing.DummyRequest()
        request.application_url = 'http://www.example.com/'
        request.referrer = 'http://www.example.com/'
        request.remote_addr = '127.0.0.1'
        request.url = 'http://www.example.com/foobar'
        request.user_agent = 'Mock/1.0'
        self.assertEqual(
            self._getTargetFunction()(request),
            {
                'application_url': 'http://www.example.com/',
                'referrer': 'http://www.example.com/',
                'remote_addr': '127.0.0.1',
                'url': 'http://www.example.com/foobar',
                'user_agent': 'Mock/1.0',
            }
        )

    def test_serialize_dict(self):
        request = {'foo': 1}
        self.assertEqual(self._getTargetFunction()(request), request)


class TestDnsBl(unittest.TestCase):

    def _makeOne(self, providers=None):
        from fanboi2.utils import Dnsbl
        if providers is None:
            providers = ['xbl.spamhaus.org']
        dnsbl = Dnsbl()
        dnsbl.configure_providers(providers)
        return dnsbl

    def test_init(self):
        dnsbl = self._makeOne()
        self.assertEqual(dnsbl.providers, ['xbl.spamhaus.org'])

    def test_init_no_providers(self):
        dnsbl = self._makeOne(providers=[])
        self.assertEqual(dnsbl.providers, [])

    def test_init_string_providers(self):
        dnsbl = self._makeOne(providers='xbl.spamhaus.org tor.ahbl.org')
        self.assertEqual(dnsbl.providers, ['xbl.spamhaus.org', 'tor.ahbl.org'])

    @unittest.mock.patch('socket.gethostbyname')
    def test_listed(self, lookup_call):
        lookup_call.return_value = '127.0.0.2'
        dnsbl = self._makeOne()
        self.assertEqual(dnsbl.listed('10.0.100.254'), True)
        lookup_call.assert_called_with('254.100.0.10.xbl.spamhaus.org.')

    @unittest.mock.patch('socket.gethostbyname')
    def test_listed_unlisted(self, lookup_call):
        import socket
        lookup_call.side_effect = socket.gaierror('foobar')
        dnsbl = self._makeOne()
        self.assertEqual(dnsbl.listed('10.0.100.1'), False)
        lookup_call.assert_called_with('1.100.0.10.xbl.spamhaus.org.')

    @unittest.mock.patch('socket.gethostbyname')
    def test_listed_invalid(self, lookup_call):
        lookup_call.return_value = '192.168.1.1'
        dnsbl = self._makeOne()
        self.assertEqual(dnsbl.listed('10.0.100.2'), False)

    @unittest.mock.patch('socket.gethostbyname')
    def test_listed_malformed(self, lookup_call):
        lookup_call.return_value = 'foobarbaz'
        dnsbl = self._makeOne()
        self.assertEqual(dnsbl.listed('10.0.100.2'), False)


class TestGeoIP(unittest.TestCase):

    def _makeOne(self, providers=None):
        from fanboi2.utils import GeoIP
        geoip = GeoIP()
        return geoip

    def _makeGeoIP2(self, country_code=None):
        class MockGeoIP2CountryResponse(object):
            @property
            def iso_code(self):
                return country_code

        class MockGeoIP2Response(object):
            @property
            def country(self):
                return MockGeoIP2CountryResponse()

        class MockGeoIP2(object):
            def country(self, ip_address):
                return MockGeoIP2Response()

        return MockGeoIP2()

    @unittest.mock.patch('geoip2.database.Reader')
    def test_init(self, reader):
        reader.return_value = self._makeGeoIP2()
        geoip = self._makeOne()
        geoip.configure_geoip2('/tmp/some/path')

    @unittest.mock.patch('geoip2.database.Reader')
    def test_init_no_path(self, reader):
        geoip = self._makeOne()
        geoip.configure_geoip2(None)
        assert not reader.called

    @unittest.mock.patch('geoip2.database.Reader')
    def test_init_file_not_found(self, reader):
        reader.side_effect = FileNotFoundError
        geoip = self._makeOne()
        geoip.configure_geoip2('/tmp/some/path')
        assert not geoip.geoip2

    @unittest.mock.patch('geoip2.database.Reader')
    def test_init_invalid_database(self, reader):
        from maxminddb.errors import InvalidDatabaseError
        reader.side_effect = InvalidDatabaseError
        geoip = self._makeOne()
        geoip.configure_geoip2('/tmp/some/path')
        assert not geoip.geoip2

    @unittest.mock.patch('geoip2.database.Reader')
    def test_country_code(self, reader):
        reader.return_value = self._makeGeoIP2(country_code='TH')
        geoip = self._makeOne()
        geoip.configure_geoip2('/tmp/some/path')
        self.assertEqual(geoip.country_code('127.0.0.1'), 'TH')

    @unittest.mock.patch('geoip2.database.Reader')
    def test_country_code_not_inited(self, reader):
        reader.return_value = self._makeGeoIP2()
        geoip = self._makeOne()
        self.assertIsNone(geoip.country_code('127.0.0.1'))

    @unittest.mock.patch('geoip2.database.Reader')
    def test_country_code_address_not_found(self, reader):
        from geoip2.errors import AddressNotFoundError
        class MockNotFoundGeoIP2(object):
            def country(self, ip_address):
                raise AddressNotFoundError
        reader.return_value = MockNotFoundGeoIP2()
        geoip = self._makeOne()
        geoip.configure_geoip2('/tmp/some/path')
        self.assertIsNone(geoip.country_code('127.0.0.1'))

    @unittest.mock.patch('geoip2.database.Reader')
    def test_country_code_not_found(self, reader):
        reader.return_value = self._makeGeoIP2()
        geoip = self._makeOne()
        geoip.configure_geoip2('/tmp/some/path')
        self.assertIsNone(geoip.country_code('127.0.0.1'))


class TestChecklist(unittest.TestCase):

    def _makeOne(self, data=None):
        from fanboi2.utils import Checklist
        checklist = Checklist()
        checklist.configure_checklist(data)
        return checklist

    def test_init(self):
        checklist = self._makeOne(['scope1/', 'scope2/foo,bar', '*/*'])
        self.assertDictEqual(checklist.data, {
            'scope1': [],
            'scope2': ['foo', 'bar'],
            '*': ['*'],
        })

    def test_init_none(self):
        checklist = self._makeOne(None)
        self.assertDictEqual(checklist.data, {})

    def test_init_empty(self):
        checklist = self._makeOne('')
        self.assertDictEqual(checklist.data, {})

    def test_fetch(self):
        checklist = self._makeOne(['scope1/', 'scope2/foo,bar', '*/*'])
        self.assertListEqual(checklist.fetch('scope1'), [])
        self.assertListEqual(checklist.fetch('scope2'), ['foo', 'bar'])
        self.assertListEqual(checklist.fetch('scope3'), ['*'])

    def test_fetch_empty(self):
        checklist = self._makeOne([])
        self.assertListEqual(checklist.fetch('scope1'), ['*'])
        self.assertListEqual(checklist.fetch('scope2'), ['*'])
        self.assertListEqual(checklist.fetch('scope3'), ['*'])

    def test_enabled(self):
        checklist = self._makeOne(['scope1/', 'scope2/foo,bar', '*/*'])
        self.assertFalse(checklist.enabled('scope1', 'foo'))
        self.assertFalse(checklist.enabled('scope1', 'bar'))
        self.assertFalse(checklist.enabled('scope1', 'baz'))
        self.assertTrue(checklist.enabled('scope2', 'foo'))
        self.assertTrue(checklist.enabled('scope2', 'bar'))
        self.assertFalse(checklist.enabled('scope2', 'baz'))
        self.assertTrue(checklist.enabled('scope3', 'foo'))
        self.assertTrue(checklist.enabled('scope3', 'bar'))
        self.assertTrue(checklist.enabled('scope3', 'baz'))

    def test_enabled_empty(self):
        checklist = self._makeOne([])
        self.assertTrue(checklist.enabled('scope1', 'foo'))
        self.assertTrue(checklist.enabled('scope1', 'bar'))
        self.assertTrue(checklist.enabled('scope1', 'baz'))
        self.assertTrue(checklist.enabled('scope2', 'foo'))
        self.assertTrue(checklist.enabled('scope2', 'bar'))
        self.assertTrue(checklist.enabled('scope2', 'baz'))
        self.assertTrue(checklist.enabled('scope3', 'foo'))
        self.assertTrue(checklist.enabled('scope3', 'bar'))
        self.assertTrue(checklist.enabled('scope3', 'baz'))


class TestAkismet(RegistryMixin, unittest.TestCase):

    def _makeOne(self, key='hogehoge'):
        from fanboi2.utils import Akismet
        akismet = Akismet()
        akismet.configure_key(key)
        return akismet

    def _makeResponse(self, content):
        class MockResponse(object):

            def __init__(self, content):
                self.content = content

        return MockResponse(content)

    def test_init(self):
        akismet = self._makeOne()
        self.assertEqual(akismet.key, 'hogehoge')

    # noinspection PyTypeChecker
    def test_init_no_key(self):
        akismet = self._makeOne(key=None)
        self.assertEqual(akismet.key, None)

    @unittest.mock.patch('requests.post')
    def test_spam(self, api_call):
        api_call.return_value = self._makeResponse(b'true')
        request = self._makeRequest()
        akismet = self._makeOne()
        self.assertEqual(akismet.spam(request, 'buy viagra'), True)
        api_call.assert_called_with(
            'https://hogehoge.rest.akismet.com/1.1/comment-check',
            headers=unittest.mock.ANY,
            data=unittest.mock.ANY,
            timeout=unittest.mock.ANY,
        )

    @unittest.mock.patch('requests.post')
    def test_spam_ham(self, api_call):
        api_call.return_value = self._makeResponse(b'false')
        request = self._makeRequest()
        akismet = self._makeOne()
        self.assertEqual(akismet.spam(request, 'Hogehogehogehoge!'), False)
        api_call.assert_called_with(
            'https://hogehoge.rest.akismet.com/1.1/comment-check',
            headers=unittest.mock.ANY,
            data=unittest.mock.ANY,
            timeout=unittest.mock.ANY,
        )

    @unittest.mock.patch('requests.post')
    def test_spam_timeout(self, api_call):
        import requests
        request = self._makeRequest()
        akismet = self._makeOne()
        api_call.side_effect = requests.Timeout('connection timed out')
        self.assertEqual(akismet.spam(request, 'buy viagra'), False)

    # noinspection PyTypeChecker
    @unittest.mock.patch('requests.post')
    def test_spam_no_key(self, api_call):
        request = self._makeRequest()
        akismet = self._makeOne(key=None)
        self.assertEqual(akismet.spam(request, 'buy viagra'), False)
        assert not api_call.called


class TestBlackBoxProxyDetector(unittest.TestCase):

    def _makeOne(self, settings={}):
        from fanboi2.utils.proxy import BlackBoxProxyDetector
        blackbox = BlackBoxProxyDetector(settings)
        return blackbox

    def _makeResponse(self, status_code, content):
        class MockResponse(object):

            def __init__(self, status_code, content):
                self.status_code = status_code
                self.content = content

        return MockResponse(status_code, content)

    def test_init(self):
        blackbox = self._makeOne({'url': 'http://www.example.com/'})
        self.assertEqual(blackbox.url, 'http://www.example.com/')

    def test_init_default(self):
        blackbox = self._makeOne()
        self.assertEqual(
            blackbox.url,
            'http://www.shroomery.org/ythan/proxycheck.php')

    @unittest.mock.patch('requests.get')
    def test_check(self, api_call):
        api_call.return_value = self._makeResponse(200, b'Y')
        blackbox = self._makeOne({'url': 'http://www.example.com/'})
        self.assertEqual(blackbox.check('8.8.8.8'), b'Y')
        api_call.assert_called_with(
            'http://www.example.com/',
            headers=unittest.mock.ANY,
            timeout=unittest.mock.ANY,
            params={'ip': '8.8.8.8'},
        )

    @unittest.mock.patch('requests.get')
    def test_check_timeout(self, api_call):
        import requests
        api_call.side_effect = requests.Timeout('connection timed out')
        blackbox = self._makeOne()
        self.assertIsNone(blackbox.check('8.8.8.8'))

    @unittest.mock.patch('requests.get')
    def test_check_status_error(self, api_call):
        api_call.return_value = self._makeResponse(500, b'Error')
        blackbox = self._makeOne()
        self.assertIsNone(blackbox.check('8.8.8.8'))

    @unittest.mock.patch('requests.get')
    def test_check_response_error(self, api_call):
        api_call.return_value = self._makeResponse(200, b'X')
        blackbox = self._makeOne()
        self.assertIsNone(blackbox.check('8.8.8.8'))

    def test_evaluate(self):
        blackbox = self._makeOne()
        self.assertEqual(blackbox.evaluate(b'Y'), True)

    def test_evaluate_negative(self):
        blackbox = self._makeOne()
        self.assertEqual(blackbox.evaluate(b'N'), False)

    def test_evaluate_unknown(self):
        blackbox = self._makeOne()
        self.assertEqual(blackbox.evaluate(b'Z'), False)


class TestGetIPIntelProxyDetector(unittest.TestCase):

    def _makeOne(self, settings={}):
        from fanboi2.utils.proxy import GetIPIntelProxyDetector
        getipintel = GetIPIntelProxyDetector(settings)
        return getipintel

    def _makeResponse(self, status_code, content):
        class MockResponse(object):

            def __init__(self, status_code, content):
                self.status_code = status_code
                self.content = content

        return MockResponse(status_code, content)

    def test_init(self):
        getipintel = self._makeOne({
            'url': 'http://www.example.com/',
            'email': 'foo@example.com',
            'flags': 'm',
        })
        self.assertEqual(getipintel.url, 'http://www.example.com/')
        self.assertEqual(getipintel.email, 'foo@example.com')
        self.assertEqual(getipintel.flags, 'm')

    def test_init_default(self):
        with self.assertRaises(ValueError):
            self._makeOne()

    def test_init_default_with_email(self):
        getipintel = self._makeOne({'email': 'foo@example.com'})
        self.assertEqual(
            getipintel.url,
            'http://check.getipintel.net/check.php')
        self.assertEqual(getipintel.email, 'foo@example.com')
        self.assertEqual(getipintel.flags, None)

    @unittest.mock.patch('requests.get')
    def test_check(self, api_call):
        api_call.return_value = self._makeResponse(200, b'1')
        getipintel = self._makeOne({
            'url': 'http://www.example.com/',
            'email': 'foo@example.com',
            'flags': 'm',
        })
        self.assertEqual(getipintel.check('8.8.8.8'), b'1')
        api_call.assert_called_with(
            'http://www.example.com/',
            headers=unittest.mock.ANY,
            timeout=unittest.mock.ANY,
            params={
                'ip': '8.8.8.8',
                'contact': 'foo@example.com',
                'flags': 'm',
            },
        )

    @unittest.mock.patch('requests.get')
    def test_check_no_flags(self, api_call):
        api_call.return_value = self._makeResponse(200, b'1')
        getipintel = self._makeOne({
            'url': 'http://www.example.com/',
            'email': 'foo@example.com',
        })
        self.assertEqual(getipintel.check('8.8.8.8'), b'1')
        api_call.assert_called_with(
            'http://www.example.com/',
            headers=unittest.mock.ANY,
            timeout=unittest.mock.ANY,
            params={
                'ip': '8.8.8.8',
                'contact': 'foo@example.com',
            },
        )

    @unittest.mock.patch('requests.get')
    def test_check_timeout(self, api_call):
        import requests
        api_call.side_effect = requests.Timeout('connection timed out')
        getipintel = self._makeOne({'email': 'foo@example.com'})
        self.assertIsNone(getipintel.check('8.8.8.8'))

    @unittest.mock.patch('requests.get')
    def test_check_status_error(self, api_call):
        api_call.return_value = self._makeResponse(500, b'1')
        getipintel = self._makeOne({'email': 'foo@example.com'})
        self.assertIsNone(getipintel.check('8.8.8.8'))

    @unittest.mock.patch('requests.get')
    def test_check_response_error(self, api_call):
        api_call.return_value = self._makeResponse(200, b'-1')
        getipintel = self._makeOne({'email': 'foo@example.com'})
        self.assertIsNone(getipintel.check('8.8.8.8'))

    def test_evaluate(self):
        getipintel = self._makeOne({'email': 'foo@example.com'})
        self.assertEqual(getipintel.evaluate(b'0.9901'), True)

    def test_evaluate_negative(self):
        getipintel = self._makeOne({'email': 'foo@example.com'})
        self.assertEqual(getipintel.evaluate(b'0.99'), False)
        self.assertEqual(getipintel.evaluate(b'0.98'), False)
        self.assertEqual(getipintel.evaluate(b'0'), False)

    def test_evaluate_unknown(self):
        getipintel = self._makeOne({'email': 'foo@example.com'})
        self.assertEqual(getipintel.evaluate(b'-1'), False)


class TestProxyDetector(CacheMixin, RegistryMixin, unittest.TestCase):

    def _makeOne(self, settings={}, key=None):
        from fanboi2.utils import ProxyDetector
        proxy_detector = ProxyDetector(cache_region=self._getRegion())
        proxy_detector.configure_from_config(settings, key)
        return proxy_detector

    @unittest.mock.patch('fanboi2.utils.proxy.BlackBoxProxyDetector')
    @unittest.mock.patch('fanboi2.utils.proxy.GetIPIntelProxyDetector')
    def test_init(self, GetIPIntelProxyDetector, BlackBoxProxyDetector):
        with unittest.mock.patch('fanboi2.utils.proxy.DETECTOR_PROVIDERS', {
                'blackbox': BlackBoxProxyDetector,
                'getipintel': GetIPIntelProxyDetector}):
            proxy_detector = self._makeOne({
                'proxy.providers': ['blackbox', 'getipintel'],
                'proxy.blackbox.url': 'http://www.example.com/blackbox',
                'proxy.getipintel.url': 'http://www.example.com/getipintel',
                'proxy.getipintel.email': 'foo@example.com',
                'proxy.getipintel.flags': 'm',
            }, 'proxy.')
            self.assertEqual(
                proxy_detector.providers,
                ['blackbox', 'getipintel']
            )
            BlackBoxProxyDetector.assert_called_with({
                'url': 'http://www.example.com/blackbox'
            })
            GetIPIntelProxyDetector.assert_called_with({
                'url': 'http://www.example.com/getipintel',
                'email': 'foo@example.com',
                'flags': 'm',
            })

    @unittest.mock.patch('fanboi2.utils.proxy.BlackBoxProxyDetector.check')
    @unittest.mock.patch('fanboi2.utils.proxy.GetIPIntelProxyDetector.check')
    def test_check(self, getipintel_check, blackbox_check):
        blackbox_check.return_value = b'N'
        getipintel_check.return_value = b'1'
        proxy_detector = self._makeOne({
            'providers': ['blackbox', 'getipintel'],
            'getipintel.email': 'foo@example.com',
        })
        self.assertEqual(proxy_detector.detect('8.8.8.8'), True)
        blackbox_check.assert_called_with('8.8.8.8')
        getipintel_check.assert_called_with('8.8.8.8')

    @unittest.mock.patch('fanboi2.utils.proxy.BlackBoxProxyDetector.check')
    @unittest.mock.patch('fanboi2.utils.proxy.GetIPIntelProxyDetector.check')
    def test_check_cached(self, getipintel_check, blackbox_check):
        blackbox_check.return_value = b'N'
        getipintel_check.return_value = b'0'
        proxy_detector = self._makeOne({
            'providers': ['blackbox', 'getipintel'],
            'getipintel.email': 'foo@example.com',
        })
        self.assertEqual(proxy_detector.detect('8.8.8.8'), False)
        self.assertEqual(proxy_detector.detect('8.8.8.8'), False)
        blackbox_check.assert_called_once_with('8.8.8.8')
        getipintel_check.assert_called_once_with('8.8.8.8')

    @unittest.mock.patch('fanboi2.utils.proxy.BlackBoxProxyDetector.check')
    @unittest.mock.patch('fanboi2.utils.proxy.GetIPIntelProxyDetector.check')
    def test_check_first_matched(self, getipintel_check, blackbox_check):
        blackbox_check.return_value = b'Y'
        getipintel_check.side_effective = AssertionError('should not called')
        proxy_detector = self._makeOne({
            'providers': ['blackbox', 'getipintel'],
            'getipintel.email': 'foo@example.com',
        })
        self.assertEqual(proxy_detector.detect('8.8.8.8'), True)
        blackbox_check.assert_called_with('8.8.8.8')
        self.assertFalse(getipintel_check.called)

    @unittest.mock.patch('fanboi2.utils.proxy.BlackBoxProxyDetector.check')
    @unittest.mock.patch('fanboi2.utils.proxy.GetIPIntelProxyDetector.check')
    def test_check_no_matched(self, getipintel_check, blackbox_check):
        blackbox_check.return_value = b'F'
        getipintel_check.return_value = b'0'
        proxy_detector = self._makeOne({
            'providers': ['blackbox', 'getipintel'],
            'getipintel.email': 'foo@example.com',
        })
        self.assertEqual(proxy_detector.detect('8.8.8.8'), False)
        blackbox_check.assert_called_with('8.8.8.8')
        getipintel_check.assert_called_with('8.8.8.8')

    @unittest.mock.patch('fanboi2.utils.proxy.BlackBoxProxyDetector.check')
    @unittest.mock.patch('fanboi2.utils.proxy.GetIPIntelProxyDetector.check')
    def test_check_error_skip(self, getipintel_check, blackbox_check):
        blackbox_check.return_value = None
        getipintel_check.return_value = None
        proxy_detector = self._makeOne({
            'providers': ['blackbox', 'getipintel'],
            'getipintel.email': 'foo@example.com',
        })
        self.assertEqual(proxy_detector.detect('8.8.8.8'), False)
        self.assertEqual(proxy_detector.detect('8.8.8.8'), False)
        self.assertEqual(blackbox_check.call_count, 2)
        self.assertEqual(getipintel_check.call_count, 2)
        blackbox_check.assert_called_with('8.8.8.8')
        getipintel_check.assert_called_with('8.8.8.8')


class TestRateLimiter(unittest.TestCase):

    def setUp(self):
        redis_conn._redis = DummyRedis()

    def tearDown(self):
        redis_conn._redis = None

    def _getTargetClass(self):
        from fanboi2.utils import RateLimiter
        return RateLimiter

    def _getHash(self, text):
        import hashlib
        return hashlib.md5(text.encode('utf8')).hexdigest()

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.remote_addr = '127.0.0.1'
        request.user_agent = 'TestBrowser/1.0'
        request.referrer = 'http://www.example.com/foo'
        testing.setUp(request=request)
        return request

    def test_init(self):
        request = self._makeRequest()
        ratelimit = self._getTargetClass()(request, namespace='foobar')
        self.assertEqual(ratelimit.key,
                         "rate:foobar:%s" % self._getHash('127.0.0.1'))

    def test_init_no_namespace(self):
        request = self._makeRequest()
        ratelimit = self._getTargetClass()(request)
        self.assertEqual(ratelimit.key,
                         "rate:None:%s" % self._getHash('127.0.0.1'))

    def test_limit(self):
        request = self._makeRequest()
        ratelimit = self._getTargetClass()(request, namespace='foobar')
        self.assertFalse(ratelimit.limited())
        self.assertEqual(ratelimit.timeleft(), 0)
        ratelimit.limit(seconds=30)
        self.assertTrue(ratelimit.limited())
        self.assertEqual(ratelimit.timeleft(), 30)

    def test_limit_no_seconds(self):
        request = self._makeRequest()
        ratelimit = self._getTargetClass()(request, namespace='foobar')
        ratelimit.limit()
        self.assertTrue(ratelimit.limited())
        self.assertEqual(ratelimit.timeleft(), 10)
