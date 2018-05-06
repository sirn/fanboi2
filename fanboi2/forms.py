import json

from wtforms import TextField, TextAreaField, Form, BooleanField
from wtforms import PasswordField
from wtforms.validators import Length as _Length
from wtforms.validators import Required, EqualTo, ValidationError


class Length(_Length):
    """"Works just like :class:`wtforms.validators.Length` but treat DOS
    newline as single character instead of two. This is to prevent situation
    where field length seemed incorrectly counted.
    """

    def __call__(self, form, field):
        length = field.data and len(field.data.replace('\r\n', '\n')) or 0
        if length < self.min or self.max != -1 and length > self.max:
            message = self.message
            if message is None:
                if self.max == -1:
                    message = field.ngettext(
                        'Field must be at least %(min)d character long.',
                        'Field must be at least %(min)d characters long.',
                        self.min)
                elif self.min == -1:
                    message = field.ngettext(
                        'Field cannot be longer than %(max)d character.',
                        'Field cannot be longer than %(max)d characters.',
                        self.max)
                else:
                    message = field.gettext('Field must be between %(min)d '
                                            'and %(max)d characters long.')
            raise ValidationError(message % dict(min=self.min, max=self.max))


class TopicForm(Form):
    """A :class:`Form` for creating new topic. This form should be populated
    to two objects, :attr:`title` to :class:`Topic` and :attr:`body` to
    :class:`Post`.
    """
    title = TextField('Title', validators=[Required(), Length(5, 200)])
    body = TextAreaField('Body', validators=[Required(), Length(5, 4000)])


class PostForm(Form):
    """A :class:`Form` for replying to a topic. The :attr:`body` field should
    be populated to :class:`Post`.
    """
    body = TextAreaField('Body', validators=[Required(), Length(5, 4000)])
    bumped = BooleanField('Bump this topic', default=True)


class AdminLoginForm(Form):
    """A :class:`Form` for logging into a moderation system."""
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])


class AdminSetupForm(Form):
    """A :class:`Form` for creating an initial user."""
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[
        Required(),
        Length(8, 64)])
    password_confirm = PasswordField(
        'Password confirmation',
        validators=[
            Required(),
            EqualTo('password', message='Password must match.')])


class AdminSettingForm(Form):
    """A :class:`Form` for updating settings."""
    value = TextAreaField('Value', validators=[Required()])

    def validate_value(form, field):
        """Custom field validator that ensure value is a valid JSON."""
        try:
            json.loads(field.data)
        except json.decoder.JSONDecodeError:
            raise ValidationError('Must be a valid JSON.')
