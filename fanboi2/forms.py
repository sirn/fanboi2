import hmac
import os
from hashlib import sha1
from wtforms import TextField, TextAreaField, Form
from wtforms.ext.csrf.fields import CSRFTokenField
from wtforms.validators import Required, Length, ValidationError


class SecureForm(Form):
    """Generate CRSF token based based on randomly generated string token."""
    csrf_token = CSRFTokenField()

    def __init__(self, formdata=None, obj=None, prefix='', request=None):
        super(SecureForm, self).__init__(formdata, obj, prefix)
        self.request = request
        self.csrf_token.current_token = self.generate_csrf_token()

    def _generate_hmac(self, message):
        secret = self.request.registry.settings['app.secret']
        return hmac.new(
            bytes(secret.encode('utf8')),
            bytes(message.encode('utf8')),
            digestmod=sha1,
        ).hexdigest()

    def generate_csrf_token(self):
        if 'csrf' not in self.request.session:
            self.request.session['csrf'] = sha1(os.urandom(64)).hexdigest()
        self.csrf_token.csrf_key = self.request.session['csrf']
        return self._generate_hmac(self.request.session['csrf'])

    def validate_csrf_token(self, field):
        if not field.data:
            raise ValidationError('CSRF token missing')
        hmac_compare = self._generate_hmac(field.csrf_key)
        if not hmac.compare_digest(field.data, hmac_compare):
            raise ValidationError('CSRF token mismatched')

    @property
    def data(self):
        d = super(SecureForm, self).data
        d.pop('csrf_token')
        return d


class TopicForm(SecureForm):
    """A :class:`Form` for creating new topic. This form should be populated
    to two objects, :attr:`title` to :class:`Topic` and :attr:`body` to
    :class:`Post`.
    """
    title = TextField('Title', validators=[Required(), Length(5, 200)])
    body = TextAreaField('Body', validators=[Required(), Length(2, 4000)])


class PostForm(SecureForm):
    """A :class:`Form` for replying to a topic. The :attr:`body` field should
    be populated to :class:`Post`.
    """
    body = TextAreaField('Body', validators=[Required(), Length(2, 4000)])
