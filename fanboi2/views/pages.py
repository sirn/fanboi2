from fanboi2.views.api import page_get


def page_show(request):
    """Display a single page.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    page = page_get(request)
    return locals()


def includeme(config):  # pragma: no cover
    config.add_route('page', '/{page:\w+}/')
    config.add_view(
        page_show,
        request_method='GET',
        route_name='page',
        renderer='pages/show.mako')
