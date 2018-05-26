from markupsafe import Markup

from ..interfaces import IPageQueryService
from .formatters import format_markdown


def get_partial(request, slug):
    """Returns a content of internal page.

    :param request: A :class:`pyramid.request.Request` object.
    :param slug: An internal page slug.
    """
    page_query_svc = request.find_service(IPageQueryService)
    try:
        return page_query_svc.internal_body_from_slug(slug)
    except ValueError:
        return None


def global_css(context, request):
    """Returns a string of inline global custom CSS for site-wide CSS override.
    This custom CSS is the content of ``internal:global/css`` page.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.
    """
    page = get_partial(request, "global/css")
    if page:
        return Markup(page)


def global_appendix(context, request):
    """Returns a HTML of global appendix content. This appendix content is the
    content of ``internal:global/appendix`` page.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.
    """
    page = get_partial(request, "global/appendix")
    if page:
        return format_markdown(context, request, page)


def global_footer(context, request):
    """Returns a HTML of global footer content. This footer content is the
    content of ``internal:global/footer`` page.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.
    :param cache_region: Optional cache region to cache this partial.
    """
    page = get_partial(request, "global/footer")
    if page:
        return Markup(page)
