from markupsafe import Markup
from sqlalchemy.orm.exc import NoResultFound

from ..interfaces import IPageQueryService
from .formatters import format_markdown


def _get_cache_key(slug):
    """Returns a cache key for given partial.

    :param slug: An internal page slug.
    """
    return 'helpers.partials:slug=%s' % (slug,)


def get_partial(request, slug):
    """Returns a content of internal page.

    :param request: A :class:`pyramid.request.Request` object.
    :param slug: An internal page slug.
    """
    page_query_svc = request.find_service(IPageQueryService)
    cache_region = request.find_service(name='cache')

    def _creator():
        try:
            page = page_query_svc.internal_page_from_slug(slug)
        except NoResultFound:
            return
        if page:
            return page.body

    return cache_region.get_or_create(
        _get_cache_key(slug),
        _creator,
        expiration_time=43200)


def reload_partial(request, slug):
    """Delete the key for the given slug from the cache to force
    reloading of partials the next time it is accessed.

    :param request: A :class:`pyramid.request.Request` object.
    :param slug: An internal page slug.
    """
    cache_region = request.find_service(name='cache')
    cache_key = _get_cache_key(slug)
    return cache_region.delete(cache_key)


def global_css(context, request):
    """Returns a string of inline global custom CSS for site-wide CSS override.
    This custom CSS is the content of ``internal:global/css`` page.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.
    """
    page = get_partial(request, 'global/css')
    if page:
        return Markup(page)


def global_appendix(context, request):
    """Returns a HTML of global appendix content. This appendix content is the
    content of ``internal:global/appendix`` page.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.
    """
    page = get_partial(request, 'global/appendix')
    if page:
        return format_markdown(context, request, page)


def global_footer(context, request):
    """Returns a HTML of global footer content. This footer content is the
    content of ``internal:global/footer`` page.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.
    :param cache_region: Optional cache region to cache this partial.
    """
    page = get_partial(request, 'global/footer')
    if page:
        return Markup(page)
