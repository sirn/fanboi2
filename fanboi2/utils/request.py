def serialize_request(request):
    """Serialize :class:`pyramid.request.Request` into a :type:`dict`.

    :param request: A :class:`pyramid.request.Request` object to serialize.

    :type request: pyramid.response.Request or dict
    :rtype: dict
    """

    if isinstance(request, dict):
        return request

    return {
        'application_url': request.application_url,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent,
        'referrer': request.referrer,
        'url': request.url,
    }
