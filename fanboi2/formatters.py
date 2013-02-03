import html
import isodate
import misaka
import pytz
import re
from jinja2 import Markup
from pyramid.threadlocal import get_current_registry, get_current_request


re_newline = re.compile(r'(?:\r\n|\n|\r)')
re_paragraph = re.compile(r'(?:(?P<newline>\r\n|\n|\r)(?P=newline)+)')


def format_text(text):
    """Format lines of text into HTML. Split into paragraphs at two or more
    consecutive newlines and adds ``<br>`` to any line with line break.
    """
    output = []
    for paragraph in re_paragraph.split(text):
        paragraph = paragraph.rstrip("\r\n")
        if paragraph:
            paragraph = '<p>%s</p>' % html.escape(paragraph)
            paragraph = re_newline.sub("<br>", paragraph)
            output.append(paragraph)
    return Markup('\n'.join(output))


def format_markdown(text):
    """Format text using Markdown parser."""
    return Markup(misaka.html(text))


re_anchor = re.compile(r'%s(\d+)(\-)?(\d+)?' % html.escape('>>'))


def format_post(post):
    """Works similar to :func:`format_text` but also process link within
    the same topic, i.e. a ``>>52`` anchor syntax will create a link to
    post numbered 52 in the same topic.
    """
    text = format_text(post.obj.body)
    request = get_current_request()

    def _anchor(match):
        anchor = ''.join([m for m in match.groups() if m is not None])
        return Markup("<a href=\"%s\" class=\"anchor\">%s</a>" % (
            request.resource_path(post.topic, anchor),
            html.escape(">>%s" % anchor),))
    text = re_anchor.sub(_anchor, text)
    return Markup(text)


def format_datetime(dt):
    """Format datetime into a human-readable format."""
    registry = get_current_registry()
    timezone = pytz.timezone(registry.settings['app.timezone'])
    return dt.astimezone(timezone).strftime('%b %d, %Y at %H:%M:%S')


def format_isotime(dt):
    """Format datetime into a machine-readable format."""
    return isodate.datetime_isoformat(dt.astimezone(pytz.utc))
