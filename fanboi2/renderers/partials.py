from markupsafe import Markup
from pyramid.request import Request

from ..interfaces import IPageQueryService
from .formatters import format_markdown


def get_partial(request: Request, slug: str):
    """Returns a content of internal page.

    :param request: A :class:`pyramid.request.Request` object.
    :param slug: An internal page slug.
    """
    page_query_svc = request.find_service(IPageQueryService)
    try:
        return page_query_svc.internal_body_from_slug(slug)
    except ValueError:
        return None


def global_css(request: Request):
    """Returns a string of inline global custom CSS for site-wide CSS override.
    This custom CSS is the content of ``internal:global/css`` page.
    """
    page = get_partial(request, "global/css")
    if page:
        return Markup(page)


def global_appendix(request: Request):
    """Returns a HTML of global appendix content. This appendix content is the
    content of ``internal:global/appendix`` page.
    """
    page = get_partial(request, "global/appendix")
    if page:
        return format_markdown(page)


def global_footer(request: Request):
    """Returns a HTML of global footer content. This footer content is the
    content of ``internal:global/footer`` page.
    """
    page = get_partial(request, "global/footer")
    if page:
        return Markup(page)
