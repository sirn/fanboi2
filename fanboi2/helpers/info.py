from fanboi2.version import __VERSION__


def app_version(context, request):
    """Returns a version of the application.

    :param context: A :class:`mako.runtime.Context` object.
    :param request: A :class:`pyramid.request.Request` object.
    """
    return __VERSION__
