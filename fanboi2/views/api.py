from sqlalchemy.orm.exc import NoResultFound
from webob.multidict import MultiDict

from ..errors import (
    ParamsInvalidError,
    RateLimitedError,
    BanRejectedError,
    BanwordRejectedError,
    BaseError,
)
from ..forms import TopicForm, PostForm
from ..interfaces import (
    IBanQueryService,
    IBanwordQueryService,
    IBoardQueryService,
    IPageQueryService,
    IPostCreateService,
    IPostQueryService,
    IRateLimiterService,
    ITaskQueryService,
    ITopicCreateService,
    ITopicQueryService,
)


def _get_params(request):
    """Return a :class:`MultiDict` of the params given in request
    regardless of whether the request is sent as JSON or as formdata.

    :param request: A :class:`pyramid.request.Request` object.
    """
    params = request.POST
    if request.content_type.startswith("application/json"):
        try:
            params = MultiDict(request.json_body)
        except ValueError:  # pragma: no cover
            pass
    return params


def root(request):
    """Display an API documentation view."""
    return {}


def boards_get(request):
    """Retrieve a list of all boards.

    :param request: A :class:`pyramid.request.Request` object.
    """
    board_query_svc = request.find_service(IBoardQueryService)
    return board_query_svc.list_active()


def board_get(request):
    """Retrieve a full info of a single board.

    :param request: A :class:`pyramid.request.Request` object.
    """
    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    return board_query_svc.board_from_slug(board_slug)


def board_topics_get(request):
    """Retrieve all available topics within a single board.

    :param request: A :class:`pyramid.request.Request` object.
    """
    board_query_svc = request.find_service(IBoardQueryService)
    topic_query_svc = request.find_service(ITopicQueryService)
    board_slug = request.matchdict["board"]
    board_query_svc.board_from_slug(board_slug)  # ensure exists
    topics = topic_query_svc.list_from_board_slug(board_slug)
    return topics


def board_topics_post(request):
    """Create a new topic.

    :param request: A :class:`pyramid.request.Request` object.
    """
    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    params = _get_params(request)
    form = TopicForm(params, request=request)

    if not form.validate():
        raise ParamsInvalidError(form.errors)

    ban_query_svc = request.find_service(IBanQueryService)
    ban_scope = {"board": board.slug}
    if ban_query_svc.is_banned(request.client_addr, scopes=ban_scope):
        raise BanRejectedError()

    banword_query_svc = request.find_service(IBanwordQueryService)
    if banword_query_svc.is_banned(form.body.data, scopes=ban_scope):
        raise BanwordRejectedError()

    rate_limiter_svc = request.find_service(IRateLimiterService)
    if rate_limiter_svc:
        payload = {"ip_address": request.client_addr, "board": board.slug}
        if rate_limiter_svc.is_limited(**payload):
            time_left = rate_limiter_svc.time_left(**payload)
            raise RateLimitedError(time_left)

        rate_limiter_svc.limit_for(board.settings["post_delay"], **payload)

    topic_create_svc = request.find_service(ITopicCreateService)
    return topic_create_svc.enqueue(
        board.slug,
        form.title.data,
        form.body.data,
        request.client_addr,
        payload={
            "application_url": request.application_url,
            "referrer": request.referrer,
            "url": request.url,
            "user_agent": request.user_agent,
        },
    )


def task_get(request):
    """Retrieve a task processing status for the given task id.

    :param request: A :class:`pyramid.request.Request` object.
    """
    task_query_svc = request.find_service(ITaskQueryService)
    task_uid = request.matchdict["task"]
    result_proxy = task_query_svc.result_from_uid(task_uid)

    if result_proxy.success():
        obj = result_proxy.deserialize(request)
        if isinstance(obj, BaseError):
            raise obj

    return result_proxy


def topic_get(request):
    """Retrieve a topic info for an individual topic.

    :param request: A :class:`pyramid.request.Request` object.
    """
    topic_query_svc = request.find_service(ITopicQueryService)
    topic_id = request.matchdict["topic"]
    return topic_query_svc.topic_from_id(topic_id)


def topic_posts_get(request):
    """Retrieve all posts in a single topic or by or by search criteria.

    :param request: A :class:`pyramid.request.Request` object.
    """
    post_query_svc = request.find_service(IPostQueryService)
    topic_id = request.matchdict["topic"]
    query = None

    if "query" in request.matchdict:
        query = request.matchdict["query"]

    return post_query_svc.list_from_topic_id(topic_id, query)


