from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config as _view_config
from fanboi2.forms import PostForm, TopicForm
from fanboi2.tasks import add_topic, add_post
from fanboi2.utils import RateLimiter, serialize_request
from fanboi2.views.api import boards_get, board_get, board_topics_get,\
    topic_get, topic_posts_get


def get_view(**kwargs):
    kwargs['request_method'] = 'GET'
    return _view_config(**kwargs)


def post_view(**kwargs):
    kwargs['request_method'] = 'POST'
    return _view_config(**kwargs)


@get_view(route_name='root', renderer='root.mako')
def root(request):
    """Display a list of all boards.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    boards = boards_get(request)
    return locals()


@get_view(route_name='board', renderer='boards/show.mako')
def board_show(request):
    """Display a single board with its related topics.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    board = board_get(request)
    topics = board_topics_get(request).limit(10)
    return locals()


@get_view(route_name='board_all', renderer='boards/all.mako')
def board_all(request):
    """Display a single board with a list of all its topic.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    board = board_get(request)
    topics = board_topics_get(request).all()
    return locals()


@get_view(route_name='board_new', renderer='boards/new.mako')
def board_new_get(request):
    """Display a form for creating new topic in a board.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    board = board_get(request)
    form = TopicForm(request=request)
    return locals()


@post_view(route_name='board_new', renderer='boards/new.mako')
def board_new_post(request):
    """Handle form posting for creating new topic in a board.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    board = board_get(request)
    form = TopicForm(request.params, request=request)

    if form.validate():
        ratelimit = RateLimiter(request, namespace=board.slug)
        if ratelimit.limited():
            return render_to_response('boards/error.mako', locals())

        task = add_topic.delay(
            request=serialize_request(request),
            board_id=board.id,
            title=form.title.data,
            body=form.body.data)

        ratelimit.limit(board.settings['post_delay'])
        return HTTPFound(location=request.route_path(
            route_name='board_new',
            board=board.slug,
            _query={'task': task.id}))

    return locals()


@get_view(route_name='topic', renderer='topics/show.mako')
@get_view(route_name='topic_scoped', renderer='topics/show.mako')
def topic_show_get(request):
    """Display a single topic with its related posts.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: dict
    """
    board = board_get(request)
    topic = topic_get(request)
    if not topic.board_id == board.id:
        raise HTTPNotFound(request.path)
    posts = topic_posts_get(request)
    form = PostForm(request=request)
    return locals()


@post_view(route_name='topic', renderer='topics/show.mako')
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
    form = PostForm(request.params, request=request)

    if form.validate():
        ratelimit = RateLimiter(request, namespace=board.slug)
        if ratelimit.limited():
            return render_to_response('topics/error.mako', locals())

        task = add_post.delay(
            request=serialize_request(request),
            topic_id=topic.id,
            body=form.body.data,
            bumped=form.bumped.data)

        ratelimit.limit(board.settings['post_delay'])
        return HTTPFound(location=request.route_path(
            route_name='topic',
            board=topic.board.slug,
            topic=topic.id,
            _query={'task': task.id}))

    return locals()
