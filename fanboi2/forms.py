from wtforms import Form, TextField, TextAreaField
from wtforms.validators import Required, Length


class TopicForm(Form):
    title = TextField(u'Title', validators=[Required(), Length(5, 200)])
    body = TextAreaField(u'Body', validators=[Required(), Length(2, 4000)])
