import unittest
from fanboi2.tests import RegistryMixin


class TestSerializeError(RegistryMixin, unittest.TestCase):

    def test_base_error(self):
        from fanboi2.errors import BaseError, serialize_error
        error = serialize_error('base', 10)
        request = self._makeRequest()
        self.assertIsInstance(error, BaseError)
        self.assertIsNotNone(error.message(request))
        self.assertEqual(error.name, 'unknown')
        self.assertEqual(error.http_status, '500 Internal Server Error')

    def test_rate_limited(self):
        from fanboi2.errors import serialize_error, RateLimitedError
        error = serialize_error('rate_limited', 10)
        request = self._makeRequest()
        self.assertIsInstance(error, RateLimitedError)
        self.assertEqual(error.timeleft, 10)
        self.assertIsNotNone(error.message(request))
        self.assertEqual(error.name, 'rate_limited')
        self.assertEqual(error.http_status, '429 Too Many Requests')

    def test_params_invalid(self):
        from fanboi2.errors import serialize_error, ParamsInvalidError
        error = serialize_error('params_invalid', {})
        request = self._makeRequest()
        self.assertIsInstance(error, ParamsInvalidError)
        self.assertEqual(error.messages, {})
        self.assertIsNotNone(error.message(request))
        self.assertEqual(error.name, 'params_invalid')
        self.assertEqual(error.http_status, '400 Bad Request')

    def test_spam_rejected(self):
        from fanboi2.errors import serialize_error, SpamRejectedError
        error = serialize_error('spam_rejected')
        request = self._makeRequest()
        self.assertIsInstance(error, SpamRejectedError)
        self.assertIsNotNone(error.message(request))
        self.assertEqual(error.name, 'spam_rejected')
        self.assertEqual(error.http_status, '422 Unprocessable Entity')

    def test_dnsbl_rejected(self):
        from fanboi2.errors import serialize_error, DnsblRejectedError
        error = serialize_error('dnsbl_rejected')
        request = self._makeRequest()
        self.assertIsInstance(error, DnsblRejectedError)
        self.assertIsNotNone(error.message(request))
        self.assertEqual(error.name, 'dnsbl_rejected')
        self.assertEqual(error.http_status, '422 Unprocessable Entity')

    def test_ban_rejected(self):
        from fanboi2.errors import serialize_error, BanRejectedError
        error = serialize_error('ban_rejected')
        request = self._makeRequest()
        self.assertIsInstance(error, BanRejectedError)
        self.assertIsNotNone(error.message(request))
        self.assertEqual(error.name, 'ban_rejected')
        self.assertEqual(error.http_status, '422 Unprocessable Entity')

    def test_status_rejected(self):
        from fanboi2.errors import serialize_error, StatusRejectedError
        error = serialize_error('status_rejected', 'locked')
        request = self._makeRequest()
        self.assertIsInstance(error, StatusRejectedError)
        self.assertEqual(error.status, 'locked')
        self.assertIsNotNone(error.message(request))
        self.assertEqual(error.name, 'status_rejected')
        self.assertEqual(error.http_status, '422 Unprocessable Entity')

    def test_proxy_rejected(self):
        from fanboi2.errors import serialize_error, ProxyRejectedError
        error = serialize_error('proxy_rejected')
        request = self._makeRequest()
        self.assertIsInstance(error, ProxyRejectedError)
        self.assertIsNotNone(error.message(request))
        self.assertEqual(error.name, 'proxy_rejected')
        self.assertEqual(error.http_status, '422 Unprocessable Entity')
