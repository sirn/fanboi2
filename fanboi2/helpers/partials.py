from markupsafe import Markup
from fanboi2.helpers.formatters import format_markdown
from fanboi2.models import DBSession, Page


def _get_internal_page(slug):
    """Returns a content of internal page.

    :param slug: An internal page slug.
    :type slug: String
    :rtype: String or None
    """
    page = DBSession.query(Page).filter_by(
            namespace='internal',
            slug=slug).\
        first()
    if page:
        return page.body


def global_css(context, request):
    """Returns a string of inline global custom CSS for site-wide CSS override.
    This custom CSS is the content of ``internal:global_css`` page.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type context: mako.runtime.Context or None
    :type request: pyramid.request.Request
    :rtype: Markup or None
    """
    page = _get_internal_page('global_css')
    if page:
        return Markup(page)


def global_appendix(context, request):
    """Returns a HTML of global appendix content. This appendix content is the
    content of ``internal:global_appendix`` page.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type context: mako.runtime.Context or None
    :type request: pyramid.request.Request
    :rtype: Markup or None
    """
    page = _get_internal_page('global_appendix')
    if page:
        return format_markdown(context, request, page)
