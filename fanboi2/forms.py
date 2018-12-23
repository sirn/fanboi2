import ipaddress
import json
import re

from wtforms import (
    TextField,
    TextAreaField,
    Form,
    BooleanField,
    PasswordField,
    IntegerField,
    SelectField,
)
from wtforms.validators import Length as _Length, Required, EqualTo, ValidationError


class Length(_Length):
    """"Works just like :class:`wtforms.validators.Length` but treat DOS
    newline as single character instead of two. This is to prevent situation
    where field length seemed incorrectly counted.
    """

    def __call__(self, form, field):
        length = field.data and len(field.data.replace("\r\n", "\n")) or 0
        if length < self.min or self.max != -1 and length > self.max:
            message = self.message
            if message is None:
                if self.max == -1:
                    message = field.ngettext(
                        "Field must be at least %(min)d character long.",
                        "Field must be at least %(min)d characters long.",
                        self.min,
                    )
                elif self.min == -1:
                    message = field.ngettext(
                        "Field cannot be longer than %(max)d character.",
                        "Field cannot be longer than %(max)d characters.",
                        self.max,
                    )
                else:
                    message = field.gettext(
                        "Field must be between %(min)d " "and %(max)d characters long."
                    )
            raise ValidationError(message % dict(min=self.min, max=self.max))


class TopicForm(Form):
    """A :class:`Form` for creating new topic. This form should be populated
    to two objects, :attr:`title` to :class:`Topic` and :attr:`body` to
    :class:`Post`.
    """

    title = TextField("Title", validators=[Required(), Length(5, 200)])
    body = TextAreaField("Body", validators=[Required(), Length(5, 4000)])


class PostForm(Form):
    """A :class:`Form` for replying to a topic. The :attr:`body` field should
    be populated to :class:`Post`.
    """

    body = TextAreaField("Body", validators=[Required(), Length(5, 4000)])
    bumped = BooleanField("Bump this topic", default=True)


class AdminLoginForm(Form):
    """A :class:`Form` for logging into a moderation system."""

    username = TextField("Username", validators=[Required()])
    password = PasswordField("Password", validators=[Required()])


class AdminSetupForm(Form):
    """A :class:`Form` for creating an initial user."""

    username = TextField("Username", validators=[Required(), Length(2, 32)])
    password = PasswordField("Password", validators=[Required(), Length(8, 64)])
    password_confirm = PasswordField(
        "Password confirmation",
        validators=[Required(), EqualTo("password", message="Password must match.")],
    )
    name = TextField("Name", validators=[Required(), Length(2, 64)])


class AdminSettingForm(Form):
    """A :class:`Form` for updating settings."""

    value = TextAreaField("Value", validators=[Required()])

    def validate_value(self, field):
        """Custom field validator that ensure value is a valid JSON."""
        try:
            json.loads(field.data)
        except json.decoder.JSONDecodeError:
            raise ValidationError("Must be a valid JSON.")


class AdminBanForm(Form):
    """A :class:`Form` for creating and updating bans."""

    ip_address = TextField("IP address", validators=[Required()])
    description = TextField("Description")
    duration = IntegerField("Duration", default=0)
    scope = TextField("Scope")
    active = BooleanField("Active", default=True)

    def validate_ip_address(self, field):
        """Custom field validator that ensure IP address is valid."""
        try:
            ipaddress.ip_network(field.data)
        except ValueError:
            raise ValidationError("Must be a valid IP address.")


class AdminBanwordForm(Form):
    """A :class:`Form` for creating and updating banwords."""

    expr = TextField("Expression", validators=[Required()])
    description = TextField("Description")
    scope = TextField("Scope")
    active = BooleanField("Active", default=True)

    def validate_expr(self, field):
        """Custom field validator that ensure expr is a valid regular expression."""
        try:
            re.compile(field.data)
        except re.error:
            raise ValidationError("Must be a valid regular expression.")


class AdminBoardForm(Form):
    """A :class:`Form` for updating a board."""

    title = TextField("Title", validators=[Required()])
    description = TextField("Description", validators=[Required()])
    status = SelectField(
        "Status",
        validators=[Required()],
        choices=[
            ("open", "Open"),
            ("restricted", "Restricted"),
            ("locked", "Locked"),
            ("archived", "Archived"),
        ],
    )

    agreements = TextAreaField("Agreements", validators=[Required()])
    settings = TextAreaField("Settings", validators=[Required()])

    def validate_settings(self, field):
        """Custom field validator that ensure value is a valid JSON."""
        try:
            json.loads(field.data)
        except json.decoder.JSONDecodeError:
            raise ValidationError("Must be a valid JSON.")


class AdminBoardNewForm(AdminBoardForm):
    """A :class:`Form` for creating a board."""

    slug = TextField("Slug", validators=[Required()])


class AdminPageForm(Form):
    """A :class:`Form` for creating and updating pages."""

    body = TextAreaField("Body", validators=[Required()])


class AdminPublicPageForm(AdminPageForm):
    """A :class:`Form` for updating public pages."""

    title = TextField("Title", validators=[Required()])


class AdminPublicPageNewForm(AdminPublicPageForm):
    """A :class:`Form` for creating public pages."""

    slug = TextField("Slug", validators=[Required()])


class AdminTopicForm(Form):
    """A :class:`Form` for updating topic."""

    status = SelectField(
        "Status",
        validators=[Required()],
        choices=[("open", "Open"), ("locked", "Locked")],
    )
