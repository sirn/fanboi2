import html
import isodate
import misaka
import pytz
import re
from collections import OrderedDict
from jinja2 import Markup
from pyramid.threadlocal import get_current_registry, get_current_request


RE_NEWLINE = re.compile(r'(?:\r\n|\n|\r)')
RE_PARAGRAPH = re.compile(r'(?:(?P<newline>\r\n|\n|\r)(?P=newline)+)')
RE_THUMBNAILS = (
    (re.compile('https?\:\/\/(?:(?:\w+\.)?imgur\.com)\/(\w+)'),
     'http://i.imgur.com/{}s.jpg',
     'http://imgur.com/{}'),
)


def extract_thumbnail(text):
    """Extract thumbnailable URLs from text and create a list of 2-tuples
    containing ``(thumbnail_url, link_url)`` for use in clickable thumbnail
    links creation.
    """
    thumbnails = OrderedDict()
    for re, thumb, url in RE_THUMBNAILS:
        for item in re.findall(text):
            try:
                if not isinstance(item, tuple):
                    item = [item]
                thumbnails[thumb.format(*item)] = url.format(*item)
            except IndexError:
                pass
    return thumbnails.items()


TP_THUMB = '<a href="%s" class="thumbnail" target="_blank"><img src="%s"></a>'
TP_PARAGRAPH = '<p>%s</p>'

def format_text(text):
    """Format lines of text into HTML. Split into paragraphs at two or more
    consecutive newlines and adds ``<br>`` to any line with line break.
    """
    output = []
    thumbs = []

    # Turns text into paragraph.
    for paragraph in RE_PARAGRAPH.split(text):
        paragraph = paragraph.rstrip("\r\n")
        if paragraph:
            paragraph = TP_PARAGRAPH % html.escape(paragraph)
            paragraph = RE_NEWLINE.sub("<br>", paragraph)
            output.append(paragraph)

    # Display thumbnail at the end of post.
    thumbnails = extract_thumbnail(text)
    if thumbnails:
        for thumbnail, link in extract_thumbnail(text):
            thumbs.append(TP_THUMB % (link, thumbnail))
        output.append(TP_PARAGRAPH % ''.join(thumbs))

    return Markup('\n'.join(output))


def format_markdown(text):
    """Format text using Markdown parser."""
    return Markup(misaka.html(text))


RE_ANCHOR = re.compile(r'%s(\d+)(\-)?(\d+)?' % html.escape('>>'))


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
    text = RE_ANCHOR.sub(_anchor, text)
    return Markup(text)


def format_datetime(dt):
    """Format datetime into a human-readable format."""
    registry = get_current_registry()
    timezone = pytz.timezone(registry.settings['app.timezone'])
    return dt.astimezone(timezone).strftime('%b %d, %Y at %H:%M:%S')


def format_isotime(dt):
    """Format datetime into a machine-readable format."""
    return isodate.datetime_isoformat(dt.astimezone(pytz.utc))
