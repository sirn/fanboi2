from pyramid.response import Response

from ..interfaces import IPageQueryService


def robots_show(request):
    """Display robots.txt.

    :param request: A :class:`pyramid.request.Request` object.
    """
    page_query_svc = request.find_service(IPageQueryService)
    page = page_query_svc.internal_page_from_slug("global/robots")
    response = Response(page.body)
    response.content_type = "text/plain"
    return response


def page_show(request):
    """Display a single page.

    :param request: A :class:`pyramid.request.Request` object.
    """
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict["page"]
    page = page_query_svc.public_page_from_slug(page_slug)
    return {"page": page}


def includeme(config):  # pragma: no cover
    config.add_route("page", "/{page:.*}/")

    config.add_view(
        robots_show, request_method="GET", route_name="robots", renderer="string"
    )

    config.add_view(
        page_show, request_method="GET", route_name="page", renderer="pages/show.mako"
    )

    config.scan()
