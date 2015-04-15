import unittest


class TestSerializeError(unittest.TestCase):

    def test_rate_limited(self):
        from fanboi2.errors import serialize_error, RateLimitedError
        error = serialize_error('rate_limited', 10)
        self.assertIsInstance(error, RateLimitedError)
        self.assertEqual(error.timeleft, 10)

    def test_form_invalid(self):
        from fanboi2.errors import serialize_error, FormInvalidError
        error = serialize_error('form_invalid', {})
        self.assertIsInstance(error, FormInvalidError)
        self.assertEqual(error.messages, {})

    def test_spam_blocked(self):
        from fanboi2.errors import serialize_error, SpamBlockedError
        error = serialize_error('spam_blocked')
        self.assertIsInstance(error, SpamBlockedError)

    def test_dnsbl_blocked(self):
        from fanboi2.errors import serialize_error, DnsblBlockedError
        error = serialize_error('dnsbl_blocked')
        self.assertIsInstance(error, DnsblBlockedError)

    def test_status_blocked(self):
        from fanboi2.errors import serialize_error, StatusBlockedError
        error = serialize_error('status_blocked', 'locked')
        self.assertIsInstance(error, StatusBlockedError)
        self.assertEqual(error.status, 'locked')
