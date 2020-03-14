from collections import namedtuple
import unittest
import unittest.mock


class TestAkismet(unittest.TestCase):
    def _make_one(self, key="hogehoge"):
        from ..filters.akismet import Akismet

        return Akismet(key, {})

    def _make_response(self, content):
        MockResponse = namedtuple("Response", ["content"])
        return MockResponse(content)

    def test_init(self):
        akismet = self._make_one(key="hogehoge")
        self.assertEqual(akismet.key, "hogehoge")

    def test_init_no_key(self):
        akismet = self._make_one(key=None)
        self.assertEqual(akismet.key, None)

    @unittest.mock.patch("requests.post")
    def test_should_reject(self, api_call):
        api_call.return_value = self._make_response(b"true")
        akismet = self._make_one()
        self.assertTrue(
            akismet.should_reject(
                {
                    "body": "buy viagra",
                    "application_url": "https://www.example.com/",
                    "ip_address": "127.0.0.1",
                    "user_agent": "cURL",
                    "referrer": "https://www.example.com/",
                }
            )
        )
        api_call.assert_called_with(
            "https://hogehoge.rest.akismet.com/1.1/comment-check",
            headers=unittest.mock.ANY,
            timeout=unittest.mock.ANY,
            data={
                "comment_content": "buy viagra",
                "blog": "https://www.example.com/",
                "user_ip": "127.0.0.1",
                "user_agent": "cURL",
                "referrer": "https://www.example.com/",
            },
        )

    @unittest.mock.patch("requests.post")
    def test_should_reject_false(self, api_call):
        api_call.return_value = self._make_response(b"false")
        akismet = self._make_one()
        self.assertFalse(
            akismet.should_reject(
                {
                    "body": "Hamhamham",
                    "application_url": "https://www.example.com/",
                    "ip_address": "127.0.0.1",
                    "user_agent": "cURL",
                    "referrer": "https://www.example.com/",
                }
            )
        )
        api_call.assert_called_with(
            "https://hogehoge.rest.akismet.com/1.1/comment-check",
            headers=unittest.mock.ANY,
            data=unittest.mock.ANY,
            timeout=unittest.mock.ANY,
        )

    @unittest.mock.patch("requests.post")
    def test_should_reject_timeout(self, api_call):
        import requests

        akismet = self._make_one()
        api_call.side_effect = requests.Timeout("connection timed out")
        self.assertFalse(
            akismet.should_reject(
                {
                    "body": "Hamhamham",
                    "application_url": "https://www.example.com/",
                    "ip_address": "127.0.0.1",
                    "user_agent": "cURL",
                    "referrer": "https://www.example.com/",
                }
            )
        )

    @unittest.mock.patch("requests.post")
    def test_should_reject_no_key(self, api_call):
        akismet = self._make_one(key=None)
        self.assertFalse(
            akismet.should_reject(
                {
                    "body": "Hamhamham",
                    "application_url": "https://www.example.com/",
                    "ip_address": "127.0.0.1",
                    "user_agent": "cURL",
                    "referrer": "https://www.example.com/",
                }
            )
        )
        assert not api_call.called

    def test_should_reject_no_payload(self):
        akismet = self._make_one()
        self.assertFalse(akismet.should_reject({}))


