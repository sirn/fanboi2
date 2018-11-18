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
        form = self._get_target_class()(self._make_form(form), request=self.request)
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
        field = _DummyField("foobar")
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

        self.assertIn("at least 8 characters", grab(min=8))
        self.assertIn("longer than 1 character", grab(max=1))
        self.assertIn("longer than 5 characters", grab(max=5))
        self.assertIn("between 2 and 5 characters", grab(min=2, max=5))
        self.assertIn(
            "at least 1 character",
            self._grab_error(Length(min=1), form, _DummyField("")),
        )

    def test_length_validator_newline(self):
        from ..forms import Length

        form = _DummyForm()
        self.assertEqual(Length(max=1)(form, _DummyField("\r\n")), None)
        self.assertEqual(Length(max=1)(form, _DummyField("\n")), None)
        self.assertEqual(Length(max=1)(form, _DummyField("\r")), None)


class TestTopicForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import TopicForm

        return TopicForm

    def test_validated(self):
        form = self._make_one({"title": "Words", "body": "Words words"})
        self.assertTrue(form.validate())

    def test_title_missing(self):
        form = self._make_one({})
        self.assertFalse(form.validate())
        self.assertListEqual(form.title.errors, ["This field is required."])

    def test_title_length_shorter(self):
        form = self._make_one({"title": "F" * 4})
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.title.errors, ["Field must be between 5 and 200 characters long."]
        )

    def test_title_length_longer(self):
        form = self._make_one({"title": "F" * 201})
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.title.errors, ["Field must be between 5 and 200 characters long."]
        )

    def test_body_missing(self):
        form = self._make_one({})
        self.assertFalse(form.validate())
        self.assertListEqual(form.body.errors, ["This field is required."])

    def test_body_length_shorter(self):
        form = self._make_one({"body": "F" * 4})
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.body.errors, ["Field must be between 5 and 4000 characters long."]
        )

    def test_body_length_longer(self):
        form = self._make_one({"body": "F" * 4001})
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.body.errors, ["Field must be between 5 and 4000 characters long."]
        )


class TestPostForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import PostForm

        return PostForm

    def test_validated(self):
        form = self._make_one({"body": "Words words"})
        self.assertTrue(form.validate())

    def test_body_missing(self):
        form = self._make_one({})
        self.assertFalse(form.validate())
        self.assertListEqual(form.body.errors, ["This field is required."])

    def test_body_length_shorter(self):
        form = self._make_one({"body": "F" * 4})
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.body.errors, ["Field must be between 5 and 4000 characters long."]
        )

    def test_body_length_longer(self):
        form = self._make_one({"body": "F" * 4001})
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.body.errors, ["Field must be between 5 and 4000 characters long."]
        )


class TestAdminLoginForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import AdminLoginForm

        return AdminLoginForm

    def test_validated(self):
        form = self._make_one({"username": "foo", "password": "bar"})
        self.assertTrue(form.validate())

    def test_username_missing(self):
        form = self._make_one({"password": "bar"})
        self.assertFalse(form.validate())
        self.assertListEqual(form.username.errors, ["This field is required."])

    def test_password_missing(self):
        form = self._make_one({"username": "foo"})
        self.assertFalse(form.validate())
        self.assertListEqual(form.password.errors, ["This field is required."])


class TestAdminSetupForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import AdminSetupForm

        return AdminSetupForm

    def test_validated(self):
        form = self._make_one(
            {
                "username": "foo",
                "password": "passw0rd",
                "password_confirm": "passw0rd",
                "name": "Foobar",
            }
        )
        self.assertTrue(form.validate())

    def test_username_missing(self):
        form = self._make_one(
            {"password": "passw0rd", "password_confirm": "passw0rd", "name": "Foobar"}
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.username.errors, ["This field is required."])

    def test_username_length_shorter(self):
        form = self._make_one(
            {
                "username": "f",
                "password": "passw0rd",
                "password_confirm": "passw0rd",
                "name": "Foo",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.username.errors, ["Field must be between 2 and 32 characters long."]
        )

    def test_username_length_longer(self):
        form = self._make_one(
            {
                "username": "f" * 33,
                "password": "passw0rd",
                "password_confirm": "passw0rd",
                "name": "Foo",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.username.errors, ["Field must be between 2 and 32 characters long."]
        )

    def test_password_missing(self):
        form = self._make_one(
            {"username": "foo", "password_confirm": "passw0rd", "name": "Foobar"}
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.password.errors, ["This field is required."])

    def test_password_length_shorter(self):
        form = self._make_one(
            {
                "username": "foo",
                "password": "passw0r",
                "password_confirm": "passw0r",
                "name": "Foobar",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.password.errors, ["Field must be between 8 and 64 characters long."]
        )

    def test_password_length_longer(self):
        form = self._make_one(
            {
                "username": "foo",
                "password": "p" * 65,
                "password_confirm": "p" * 65,
                "name": "Foobar",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.password.errors, ["Field must be between 8 and 64 characters long."]
        )

    def test_password_confirm_missing(self):
        form = self._make_one(
            {"username": "foo", "password": "passw0rd", "name": "Foobar"}
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.password_confirm.errors, ["This field is required."])

    def test_password_confirm_mismatched(self):
        form = self._make_one(
            {
                "username": "foo",
                "password": "passw0rd",
                "password_confirm": "password",
                "name": "Foobar",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.password_confirm.errors, ["Password must match."])

    def test_name_missing(self):
        form = self._make_one(
            {"username": "foo", "password": "passw0rd", "password_confirm": "passw0rd"}
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.name.errors, ["This field is required."])

    def test_name_shorter(self):
        form = self._make_one(
            {
                "username": "foo",
                "password": "passw0rd",
                "password_confirm": "passw0rd",
                "name": "f",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.name.errors, ["Field must be between 2 and 64 characters long."]
        )

    def test_name_longer(self):
        form = self._make_one(
            {
                "username": "foo",
                "password": "passw0rd",
                "password_confirm": "passw0rd",
                "name": "f" * 65,
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(
            form.name.errors, ["Field must be between 2 and 64 characters long."]
        )


class TestAdminSettingForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import AdminSettingForm

        return AdminSettingForm

    def test_validated(self):
        form = self._make_one({"value": '"foo"'})
        self.assertTrue(form.validate())

    def test_value_missing(self):
        form = self._make_one({})
        self.assertFalse(form.validate())
        self.assertListEqual(form.value.errors, ["This field is required."])

    def test_value_invalid_json(self):
        form = self._make_one({"value": "invalid"})
        self.assertFalse(form.validate())
        self.assertListEqual(form.value.errors, ["Must be a valid JSON."])


class TestAdminBanForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import AdminBanForm

        return AdminBanForm

    def test_validated(self):
        form = self._make_one({"ip_address": "10.0.0.0/24"})
        self.assertTrue(form.validate())

    def test_ip_address_missing(self):
        form = self._make_one({})
        self.assertFalse(form.validate())
        self.assertListEqual(form.ip_address.errors, ["This field is required."])

    def test_ip_address_invalid(self):
        form = self._make_one({"ip_address": "foobar"})
        self.assertFalse(form.validate())
        self.assertListEqual(form.ip_address.errors, ["Must be a valid IP address."])


class TestAdminBanwordForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import AdminBanwordForm

        return AdminBanwordForm

    def test_validated(self):
        form = self._make_one({"expr": "https:\\/\\/bit\\.ly"})
        self.assertTrue(form.validate())

    def test_expr_missing(self):
        form = self._make_one({})
        self.assertFalse(form.validate())
        self.assertListEqual(form.expr.errors, ["This field is required."])

    def test_expr_invalid(self):
        form = self._make_one({"expr": "(?y)"})
        self.assertFalse(form.validate())
        self.assertListEqual(form.expr.errors, ["Must be a valid regular expression."])


class TestAdminBoardForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import AdminBoardForm

        return AdminBoardForm

    def test_validated(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "description": "New board",
                "status": "open",
                "agreements": "None!",
                "settings": "{}",
            }
        )
        self.assertTrue(form.validate())

    def test_title_missing(self):
        form = self._make_one(
            {
                "description": "New board",
                "status": "open",
                "agreements": "None!",
                "settings": "{}",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.title.errors, ["This field is required."])

    def test_description_missing(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "status": "open",
                "agreements": "None!",
                "settings": "{}",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.description.errors, ["This field is required."])

    def test_status_missing(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "description": "New board",
                "agreements": "None!",
                "settings": "{}",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.status.errors, ["Not a valid choice"])

    def test_status_not_allowed(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "status": "foobar",
                "description": "New board",
                "agreements": "None!",
                "settings": "{}",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.status.errors, ["Not a valid choice"])

    def test_agreements_missing(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "description": "New board",
                "status": "open",
                "settings": "{}",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.agreements.errors, ["This field is required."])

    def test_settings_missing(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "description": "New board",
                "status": "open",
                "agreements": "None!",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.settings.errors, ["This field is required."])

    def test_settings_invalid_json(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "description": "New board",
                "status": "open",
                "agreements": "None!",
                "settings": "foobar",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.settings.errors, ["Must be a valid JSON."])


class TestAdminBoardNewForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import AdminBoardNewForm

        return AdminBoardNewForm

    def test_validated(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "slug": "foobar",
                "description": "New board",
                "status": "open",
                "agreements": "None!",
                "settings": "{}",
            }
        )
        self.assertTrue(form.validate())

    def test_title_missing(self):
        form = self._make_one(
            {
                "slug": "foobar",
                "description": "New board",
                "status": "open",
                "agreements": "None!",
                "settings": "{}",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.title.errors, ["This field is required."])

    def test_slug_missing(self):
        form = self._make_one(
            {
                "description": "New board",
                "status": "open",
                "agreements": "None!",
                "settings": "{}",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.slug.errors, ["This field is required."])

    def test_description_missing(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "slug": "foobar",
                "status": "open",
                "agreements": "None!",
                "settings": "{}",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.description.errors, ["This field is required."])

    def test_status_missing(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "slug": "foobar",
                "description": "New board",
                "agreements": "None!",
                "settings": "{}",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.status.errors, ["Not a valid choice"])

    def test_status_not_allowed(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "slug": "foobar",
                "status": "foobar",
                "description": "New board",
                "agreements": "None!",
                "settings": "{}",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.status.errors, ["Not a valid choice"])

    def test_agreements_missing(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "slug": "foobar",
                "description": "New board",
                "status": "open",
                "settings": "{}",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.agreements.errors, ["This field is required."])

    def test_settings_missing(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "slug": "foobar",
                "description": "New board",
                "status": "open",
                "agreements": "None!",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.settings.errors, ["This field is required."])

    def test_settings_invalid_json(self):
        form = self._make_one(
            {
                "title": "Foobar",
                "slug": "foobar",
                "description": "New board",
                "status": "open",
                "agreements": "None!",
                "settings": "foobar",
            }
        )
        self.assertFalse(form.validate())
        self.assertListEqual(form.settings.errors, ["Must be a valid JSON."])


class TestAdminPageForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import AdminPageForm

        return AdminPageForm

    def test_validated(self):
        form = self._make_one({"body": "Foobar"})
        self.assertTrue(form.validate())

    def test_body_missing(self):
        form = self._make_one({})
        self.assertFalse(form.validate())
        self.assertListEqual(form.body.errors, ["This field is required."])


class TestAdminPublicPageForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import AdminPublicPageForm

        return AdminPublicPageForm

    def test_validated(self):
        form = self._make_one({"body": "Foobar", "title": "Foobar"})
        self.assertTrue(form.validate())

    def test_body_missing(self):
        form = self._make_one({"title": "Foobar"})
        self.assertFalse(form.validate())
        self.assertListEqual(form.body.errors, ["This field is required."])

    def test_title_missing(self):
        form = self._make_one({"body": "Foobar"})
        self.assertFalse(form.validate())
        self.assertListEqual(form.title.errors, ["This field is required."])


class TestAdminPublicPageNewForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import AdminPublicPageNewForm

        return AdminPublicPageNewForm

    def test_validated(self):
        form = self._make_one({"body": "Foobar", "slug": "foobar", "title": "Foobar"})
        self.assertTrue(form.validate())

    def test_body_missing(self):
        form = self._make_one({"slug": "foobar", "title": "Foobar"})
        self.assertFalse(form.validate())
        self.assertListEqual(form.body.errors, ["This field is required."])

    def test_slug_missing(self):
        form = self._make_one({"body": "Foobar", "title": "Foobar"})
        self.assertFalse(form.validate())
        self.assertListEqual(form.slug.errors, ["This field is required."])

    def test_title_missing(self):
        form = self._make_one({"body": "Foobar", "slug": "foobar"})
        self.assertFalse(form.validate())
        self.assertListEqual(form.title.errors, ["This field is required."])


class TestAdminTopicForm(_FormMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..forms import AdminTopicForm

        return AdminTopicForm

    def test_validated(self):
        form = self._make_one({"status": "open"})
        self.assertTrue(form.validate())

    def test_status_missing(self):
        form = self._make_one({})
        self.assertFalse(form.validate())
        self.assertListEqual(form.status.errors, ["Not a valid choice"])

    def test_status_not_allowed(self):
        form = self._make_one({"status": "foobar"})
        self.assertFalse(form.validate())
        self.assertListEqual(form.status.errors, ["Not a valid choice"])
