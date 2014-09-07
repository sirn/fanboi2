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


RE_PARAGRAPH = re.compile(r'(?:(?P<newline>\r\n|\n|\r)(?P=newline)+)')
RE_THUMBNAILS = (
    (re.compile(r"https?\:\/\/(?:(?:\w+\.)?imgur\.com)\/(\w+)", re.ASCII),
     '//i.imgur.com/{}s.jpg',
     '//imgur.com/{}'),
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


class PostMarkup(Markup):
    """Works like :class:`Markup` but allow passing in hints for post
    formatting such as raw data length or shortened status.
    """

    def __init__(self, *args, **kwargs):
        super(PostMarkup, self).__init__(*args, **kwargs)
        self.length = None
        self.shortened = False

    def __len__(self):
        if not self.length:
            return super(PostMarkup, self).__len__()
        return self.length


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
TP_THUMB_PARAGRAPH = '<p class="thumbnails">%s</p>'


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


def format_text(text, shorten=None):
    """Format lines of text into HTML. Split into paragraphs at two or more
    consecutive newlines and adds `<br>` to any line with line break. If
    `shorten` is given, then the post will be shortened to the first
    paragraph that exceed the given value.
    """
    output = []
    thumbs = []
    length = 0
    shortened = False

    # Auto-link
    def _replace_link(match):
        link = HTMLParser().unescape(urlparse.unquote(match.group(0)))
        return Markup(TP_LINK % (
            url_fix(link),
            html.escape(link)))

    # Turns text into paragraph.
    text = "\n".join((t.strip() for t in text.splitlines()))  # Cleanup
    for paragraph in RE_PARAGRAPH.split(text):
        paragraph = paragraph.strip()
        if paragraph:
            lines = []
            for line in paragraph.splitlines():
                if shorten and length >= shorten:
                    shortened = True
                    break
                lines.append(html.escape(line))
                length += len(line)
            paragraph = TP_PARAGRAPH % '<br>'.join(lines)
            paragraph = RE_LINK.sub(_replace_link, paragraph)
            output.append(paragraph)
            if shortened:
                break

    # Display thumbnail at the end of post.
    thumbnails = extract_thumbnail(text)
    if thumbnails:
        for thumbnail, link in extract_thumbnail(text):
            thumbs.append(TP_THUMB % (link, thumbnail))
        output.append(TP_THUMB_PARAGRAPH % ''.join(thumbs))

    markup = PostMarkup('\n'.join(output))
    markup.length = length
    markup.shortened = shortened
    return markup


def format_markdown(text):
    """Format text using Markdown parser."""
    if text is not None:
        return Markup(misaka.html(str(text)))


RE_ANCHOR = re.compile(r'%s(\d+)(\-)?(\d+)?' % html.escape('>>'))
TP_ANCHOR = '<a data-number="%s" href="%s" class="anchor">%s</a>'

RE_ANCHOR_CROSS = re.compile(r"""
  %s\/                       # Syntax start
  (\w+)                      # Board name
  (?:\/(\d+))?               # Topic id
  (?:\/(\d+)(\-)?(\d+)?)     # Post id
  ?(\/?)                     # Trailing slash
""" % html.escape('>>>'), re.VERBOSE)
TP_ANCHOR_CROSS = ''.join("""
<a data-board="%s" data-topic="%s" data-number="%s" href="%s" class="anchor">
%s
</a>
""".splitlines())

TP_SHORTENED = ''.join("""
<p class="shortened">
Post shortened. <a href="%s">See full post</a>.
</p>
""".splitlines())


def format_post(post, shorten=None):
    """Works similar to :func:`format_text` but also process link within
    the same topic, i.e. a `>>52` anchor syntax will create a link to
    post numbered 52 in the same topic, as well as display "click to see
    more" link for posts that has been shortened.
    """
    text = format_text(post.body, shorten)
    request = get_current_request()

    # Append click to see more link if post is shortened.
    try:
        if text.shortened:
            text += Markup("\n" + TP_SHORTENED % (
                request.route_path('topic_scoped',
                                   board=post.topic.board.slug,
                                   topic=post.topic.id,
                                   query="%s-" % post.number)))
    except AttributeError:  # pragma: no cover
        pass

    # Convert cross anchor (>>>/demo/123/1-10) into link.
    def _anchor_cross(match):
        board = match.groups()[0]
        topic = match.groups()[1] if match.groups()[1] else ''
        anchor = ''.join([m for m in match.groups()[2:-1] if m is not None])
        trail = match.groups()[-1]

        if board and topic:
            args = {'board': board, 'topic': topic, 'query': anchor}
            args['query'] = anchor if anchor else 'recent'
            path = request.route_path('topic_scoped', **args)
        else:
            path = request.route_path('board', board=board)

        text = []
        for part in (board, topic, anchor):
            if part:
                text.append(part)
        text = html.escape(">>>/%s" % '/'.join(text))
        text += str(trail) if trail else ''
        return Markup(TP_ANCHOR_CROSS % (board, topic, anchor, path, text))

    text = RE_ANCHOR_CROSS.sub(_anchor_cross, text)

    # Convert post anchor (>>123) into link.
    def _anchor(match):
        anchor = ''.join([m for m in match.groups() if m is not None])
        return Markup(TP_ANCHOR % (
            anchor,
            request.route_path('topic_scoped',
                               board=post.topic.board.slug,
                               topic=post.topic.id,
                               query=anchor),
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
