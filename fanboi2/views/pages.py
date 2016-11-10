from pyramid.response import Response
from fanboi2.views.api import page_get


def robots_show(request):
    """Display robots.txt.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    page = page_get(request, page='global/robots', namespace='internal')
    response = Response(page.body)
    response.content_type = 'text/plain'
    return response


def page_show(request):
    """Display a single page.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    page = page_get(request)
    return locals()


def includeme(config):  # pragma: no cover
    config.add_view(
        robots_show,
        request_method='GET',
        route_name='robots',
        renderer='string')

    config.add_route('page', '/{page:.*}/')
    config.add_view(
        page_show,
        request_method='GET',
        route_name='page',
        renderer='pages/show.mako')
