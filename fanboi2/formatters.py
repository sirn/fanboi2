import html
import isodate
import misaka
import pytz
import re
import urllib.parse as urlparse
from collections import OrderedDict
from html.parser import HTMLParser
from jinja2 import Markup
from pyramid.threadlocal import get_current_registry, get_current_request


RE_NEWLINE = re.compile(r'(?:\r\n|\n|\r)')
RE_PARAGRAPH = re.compile(r'(?:(?P<newline>\r\n|\n|\r)(?P=newline)+)')
RE_THUMBNAILS = (
    (re.compile(r"https?\:\/\/(?:(?:\w+\.)?imgur\.com)\/(\w+)", re.ASCII),
     'http://i.imgur.com/{}s.jpg',
     'http://imgur.com/{}'),
)

RE_LINK = re.compile(r"""
 (                     # Group start
   (http|ftp|https)    # Protocols
 \:\/\/                # Separator
   ([a-zA-Z0-9\-]+)    # Sub-domain
 \.                    # Dot
   ([a-zA-Z0-9.\-]+)   # Domain, or TLD
 \/                    # Slash
   ?([^\s<*]+)         # Link, all characters except space and end tag
 )
""", re.VERBOSE)


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
            except IndexError:  # pragma: no cover
                pass
    return thumbnails.items()


TP_THUMB = '<a href="%s" class="thumbnail" target="_blank"><img src="%s"></a>'
TP_LINK = '<a href="%s" class="link" target="_blank" rel="nofollow">%s</a>'
TP_PARAGRAPH = '<p>%s</p>'


def url_fix(string):
    """Sanitize user URL that may contains unsafe characters like ' and so on
    in similar way browsers handle data entered by the user:

    >>> url_fix('http://de.wikipedia.org/wiki/Elf (Begriffsklärung)')
    'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'

    Ported from ``werkzeug.urls.url_fix``.
    """
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(string)
    path = urlparse.quote(path, '/%')
    qs = urlparse.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))


def format_text(text):
    """Format lines of text into HTML. Split into paragraphs at two or more
    consecutive newlines and adds ``<br>`` to any line with line break.
    """
    output = []
    thumbs = []

    # Auto-link
    def _replace_link(match):
        link = HTMLParser().unescape(urlparse.unquote(match.group(0)))
        return Markup(TP_LINK % (
            url_fix(link),
            html.escape(link)))

    # Turns text into paragraph.
    for paragraph in RE_PARAGRAPH.split(text):
        paragraph = paragraph.rstrip("\r\n")
        if paragraph:
            paragraph = TP_PARAGRAPH % html.escape(paragraph)
            paragraph = RE_LINK.sub(_replace_link, paragraph)
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
TP_ANCHOR = '<a data-number="%s" href="%s" class="anchor">%s</a>'


def format_post(post):
    """Works similar to :func:`format_text` but also process link within
    the same topic, i.e. a ``>>52`` anchor syntax will create a link to
    post numbered 52 in the same topic.
    """
    text = format_text(post.obj.body)
    request = get_current_request()

    def _anchor(match):
        anchor = ''.join([m for m in match.groups() if m is not None])
        return Markup(TP_ANCHOR % (
            anchor,
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