class TestDNSBL(unittest.TestCase):
    def _make_one(self, providers=("xbl.spamhaus.org",)):
        from ..filters.dnsbl import DNSBL

        return DNSBL(providers, {})

    def test_init(self):
        dnsbl = self._make_one(["xbl.spamhaus.org"])
        self.assertEqual(dnsbl.providers, ("xbl.spamhaus.org",))

    def test_init_no_providers(self):
        dnsbl = self._make_one([])
        self.assertEqual(dnsbl.providers, tuple())

    @unittest.mock.patch("socket.gethostbyname")
    def test_should_reject(self, lookup_call):
        lookup_call.return_value = "127.0.0.2"
        dnsbl = self._make_one()
        self.assertTrue(dnsbl.should_reject({"ip_address": "10.0.100.254"}))
        lookup_call.assert_called_with("254.100.0.10.xbl.spamhaus.org.")

    @unittest.mock.patch("socket.gethostbyname")
    def test_should_reject_ipv6(self, lookup_call):
        lookup_call.return_value = "127.0.0.2"
        dnsbl = self._make_one()
        self.assertTrue(dnsbl.should_reject({"ip_address": "fe80:c9cd::1"}))
        lookup_call.assert_called_with(
            "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0."
            + "d.c.9.c.0.8.e.f.xbl.spamhaus.org."
        )

    @unittest.mock.patch("socket.gethostbyname")
    def test_should_reject_false(self, lookup_call):
        import socket

        lookup_call.side_effect = socket.gaierror("foobar")
        dnsbl = self._make_one()
        self.assertFalse(dnsbl.should_reject({"ip_address": "10.0.100.1"}))
        lookup_call.assert_called_with("1.100.0.10.xbl.spamhaus.org.")

    @unittest.mock.patch("socket.gethostbyname")
    def test_should_reject_invalid(self, lookup_call):
        lookup_call.return_value = "192.168.1.1"
        dnsbl = self._make_one()
        self.assertFalse(dnsbl.should_reject({"ip_address": "10.0.100.2"}))

    @unittest.mock.patch("socket.gethostbyname")
    def test_should_reject_malformed(self, lookup_call):
        lookup_call.return_value = "foobarbaz"
        dnsbl = self._make_one()
        self.assertFalse(dnsbl.should_reject({"ip_address": "10.0.100.2"}))

    def test_should_reject_no_providers(self):
        dnsbl = self._make_one([])
        self.assertFalse(dnsbl.should_reject({"ip_address": "127.0.0.1"}))


class TestGetIPIntelProxyDetector(unittest.TestCase):
    def _make_one(self, settings):
        from ..filters.proxy import GetIPIntelProxyDetector

        return GetIPIntelProxyDetector(**settings)

    def _make_response(self, status_code, content):
        MockResponse = namedtuple("Response", ["status_code", "content"])
        return MockResponse(status_code, content)

    def test_init(self):
        getipintel = self._make_one(
            {"url": "http://www.example.com/", "email": "foo@example.com", "flags": "m"}
        )
        self.assertEqual(getipintel.url, "http://www.example.com/")
        self.assertEqual(getipintel.email, "foo@example.com")
        self.assertEqual(getipintel.flags, "m")

    def test_init_default(self):
        with self.assertRaises(ValueError):
            self._make_one({})

    def test_init_default_with_email(self):
        getipintel = self._make_one({"email": "foo@example.com"})
        self.assertEqual(getipintel.url, "http://check.getipintel.net/check.php")
        self.assertEqual(getipintel.email, "foo@example.com")
        self.assertEqual(getipintel.flags, None)

    @unittest.mock.patch("requests.get")
    def test_check(self, api_call):
        api_call.return_value = self._make_response(200, b"1")
        getipintel = self._make_one(
            {"url": "http://www.example.com/", "email": "foo@example.com", "flags": "m"}
        )
        self.assertEqual(getipintel.check("8.8.8.8"), b"1")
        api_call.assert_called_with(
            "http://www.example.com/",
            headers=unittest.mock.ANY,
            timeout=unittest.mock.ANY,
            params={"ip": "8.8.8.8", "contact": "foo@example.com", "flags": "m"},
        )

    @unittest.mock.patch("requests.get")
    def test_check_no_flags(self, api_call):
        api_call.return_value = self._make_response(200, b"1")
        getipintel = self._make_one(
            {"url": "http://www.example.com/", "email": "foo@example.com"}
        )
        self.assertEqual(getipintel.check("8.8.8.8"), b"1")
        api_call.assert_called_with(
            "http://www.example.com/",
            headers=unittest.mock.ANY,
            timeout=unittest.mock.ANY,
            params={"ip": "8.8.8.8", "contact": "foo@example.com"},
        )

    @unittest.mock.patch("requests.get")
    def test_check_timeout(self, api_call):
        import requests

        api_call.side_effect = requests.Timeout("connection timed out")
        getipintel = self._make_one({"email": "foo@example.com"})
        self.assertIsNone(getipintel.check("8.8.8.8"))

    @unittest.mock.patch("requests.get")
    def test_check_status_error(self, api_call):
        api_call.return_value = self._make_response(500, b"1")
        getipintel = self._make_one({"email": "foo@example.com"})
        self.assertIsNone(getipintel.check("8.8.8.8"))

    @unittest.mock.patch("requests.get")
    def test_check_response_error(self, api_call):
        api_call.return_value = self._make_response(200, b"-1")
        getipintel = self._make_one({"email": "foo@example.com"})
        self.assertIsNone(getipintel.check("8.8.8.8"))

    def test_evaluate(self):
        getipintel = self._make_one({"email": "foo@example.com", "threshold": "0.8"})
        self.assertEqual(getipintel.evaluate(b"0.8001"), True)

    def test_evaluate_default(self):
        getipintel = self._make_one({"email": "foo@example.com"})
        self.assertEqual(getipintel.evaluate(b"0.9901"), True)

    def test_evaluate_negative(self):
        getipintel = self._make_one({"email": "foo@example.com", "threshold": "0.8"})
        self.assertEqual(getipintel.evaluate(b"0.79"), False)
        self.assertEqual(getipintel.evaluate(b"0.799"), False)
        self.assertEqual(getipintel.evaluate(b"0"), False)

    def test_evaluate_unknown(self):
        getipintel = self._make_one({"email": "foo@example.com", "threshold": "0.8"})
        self.assertEqual(getipintel.evaluate(b"-1"), False)

    def test_evaluate_threshold_invalid(self):
        getipintel = self._make_one({"email": "foo@example.com", "threshold": "foo"})
        self.assertEqual(getipintel.evaluate(b"0.9901"), True)
        self.assertEqual(getipintel.evaluate(b"0.99"), False)

    def test_evaluate_threshold_nan(self):
        getipintel = self._make_one({"email": "foo@example.com", "threshold": "nan"})
        self.assertEqual(getipintel.evaluate(b"0.9901"), True)
        self.assertEqual(getipintel.evaluate(b"0.99"), False)


