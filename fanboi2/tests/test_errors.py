import unittest

from pyramid import testing


class TestDeserializeError(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry

    def tearDown(self):
        testing.tearDown()

    def test_base_error(self):
        from ..errors import BaseError, deserialize_error

        error_cls = deserialize_error("base")
        error = error_cls()
        self.assertIsInstance(error, BaseError)
        self.assertIsNotNone(error.message(self.request))
        self.assertEqual(error.name, "unknown")
        self.assertEqual(error.http_status, "500 Internal Server Error")

    def test_rate_limited(self):
        from ..errors import deserialize_error, RateLimitedError

        error_cls = deserialize_error("rate_limited")
        error = error_cls(10)
        self.assertIsInstance(error, RateLimitedError)
        self.assertEqual(error.timeleft, 10)
        self.assertIsNotNone(error.message(self.request))
        self.assertEqual(error.name, "rate_limited")
        self.assertEqual(error.http_status, "429 Too Many Requests")

    def test_params_invalid(self):
        from ..errors import deserialize_error, ParamsInvalidError

        error_cls = deserialize_error("params_invalid")
        error = error_cls({})
        self.assertIsInstance(error, ParamsInvalidError)
        self.assertEqual(error.messages, {})
        self.assertIsNotNone(error.message(self.request))
        self.assertEqual(error.name, "params_invalid")
        self.assertEqual(error.http_status, "400 Bad Request")

    def test_akismet_rejected(self):
        from ..errors import deserialize_error, AkismetRejectedError

        error_cls = deserialize_error("akismet_rejected")
        error = error_cls()
        self.assertIsInstance(error, AkismetRejectedError)
        self.assertIsNotNone(error.message(self.request))
        self.assertEqual(error.name, "akismet_rejected")
        self.assertEqual(error.http_status, "422 Unprocessable Entity")

    def test_dnsbl_rejected(self):
        from ..errors import deserialize_error, DNSBLRejectedError

        error_cls = deserialize_error("dnsbl_rejected")
        error = error_cls()
        self.assertIsInstance(error, DNSBLRejectedError)
        self.assertIsNotNone(error.message(self.request))
        self.assertEqual(error.name, "dnsbl_rejected")
        self.assertEqual(error.http_status, "422 Unprocessable Entity")

    def test_ban_rejected(self):
        from ..errors import deserialize_error, BanRejectedError

        error_cls = deserialize_error("ban_rejected")
        error = error_cls()
        self.assertIsInstance(error, BanRejectedError)
        self.assertIsNotNone(error.message(self.request))
        self.assertEqual(error.name, "ban_rejected")
        self.assertEqual(error.http_status, "422 Unprocessable Entity")

    def test_banword_rejected(self):
        from ..errors import deserialize_error, BanwordRejectedError

        error_cls = deserialize_error("banword_rejected")
        error = error_cls()
        self.assertIsInstance(error, BanwordRejectedError)
        self.assertIsNotNone(error.message(self.request))
        self.assertEqual(error.name, "banword_rejected")
        self.assertEqual(error.http_status, "422 Unprocessable Entity")

    def test_status_rejected(self):
        from ..errors import deserialize_error, StatusRejectedError

        error_cls = deserialize_error("status_rejected")
        error = error_cls("locked")
        self.assertIsInstance(error, StatusRejectedError)
        self.assertEqual(error.status, "locked")
        self.assertIsNotNone(error.message(self.request))
        self.assertEqual(error.name, "status_rejected")
        self.assertEqual(error.http_status, "422 Unprocessable Entity")

    def test_proxy_rejected(self):
        from ..errors import deserialize_error, ProxyRejectedError

        error_cls = deserialize_error("proxy_rejected")
        error = error_cls()
        self.assertIsInstance(error, ProxyRejectedError)
        self.assertIsNotNone(error.message(self.request))
        self.assertEqual(error.name, "proxy_rejected")
        self.assertEqual(error.http_status, "422 Unprocessable Entity")