def topic_posts_post(request):
    """Create a new post within topic.

    :param request: A :class:`pyramid.request.Request` object.
    """
    topic_query_svc = request.find_service(ITopicQueryService)
    topic_id = request.matchdict["topic"]

    topic = topic_query_svc.topic_from_id(topic_id)
    board = topic.board

    params = _get_params(request)
    form = PostForm(params, request=request)

    if not form.validate():
        raise ParamsInvalidError(form.errors)

    ban_query_svc = request.find_service(IBanQueryService)
    ban_scope = {"board": board.slug, "topic": topic.title}
    if ban_query_svc.is_banned(request.client_addr, scopes=ban_scope):
        raise BanRejectedError()

    banword_query_svc = request.find_service(IBanwordQueryService)
    if banword_query_svc.is_banned(form.body.data, scopes=ban_scope):
        raise BanwordRejectedError()

    rate_limiter_svc = request.find_service(IRateLimiterService)
    if rate_limiter_svc:
        payload = {"ip_address": request.client_addr, "board": board.slug}
        if rate_limiter_svc.is_limited(**payload):
            time_left = rate_limiter_svc.time_left(**payload)
            raise RateLimitedError(time_left)

        rate_limiter_svc.limit_for(board.settings["post_delay"], **payload)

    post_create_svc = request.find_service(IPostCreateService)
    return post_create_svc.enqueue(
        topic.id,
        form.body.data,
        form.bumped.data,
        request.client_addr,
        payload={
            "application_url": request.application_url,
            "referrer": request.referrer,
            "url": request.url,
            "user_agent": request.user_agent,
        },
    )


def pages_get(request):
    """Retrieve a list of all pages.

    :param request: A :class:`pyramid.request.Request` object.
    """
    page_query_svc = request.find_service(IPageQueryService)
    return page_query_svc.list_public()


def page_get(request):
    """Retrieve a page.

    :param request: A :class:`pyramid.request.Request` object.
    :param page: Page name to retrieve.
    :param namespace: Page namespace to retrieve from.
    """
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict["page"]
    return page_query_svc.public_page_from_slug(page_slug)


def error_not_found(exc, request):
    """Handle any exception that should cause the app to treat it as
    NotFound resources, such as :class:`pyramid.httpexceptions.HTTPNotFound`
    or :class:`sqlalchemy.orm.exc.NoResultFound`.

    :param exc: An :class:`Exception`.
    :param request: A :class:`pyramid.request.Request` object.
    """
    request.response.status = "404 Not Found"
    return {
        "type": "error",
        "status": "not_found",
        "message": "The resource %s %s could not be found."
        % (request.method, request.path),
    }


def error_base_handler(exc, request):
    """Handle any exception that should be rendered with the serializer.
    Normally this is any subclass of the :class:`fanboi2.errors.BaseError`.

    :param exc: A :class:`fanboi2.errors.BaseError`.
    :param request: A :class:`pyramid.request.Request` object.
    """
    request.response.status = exc.http_status
    return exc


def _api_routes_only(context, request):
    """A predicate for :meth:`pyramid.config.add_view` that returns true
    if the requested route is an API route.
    """
    return request.path.startswith("/api/")


def includeme(config):  # pragma: no cover
    config.add_route("api_root", "/")
    config.add_view(
        root, request_method="GET", route_name="api_root", renderer="api/show.mako"
    )

    #
    # Pages API
    #

    config.add_route("api_pages", "/1.0/pages/")
    config.add_route("api_page", "/1.0/pages/{page:.*}/")

    config.add_view(
        pages_get, request_method="GET", route_name="api_pages", renderer="json"
    )

    config.add_view(
        page_get, request_method="GET", route_name="api_page", renderer="json"
    )

    #
    # Boards API
    #

    config.add_route("api_boards", "/1.0/boards/")
    config.add_route("api_board", "/1.0/boards/{board}/")
    config.add_route("api_board_topics", "/1.0/boards/{board}/topics/")

    config.add_view(
        boards_get, request_method="GET", route_name="api_boards", renderer="json"
    )

    config.add_view(
        board_get, request_method="GET", route_name="api_board", renderer="json"
    )

    config.add_view(
        board_topics_get,
        request_method="GET",
        route_name="api_board_topics",
        renderer="json",
    )

    config.add_view(
        board_topics_post,
        request_method="POST",
        route_name="api_board_topics",
        renderer="json",
    )

    #
    # Task API
    #

    config.add_route("api_task", "/1.0/tasks/{task}/")

    config.add_view(
        task_get, request_method="GET", route_name="api_task", renderer="json"
    )

    #
    # Topics API
    #

    config.add_route("api_topic", "/1.0/topics/{topic:\d+}/")
    config.add_route("api_topic_posts", "/1.0/topics/{topic:\d+}/posts/")
    config.add_route("api_topic_posts_scoped", "/1.0/topics/{topic:\d+}/posts/{query}/")

    config.add_view(
        topic_get, request_method="GET", route_name="api_topic", renderer="json"
    )

    config.add_view(
        topic_posts_get,
        request_method="GET",
        route_name="api_topic_posts",
        renderer="json",
    )

    config.add_view(
        topic_posts_post,
        request_method="POST",
        route_name="api_topic_posts",
        renderer="json",
    )

    config.add_view(
        topic_posts_get,
        request_method="GET",
        route_name="api_topic_posts_scoped",
        renderer="json",
    )

    #
    # Error handling
    #

    config.add_view(
        error_base_handler,
        context=BaseError,
        renderer="json",
        custom_predicates=[_api_routes_only],
    )

    config.add_view(
        error_not_found,
        context=NoResultFound,
        renderer="json",
        custom_predicates=[_api_routes_only],
    )

    config.add_notfound_view(
        error_not_found,
        append_slash=True,
        renderer="json",
        custom_predicates=[_api_routes_only],
    )

    config.scan()
