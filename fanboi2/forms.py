from wtforms import Form, TextField, TextAreaField
from wtforms.validators import Required, Length


class TopicForm(Form):
    """A :class:`Form` for creating new topic. This form should be populated
    to two objects, :attr:`title` to :class:`Topic` and :attr:`body` to
    :class:`Post`.
    """
    title = TextField('Title', validators=[Required(), Length(5, 200)])
    body = TextAreaField('Body', validators=[Required(), Length(2, 4000)])


class PostForm(Form):
    """A :class:`Form` for replying to a topic. The :attr:`body` field should
    be populated to :class:`Post`.
    """
    body = TextAreaField('Body', validators=[Required(), Length(2, 4000)])