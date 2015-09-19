import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import or_, and_
from fanboi2.errors import ParamsInvalidError, RateLimitedError, BaseError
from fanboi2.forms import TopicForm, PostForm
from fanboi2.models import DBSession, Board, Topic
from fanboi2.tasks import ResultProxy, add_topic, add_post, celery
from fanboi2.utils import RateLimiter, serialize_request


def root(request):
    """Display an API documentation view."""
    return {}


def boards_get(request):
    """Retrieve a list of all boards.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: sqlalchemy.orm.Query
    """
    return DBSession.query(Board).order_by(Board.title)


def board_get(request):
    """Retrieve a full info of a single board.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: sqlalchemy.orm.Query
    """
    return DBSession.query(Board).\
        filter_by(slug=request.matchdict['board']).\
        one()


def board_topics_get(request):
    """Retrieve all available topics within a single board.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: sqlalchemy.orm.Query
    """
    return board_get(request).topics. \
        filter(or_(Topic.status == "open",
                   and_(Topic.status != "open",
                        Topic.posted_at >= datetime.datetime.now() -
                        datetime.timedelta(days=7))))


def board_topics_post(request, board=None, form=None):
    """Create a new topic.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: celery.task.Task
    """
    if board is None: board = board_get(request)
    if form is None: form = TopicForm(request.params, request=request)

    if form.validate():
        ratelimit = RateLimiter(request, namespace=board.slug)
        if ratelimit.limited():
            timeleft = ratelimit.timeleft()
            raise RateLimitedError(timeleft)

        ratelimit.limit(board.settings['post_delay'])
        return add_topic.delay(
            request=serialize_request(request),
            board_id=board.id,
            title=form.title.data,
            body=form.body.data)

    raise ParamsInvalidError(form.errors)


def task_get(request, task=None):
    """Retrieve a task processing status for the given task id.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: fanboi2.tasks.ResultProxy
    """
    if task is None:
        task = celery.AsyncResult(request.matchdict['task'])
    response = ResultProxy(task)
    if response.success():
        if isinstance(response.object, BaseError):
            raise response.object
    return response


def topic_get(request):
    """Retrieve a full post info for an individual topic.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: sqlalchemy.orm.Query
    """
    return DBSession.query(Topic).\
        filter_by(id=request.matchdict['topic']).\
        one()


def topic_posts_get(request):
    """Retrieve all posts in a single topic or by or by search criteria.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: sqlalchemy.orm.Query
    """
    topic = topic_get(request)
    if 'query' in request.matchdict:
        return topic.scoped_posts(request.matchdict['query'])
    return topic.posts


def topic_posts_post(request, board=None, topic=None, form=None):
    """Create a new post within topic.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: celery.task.Task
    """
    if topic is None: topic = topic_get(request)
    if board is None: board = topic.board
    if form is None: form = PostForm(request.params, request=request)

    if form.validate():
        ratelimit = RateLimiter(request, namespace=board.slug)
        if ratelimit.limited():
            timeleft = ratelimit.timeleft()
            raise RateLimitedError(timeleft)

        ratelimit.limit(board.settings['post_delay'])
        return add_post.delay(
            request=serialize_request(request),
            topic_id=topic.id,
            body=form.body.data,
            bumped=form.bumped.data)

    raise ParamsInvalidError(form.errors)


def error_not_found(exc, request):
    """Handle any exception that should cause the app to treat it as
    NotFound resources, such as :class:`pyramid.httpexceptions.HTTPNotFound`
    or :class:`sqlalchemy.orm.exc.NoResultFound`.

    :param exc: An :class:`Exception`.
    :param request: A :class:`pyramid.request.Request` object.

    :type exc: Exception
    :type request: pyramid.request.Request
    :rtype: dict
    """
    request.response.status = '404 Not Found'
    return {
        'type': 'error',
        'status': 'not_found',
        'message': 'The resource %s %s could not be found.' % (
            request.method,
            request.path,
        )
    }


def error_base_handler(exc, request):
    """Handle any exception that should be rendered with the serializer.
    Normally this is any subclass of the :class:`fanboi2.errors.BaseError`.

    :param exc: A :class:`fanboi2.errors.BaseError`.
    :param request: A :class:`pyramid.request.Request` object.

    :type exc: fanboi2.errors.BaseError
    :type request: pyramid.request.Request
    :rtype: dict
    """
    request.response.status = exc.http_status
    return exc


def _api_routes_only(context, request):
    """A predicate for :meth:`pyramid.config.add_view` that returns true
    if the requested route is an API route.

    :type request: pyramid.request.Request
    :rtype: bool
    """
    return request.path.startswith('/api/')


def includeme(config):  # pragma: no cover
    config.add_route('api_root', '/')
    config.add_view(
        root,
        request_method='GET',
        route_name='api_root',
        renderer='api.mako')

    def _map_api_route(name, path, callables=None):
        config.add_route(name, path)
        if callables is not None:
            for method, callable in callables.items():
                config.add_view(
                    callable,
                    request_method=method,
                    route_name=name,
                    renderer='json')

    _map_api_route('api_boards', '/1.0/boards/', {'GET': boards_get})
    _map_api_route('api_board', '/1.0/boards/{board:\w+}/', {'GET': board_get})
    _map_api_route('api_board_topics', '/1.0/boards/{board:\w+}/topics/', {
        'GET': board_topics_get,
        'POST': board_topics_post})

    _map_api_route('api_task', '/1.0/tasks/{task}/', {'GET': task_get})
    _map_api_route('api_topic', '/1.0/topics/{topic:\d+}/', {'GET': topic_get})
    _map_api_route('api_topic_posts', '/1.0/topics/{topic:\d+}/posts/', {
        'GET': topic_posts_get,
        'POST': topic_posts_post})

    _map_api_route(
        'api_topic_posts_scoped',
        '/1.0/topics/{topic:\d+}/posts/{query}/',
        {'GET': topic_posts_get})

    def _map_api_errors(exc, callable):
        config.add_view(
            callable,
            context=exc,
            renderer='json',
            custom_predicates=[_api_routes_only])

    _map_api_errors(BaseError, error_base_handler)
    _map_api_errors(NoResultFound, error_not_found)
    config.add_notfound_view(
        error_not_found,
        append_slash=True,
        renderer='json',
        custom_predicates=[_api_routes_only])