class TestBlackBoxProxyDetector(unittest.TestCase):
    def _make_one(self, settings):
        from ..filters.proxy import BlackBoxProxyDetector

        return BlackBoxProxyDetector(**settings)

    def _make_response(self, status_code, content):
        MockResponse = namedtuple("Response", ["status_code", "content"])
        return MockResponse(status_code, content)

    def test_init(self):
        blackbox = self._make_one({"url": "http://www.example.com/"})
        self.assertEqual(blackbox.url, "http://www.example.com/")

    def test_init_default(self):
        blackbox = self._make_one({})
        self.assertEqual(
            blackbox.url, "http://proxy.mind-media.com/block/proxycheck.php"
        )

    @unittest.mock.patch("requests.get")
    def test_check(self, api_call):
        api_call.return_value = self._make_response(200, b"Y")
        blackbox = self._make_one({"url": "http://www.example.com/"})
        self.assertEqual(blackbox.check("8.8.8.8"), b"Y")
        api_call.assert_called_with(
            "http://www.example.com/",
            headers=unittest.mock.ANY,
            timeout=unittest.mock.ANY,
            params={"ip": "8.8.8.8"},
        )

    @unittest.mock.patch("requests.get")
    def test_check_timeout(self, api_call):
        import requests

        api_call.side_effect = requests.Timeout("connection timed out")
        blackbox = self._make_one({})
        self.assertIsNone(blackbox.check("8.8.8.8"))

    @unittest.mock.patch("requests.get")
    def test_check_status_error(self, api_call):
        api_call.return_value = self._make_response(500, b"Error")
        blackbox = self._make_one({})
        self.assertIsNone(blackbox.check("8.8.8.8"))

    @unittest.mock.patch("requests.get")
    def test_check_response_error(self, api_call):
        api_call.return_value = self._make_response(200, b"X")
        blackbox = self._make_one({})
        self.assertIsNone(blackbox.check("8.8.8.8"))

    def test_evaluate(self):
        blackbox = self._make_one({})
        self.assertEqual(blackbox.evaluate(b"Y"), True)

    def test_evaluate_negative(self):
        blackbox = self._make_one({})
        self.assertEqual(blackbox.evaluate(b"N"), False)

    def test_evaluate_unknown(self):
        blackbox = self._make_one({})
        self.assertEqual(blackbox.evaluate(b"Z"), False)


