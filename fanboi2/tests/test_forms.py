import unittest
from pyramid import testing


class _FormMixin(object):

    def setUp(self):
        super(_FormMixin, self).setUp()
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry

    def tearDown(self):
        super(_FormMixin, self).tearDown()
        testing.tearDown()

    def _get_target_class(self):  # pragma: no cover
        raise NotImplementedError

    def _make_one(self, form):
        form = self._get_target_class()(
            self._make_form(form),
            request=self.request)
        form.validate()
        return form

    def _make_form(self, data):
        from webob.multidict import MultiDict
        return MultiDict(data)


class _DummyTranslations(object):

    def gettext(self, string):
        return string

    def ngettext(self, singular, plural, n):
        if n == 1:
            return singular
        return plural


class _DummyForm(dict):
    pass


class _DummyField(object):
    _translations = _DummyTranslations()

    def __init__(self, data, errors=(), raw_data=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data

    def gettext(self, string):
        return self._translations.gettext(string)

    def ngettext(self, singular, plural, n):
        return self._translations.ngettext(singular, plural, n)


class TestFormValidators(unittest.TestCase):

    def _grab_error(self, callable, form, field):
        from ..forms import ValidationError
        try:
            callable(form, field)
        except ValidationError as e:
            return e.args[0]

    def test_length_validator(self):
        from ..forms import Length, ValidationError
        form = _DummyForm()
        field = _DummyField('foobar')
        self.assertEqual(Length(min=2, max=6)(form, field), None)
        self.assertEqual(Length(min=6)(form, field), None)
        self.assertEqual(Length(max=6)(form, field), None)
        self.assertRaises(ValidationError, Length(min=7), form, field)
        self.assertRaises(ValidationError, Length(max=5), form, field)
        self.assertRaises(ValidationError, Length(7, 10), form, field)
        self.assertRaises(AssertionError, Length)
        self.assertRaises(AssertionError, Length, min=5, max=2)

        def grab(**k):
            return self._grab_error(Length(**k), form, field)
        self.assertIn('at least 8 characters', grab(min=8))
        self.assertIn('longer than 1 character', grab(max=1))
        self.assertIn('longer than 5 characters', grab(max=5))
        self.assertIn('between 2 and 5 characters', grab(min=2, max=5))
        self.assertIn(
            'at least 1 character',
            self._grab_error(Length(min=1), form, _DummyField('')))

    def test_length_validator_newline(self):
        from ..forms import Length
        form = _DummyForm()
        self.assertEqual(Length(max=1)(form, _DummyField('\r\n')), None)
        self.assertEqual(Length(max=1)(form, _DummyField('\n')), None)
        self.assertEqual(Length(max=1)(form, _DummyField('\r')), None)


class TestTopicForm(_FormMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..forms import TopicForm
        return TopicForm

    def test_validated(self):
        form = self._make_one({'title': 'Words', 'body': 'Words words'})
        self.assertTrue(form.validate())

    def test_title_missing(self):
        form = self._make_one({})
        self.assertFalse(form.validate())
        self.assertListEqual(form.title.errors, ['This field is required.'])

    def test_title_length_shorter(self):
        form = self._make_one({'title': 'F'*4})
        self.assertFalse(form.validate())
        self.assertListEqual(form.title.errors, [
            'Field must be between 5 and 200 characters long.'])

    def test_title_length_longer(self):
        form = self._make_one({'title': 'F'*201})
        self.assertFalse(form.validate())
        self.assertListEqual(form.title.errors, [
            'Field must be between 5 and 200 characters long.'])

    def test_body_missing(self):
        form = self._make_one({})
        self.assertFalse(form.validate())
        self.assertListEqual(form.body.errors, ['This field is required.'])

    def test_body_length_shorter(self):
        form = self._make_one({'body': 'F'*4})
        self.assertFalse(form.validate())
        self.assertListEqual(form.body.errors, [
            'Field must be between 5 and 4000 characters long.'])

    def test_body_length_longer(self):
        form = self._make_one({'body': 'F'*4001})
        self.assertFalse(form.validate())
        self.assertListEqual(form.body.errors, [
            'Field must be between 5 and 4000 characters long.'])


class TestPostForm(_FormMixin, unittest.TestCase):

    def _get_target_class(self):
        from ..forms import PostForm
        return PostForm

    def test_validated(self):
        form = self._make_one({'body': 'Words words'})
        self.assertTrue(form.validate())

    def test_body_missing(self):
        form = self._make_one({})
        self.assertFalse(form.validate())
        self.assertListEqual(form.body.errors, ['This field is required.'])

    def test_body_length_shorter(self):
        form = self._make_one({'body': 'F'*4})
        self.assertFalse(form.validate())
        self.assertListEqual(form.body.errors, [
            'Field must be between 5 and 4000 characters long.'])

    def test_body_length_longer(self):
        form = self._make_one({'body': 'F'*4001})
        self.assertFalse(form.validate())
        self.assertListEqual(form.body.errors, [
            'Field must be between 5 and 4000 characters long.'])
