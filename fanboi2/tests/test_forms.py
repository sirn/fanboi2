import unittest
from pyramid import testing


class TestSecureForm(unittest.TestCase):

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.registry.settings = {'app.secret': 'TESTME'}
        return request

    def _makeForm(self, data):
        from webob.multidict import MultiDict
        return MultiDict(data)

    def _makeOne(self, form, request):
        from fanboi2.forms import SecureForm
        form = SecureForm(self._makeForm(form), request=request)
        form.validate()
        return form

    def test_csrf_token(self):
        import hmac
        import os
        from hashlib import sha1
        request = self._makeRequest()
        request.session['csrf'] = sha1(os.urandom(64)).hexdigest()
        token = hmac.new(
            bytes(request.registry.settings['app.secret'].encode('utf8')),
            bytes(request.session['csrf'].encode('utf8')),
            digestmod=sha1,
        ).hexdigest()
        form = self._makeOne({'csrf_token': token}, request)
        self.assertTrue(form.validate())
        self.assertEqual(form.errors, {})

    def test_csrf_token_empty(self):
        request = self._makeRequest()
        form = self._makeOne({}, request)
        self.assertDictEqual(form.errors, {
            'csrf_token': ['CSRF token missing.'],
        })

    def test_csrf_token_invalid(self):
        request = self._makeRequest()
        form = self._makeOne({'csrf_token': 'invalid'}, request)
        self.assertDictEqual(form.errors, {
            'csrf_token': ['CSRF token mismatched.'],
        })

    def test_data(self):
        request = self._makeRequest()
        form = self._makeOne({'csrf_token': 'strip_me'}, request)
        self.assertDictEqual(form.data, {})


class DummyTranslations(object):

    def gettext(self, string):
        return string

    def ngettext(self, singular, plural, n):
        if n == 1:
            return singular
        return plural


class DummyForm(dict):
    pass


class DummyField(object):
    _translations = DummyTranslations()

    def __init__(self, data, errors=(), raw_data=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data

    def gettext(self, string):
        return self._translations.gettext(string)

    def ngettext(self, singular, plural, n):
        return self._translations.ngettext(singular, plural, n)


class TestForm(unittest.TestCase):

    def _grab_error(self, callable, form, field):
        from fanboi2.forms import ValidationError
        try:
            callable(form, field)
        except ValidationError as e:
            return e.args[0]

    def test_length_validator(self):
        from fanboi2.forms import Length, ValidationError
        form = DummyForm()
        field = DummyField('foobar')

        self.assertEqual(Length(min=2, max=6)(form, field), None)
        self.assertEqual(Length(min=6)(form, field), None)
        self.assertEqual(Length(max=6)(form, field), None)
        self.assertRaises(ValidationError, Length(min=7), form, field)
        self.assertRaises(ValidationError, Length(max=5), form, field)
        self.assertRaises(ValidationError, Length(7, 10), form, field)
        self.assertRaises(AssertionError, Length)
        self.assertRaises(AssertionError, Length, min=5, max=2)

        grab = lambda **k: self._grab_error(Length(**k), form, field)
        self.assertIn('at least 8 characters', grab(min=8))
        self.assertIn('longer than 1 character', grab(max=1))
        self.assertIn('longer than 5 characters', grab(max=5))
        self.assertIn('between 2 and 5 characters', grab(min=2, max=5))
        self.assertIn(
            'at least 1 character',
            self._grab_error(Length(min=1), form, DummyField('')))

    def test_length_validator_newline(self):
        from fanboi2.forms import Length
        form = DummyForm()
        self.assertEqual(Length(max=1)(form, DummyField('\r\n')), None)
        self.assertEqual(Length(max=1)(form, DummyField('\n')), None)
        self.assertEqual(Length(max=1)(form, DummyField('\r')), None)
