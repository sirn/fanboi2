from markupsafe import Markup
from fanboi2.helpers.formatters import format_markdown
from fanboi2.models import DBSession, Page
from fanboi2.cache import cache_region as cache_region_


def _get_internal_page(slug, cache_region=cache_region_):
    """Returns a content of internal page.

    :param slug: An internal page slug.
    :type slug: String
    :rtype: String or None
    """
    def _creator():
        page = DBSession.query(Page).filter_by(
                namespace='internal',
                slug=slug).\
            first()
        if page:
            return page.body
    return cache_region.get_or_create(
        'partial:%s' % (slug,),
        _creator,
        expiration_time=43200)


def global_css(context, request, cache_region=cache_region_):
    """Returns a string of inline global custom CSS for site-wide CSS override.
    This custom CSS is the content of ``internal:global/css`` page.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.
    :param cache_region: Optional cache region to cache this partial.

    :type context: mako.runtime.Context or None
    :type request: pyramid.request.Request
    :type cache_region: dogpile.cache.region.CacheRegion
    :rtype: Markup or None
    """
    page = _get_internal_page('global/css', cache_region)
    if page:
        return Markup(page)


def global_appendix(context, request, cache_region=cache_region_):
    """Returns a HTML of global appendix content. This appendix content is the
    content of ``internal:global/appendix`` page.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.
    :param cache_region: Optional cache region to cache this partial.

    :type context: mako.runtime.Context or None
    :type request: pyramid.request.Request
    :type cache_region: dogpile.cache.region.CacheRegion
    :rtype: Markup or None
    """
    page = _get_internal_page('global/appendix', cache_region)
    if page:
        return format_markdown(context, request, page)


def global_footer(context, request, cache_region=cache_region_):
    """Returns a HTML of global footer content. This footer content is the
    content of ``internal:global/footer`` page.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.
    :param cache_region: Optional cache region to cache this partial.

    :type context: mako.runtime.Context or None
    :type request: pyramid.request.Request
    :type cache_region: dogpile.cache.region.CacheRegion
    :rtype: Markup or None
    """
    page = _get_internal_page('global/footer', cache_region)
    if page:
        return Markup(page)