class TestProxyDetector(unittest.TestCase):
    def _get_target_class(self):
        from ..filters.proxy import ProxyDetector

        return ProxyDetector

    def _make_one(self, settings, cache_svc):
        return self._get_target_class()(settings, {"cache": cache_svc})

    def _make_config(self):
        return {
            "blackbox": {"enabled": True, "url": "http://www.example.com/blackbox"},
            "getipintel": {
                "enabled": True,
                "url": "http://www.example.com/getipintel",
                "email": "foo@example.com",
                "flags": "m",
            },
        }

    def test_init(self):
        from . import make_cache_region

        settings = self._make_config()
        cache_svc = make_cache_region({})
        proxy_detector = self._make_one(settings, cache_svc)
        self.assertEqual(proxy_detector.settings, settings)
        self.assertEqual(proxy_detector.cache_region, cache_svc)

    def test_init_no_value(self):
        from . import make_cache_region

        cache_svc = make_cache_region({})
        proxy_detector = self._make_one(None, cache_svc)
        self.assertEqual(proxy_detector.settings, {})

    def test_init_no_service(self):
        settings = self._make_config()
        with self.assertRaises(RuntimeError):
            self._get_target_class()(settings, None)

    @unittest.mock.patch("fanboi2.filters.proxy.BlackBoxProxyDetector.check")
    @unittest.mock.patch("fanboi2.filters.proxy.GetIPIntelProxyDetector.check")
    def test_check(self, getipintel_check, blackbox_check):
        from . import make_cache_region

        settings = self._make_config()
        cache_svc = make_cache_region({})
        blackbox_check.return_value = b"N"
        getipintel_check.return_value = b"1"
        proxy_detector = self._make_one(settings, cache_svc)
        self.assertTrue(proxy_detector.should_reject({"ip_address": "8.8.8.8"}))
        blackbox_check.assert_called_with("8.8.8.8")
        getipintel_check.assert_called_with("8.8.8.8")

    @unittest.mock.patch("fanboi2.filters.proxy.BlackBoxProxyDetector.check")
    @unittest.mock.patch("fanboi2.filters.proxy.GetIPIntelProxyDetector.check")
    def test_check_cached(self, getipintel_check, blackbox_check):
        from . import make_cache_region

        settings = self._make_config()
        cache_svc = make_cache_region({})
        blackbox_check.return_value = b"N"
        getipintel_check.return_value = b"0"
        proxy_detector = self._make_one(settings, cache_svc)
        self.assertFalse(proxy_detector.should_reject({"ip_address": "8.8.8.8"}))
        self.assertFalse(proxy_detector.should_reject({"ip_address": "8.8.8.8"}))
        blackbox_check.assert_called_once_with("8.8.8.8")
        getipintel_check.assert_called_once_with("8.8.8.8")

    @unittest.mock.patch("fanboi2.filters.proxy.BlackBoxProxyDetector.check")
    @unittest.mock.patch("fanboi2.filters.proxy.GetIPIntelProxyDetector.check")
    def test_check_first_matched(self, getipintel_check, blackbox_check):
        from . import make_cache_region

        settings = self._make_config()
        cache_svc = make_cache_region({})
        blackbox_check.return_value = b"Y"
        getipintel_check.side_effective = AssertionError("should not called")
        proxy_detector = self._make_one(settings, cache_svc)
        self.assertTrue(proxy_detector.should_reject({"ip_address": "8.8.8.8"}))
        blackbox_check.assert_called_with("8.8.8.8")
        self.assertFalse(getipintel_check.called)

    @unittest.mock.patch("fanboi2.filters.proxy.BlackBoxProxyDetector.check")
    @unittest.mock.patch("fanboi2.filters.proxy.GetIPIntelProxyDetector.check")
    def test_check_no_matched(self, getipintel_check, blackbox_check):
        from . import make_cache_region

        settings = self._make_config()
        cache_svc = make_cache_region({})
        blackbox_check.return_value = b"F"
        getipintel_check.return_value = b"0"
        proxy_detector = self._make_one(settings, cache_svc)
        self.assertFalse(proxy_detector.should_reject({"ip_address": "8.8.8.8"}))
        blackbox_check.assert_called_with("8.8.8.8")
        getipintel_check.assert_called_with("8.8.8.8")

    @unittest.mock.patch("fanboi2.filters.proxy.BlackBoxProxyDetector.check")
    @unittest.mock.patch("fanboi2.filters.proxy.GetIPIntelProxyDetector.check")
    def test_check_error_skip(self, getipintel_check, blackbox_check):
        from . import make_cache_region

        settings = self._make_config()
        cache_svc = make_cache_region({})
        blackbox_check.return_value = None
        getipintel_check.return_value = None
        proxy_detector = self._make_one(settings, cache_svc)
        self.assertFalse(proxy_detector.should_reject({"ip_address": "8.8.8.8"}))
        self.assertFalse(proxy_detector.should_reject({"ip_address": "8.8.8.8"}))
        self.assertEqual(blackbox_check.call_count, 2)
        self.assertEqual(getipintel_check.call_count, 2)
        blackbox_check.assert_called_with("8.8.8.8")
        getipintel_check.assert_called_with("8.8.8.8")
