from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.renderers import render_to_response
from fanboi2.errors import RateLimitedError, FormInvalidError
from fanboi2.forms import SecurePostForm, SecureTopicForm
from fanboi2.views.api import boards_get, board_get, board_topics_get,\
    topic_get, topic_posts_get, topic_posts_post, board_topics_post


def root(request):
    """Display a list of all boards.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    boards = boards_get(request)
    return locals()


def board_show(request):
    """Display a single board with its related topics.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    board = board_get(request)
    topics = board_topics_get(request).limit(10)
    return locals()


def board_all(request):
    """Display a single board with a list of all its topic.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    board = board_get(request)
    topics = board_topics_get(request).all()
    return locals()


def board_new_get(request):
    """Display a form for creating new topic in a board.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    board = board_get(request)
    form = SecureTopicForm(request=request)
    return locals()


def board_new_post(request):
    """Handle form posting for creating new topic in a board.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    board = board_get(request)
    form = SecureTopicForm(request.params, request=request)
    try:
        task = board_topics_post(request, board=board, form=form)
        return HTTPFound(location=request.route_path(
            route_name='board_new',
            board=board.slug,
            _query={'task': task.id}))
    except RateLimitedError as e:
        timeleft = e.timeleft
        return render_to_response('boards/error.mako', locals())
    except FormInvalidError as e:
        return locals()


def topic_show_get(request):
    """Display a single topic with its related posts.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    board = board_get(request)
    topic = topic_get(request)
    posts = topic_posts_get(request)
    if not topic.board_id == board.id or not posts:
        raise HTTPNotFound(request.path)
    form = SecurePostForm(request=request)
    return locals()


def topic_show_post(request):
    """Handle form posting for replying to a topic.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    board = board_get(request)
    topic = topic_get(request)
    if not topic.board_id == board.id:
        raise HTTPNotFound(request.path)
    form = SecurePostForm(request.params, request=request)
    try:
        task = topic_posts_post(request, board=board, topic=topic, form=form)
        return HTTPFound(location=request.route_path(
            route_name='topic',
            board=topic.board.slug,
            topic=topic.id,
            _query={'task': task.id}))
    except RateLimitedError as e:
        timeleft = e.timeleft
        return render_to_response('topics/error.mako', locals())
    except FormInvalidError as e:
        return locals()


def includeme(config):  # pragma: no cover
    def _map_view(name, path, renderer, callables=None):
        config.add_route(name, path)
        if callables is not None:
            for method, callable in callables.items():
                config.add_view(
                    callable,
                    request_method=method,
                    route_name=name,
                    renderer=renderer)

    _map_view('root', '/', 'root.mako', {'GET': root})
    _map_view('board', '/{board:\w+}/', 'boards/show.mako', {'GET': board_show})
    _map_view('board_all', '/{board:\w+}/all/', 'boards/all.mako', {
        'GET': board_all})

    _map_view('board_new', '/{board:\w+}/new/', 'boards/new.mako', {
        'GET': board_new_get,
        'POST': board_new_post})

    _map_view('topic', '/{board:\w+}/{topic:\d+}/', 'topics/show.mako', {
        'GET': topic_show_get,
        'POST': topic_show_post})

    _map_view('topic_scoped',
        '/{board:\w+}/{topic:\d+}/{query}/',
        'topics/show.mako',
        {'GET': topic_show_get})
