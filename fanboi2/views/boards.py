from pyramid.csrf import check_csrf_token, BadCSRFToken
from pyramid.httpexceptions import HTTPNotFound, HTTPFound, HTTPForbidden
from pyramid.renderers import render_to_response
from sqlalchemy.orm.exc import NoResultFound

from ..errors import BaseError
from ..forms import PostForm, TopicForm
from ..interfaces import (
    IBanQueryService,
    IBanwordQueryService,
    IBoardQueryService,
    IPostCreateService,
    IPostQueryService,
    IRateLimiterService,
    ITaskQueryService,
    ITopicCreateService,
    ITopicQueryService,
)


def root(request):
    """Display a list of all boards.

    :param request: A :class:`pyramid.request.Request` object.
    """
    board_query_svc = request.find_service(IBoardQueryService)
    return {"boards": board_query_svc.list_active()}


def board_show(request):
    """Display a single board with its related topics.

    :param request: A :class:`pyramid.request.Request` object.
    """
    board_query_svc = request.find_service(IBoardQueryService)
    topic_query_svc = request.find_service(ITopicQueryService)
    board_slug = request.matchdict["board"]
    return {
        "board": board_query_svc.board_from_slug(board_slug),
        "topics": topic_query_svc.list_recent_from_board_slug(board_slug),
    }


def board_all(request):
    """Display a single board with a list of all its topic.

    :param request: A :class:`pyramid.request.Request` object.
    """
    board_query_svc = request.find_service(IBoardQueryService)
    topic_query_svc = request.find_service(ITopicQueryService)
    board_slug = request.matchdict["board"]
    return {
        "board": board_query_svc.board_from_slug(board_slug),
        "topics": topic_query_svc.list_from_board_slug(board_slug),
    }


def board_new_get(request):
    """Display a form for creating new topic in a board. If a `task` query
    string is given, the function will try to retrieve and process that task
    in board context instead.

    :param request: A :class:`pyramid.request.Request` object.
    """
    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    if board.status != "open":
        raise HTTPForbidden

    if request.GET.get("task"):
        task_query_svc = request.find_service(ITaskQueryService)
        task_uid = request.GET["task"]
        result_proxy = task_query_svc.result_from_uid(task_uid)

        if result_proxy.success():
            obj = result_proxy.deserialize(request)
            if isinstance(obj, BaseError):
                extra_locals = {}
                if hasattr(obj, "status"):
                    extra_locals["status"] = obj.status

                response = render_to_response(
                    "boards/new_error.mako",
                    {"board": board, "name": obj.name, **extra_locals},
                    request=request,
                )
                response.status = obj.http_status
                return response

            return HTTPFound(
                location=request.route_path(
                    route_name="topic", board=board.slug, topic=obj.id
                )
            )

        return render_to_response(
            "boards/new_wait.mako", {"board": board}, request=request
        )

    form = TopicForm(request=request)
    return {"board": board, "form": form}


def board_new_post(request):
    """Handle form posting for creating new topic in a board.

    :param request: A :class:`pyramid.request.Request` object.
    """
    check_csrf_token(request)

    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    form = TopicForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"board": board, "form": form}

    ban_query_svc = request.find_service(IBanQueryService)
    if ban_query_svc.is_banned(request.client_addr, scopes={"board": board.slug}):
        response = render_to_response(
            "boards/new_error.mako",
            {"board": board, "name": "ban_rejected"},
            request=request,
        )
        response.status = "403 Forbidden"
        return response

    banword_query_svc = request.find_service(IBanwordQueryService)
    if banword_query_svc.is_banned(form.body.data):
        response = render_to_response(
            "boards/new_error.mako",
            {"board": board, "name": "banword_rejected"},
            request=request,
        )
        response.status = "403 Forbidden"
        return response

    rate_limiter_svc = request.find_service(IRateLimiterService)
    if rate_limiter_svc:
        payload = {"ip_address": request.client_addr, "board": board.slug}
        if rate_limiter_svc.is_limited(**payload):
            response = render_to_response(
                "boards/new_error.mako",
                {
                    "board": board,
                    "name": "rate_limited",
                    "time_left": rate_limiter_svc.time_left(**payload),
                },
                request=request,
            )
            response.status = "429 Too Many Requests"
            return response

        rate_limiter_svc.limit_for(board.settings["post_delay"], **payload)

    topic_create_svc = request.find_service(ITopicCreateService)
    task = topic_create_svc.enqueue(
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

    return HTTPFound(
        location=request.route_path(
            route_name="board_new", board=board.slug, _query={"task": task.id}
        )
    )


def topic_show_get(request):
    """Display a single topic with its related posts. If a `task` query string
    is given, the function will try to retrieve and process that task in topic
    context instead.

    :param request: A :class:`pyramid.request.Request` object.
    """
    board_query_svc = request.find_service(IBoardQueryService)
    topic_query_svc = request.find_service(ITopicQueryService)
    board_slug = request.matchdict["board"]
    topic_id = request.matchdict["topic"]

    board = board_query_svc.board_from_slug(board_slug)
    topic = topic_query_svc.topic_from_id(topic_id)

    query = None
    if "query" in request.matchdict:
        query = request.matchdict["query"]

    if topic.board_id != board.id:
        if query:
            return HTTPFound(
                location=request.route_path(
                    route_name="topic_scoped",
                    board=topic.board.slug,
                    topic=topic.id,
                    query=query,
                )
            )
        else:
            return HTTPFound(
                location=request.route_path(
                    route_name="topic", board=topic.board.slug, topic=topic.id
                )
            )

    if request.GET.get("task"):
        task_query_svc = request.find_service(ITaskQueryService)
        task_uid = request.GET["task"]
        result_proxy = task_query_svc.result_from_uid(task_uid)

        if result_proxy.success():
            obj = result_proxy.deserialize(request)
            if isinstance(obj, BaseError):
                extra_locals = {}
                if hasattr(obj, "status"):
                    extra_locals["status"] = obj.status

                response = render_to_response(
                    "topics/show_error.mako",
                    {"board": board, "topic": topic, "name": obj.name, **extra_locals},
                    request=request,
                )
                response.status = obj.http_status
                return response

            return HTTPFound(
                location=request.route_path(
                    route_name="topic_scoped",
                    board=board.slug,
                    topic=topic.id,
                    query="l10",
                )
            )

        return render_to_response(
            "topics/show_wait.mako",
            {"request": request, "board": board, "topic": topic},
            request=request,
        )

    post_query_svc = request.find_service(IPostQueryService)
    posts = post_query_svc.list_from_topic_id(topic_id, query)
    if not posts:
        raise HTTPNotFound(request.path)

    form = PostForm(request=request)
    return {"board": board, "form": form, "posts": posts, "topic": topic}


def topic_show_post(request):
    """Handle form posting for replying to a topic.

    :param request: A :class:`pyramid.request.Request` object.
    """
    check_csrf_token(request)

    board_query_svc = request.find_service(IBoardQueryService)
    topic_query_svc = request.find_service(ITopicQueryService)
    board_slug = request.matchdict["board"]
    topic_id = request.matchdict["topic"]

    board = board_query_svc.board_from_slug(board_slug)
    topic = topic_query_svc.topic_from_id(topic_id)

    if topic.board_id != board.id:
        raise HTTPNotFound(request.path)

    post_create_svc = request.find_service(IPostCreateService)
    form = PostForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"board": board, "topic": topic, "form": form}

    ban_query_svc = request.find_service(IBanQueryService)
    if ban_query_svc.is_banned(
        request.client_addr, scopes={"board": board.slug, "topic": topic.title}
    ):
        response = render_to_response(
            "topics/show_error.mako",
            {"board": board, "topic": topic, "name": "ban_rejected"},
            request=request,
        )
        response.status = "403 Forbidden"
        return response

    banword_query_svc = request.find_service(IBanwordQueryService)
    if banword_query_svc.is_banned(form.body.data):
        response = render_to_response(
            "topics/show_error.mako",
            {"board": board, "topic": topic, "name": "banword_rejected"},
            request=request,
        )
        response.status = "403 Forbidden"
        return response

    rate_limiter_svc = request.find_service(IRateLimiterService)
    if rate_limiter_svc:
        payload = {"ip_address": request.client_addr, "board": board.slug}
        if rate_limiter_svc.is_limited(**payload):
            response = render_to_response(
                "topics/show_error.mako",
                {
                    "board": board,
                    "topic": topic,
                    "name": "rate_limited",
                    "time_left": rate_limiter_svc.time_left(**payload),
                },
                request=request,
            )
            response.status = "429 Too Many Requests"
            return response

        rate_limiter_svc.limit_for(board.settings["post_delay"], **payload)

    post_create_svc = request.find_service(IPostCreateService)
    task = post_create_svc.enqueue(
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

    return HTTPFound(
        location=request.route_path(
            route_name="topic",
            board=topic.board.slug,
            topic=topic.id,
            _query={"task": task.id},
        )
    )


def error_not_found(exc, request):
    """Handle any exception that should cause the app to treat it as
    NotFound resources, such as :class:`pyramid.httpexceptions.HTTPNotFound`
    or :class:`sqlalchemy.orm.exc.NoResultFound`.

    :param exc: An :class:`Exception`.
    :param request: A :class:`pyramid.request.Request` object.
    """
    response = render_to_response("not_found.mako", {}, request=request)
    response.status = "404 Not Found"
    return response


def error_bad_request(exc, request):
    """Handle any exception that should cause the app to treat it as
    BadRequest resources, such as invalid CSRF token.

    :param exc: An :class:`Exception`.
    :param request: A :class:`pyramid.request.Request` object.
    """
    response = render_to_response("bad_request.mako", {}, request=request)
    response.status = "400 Bad Request"
    return response


def includeme(config):  # pragma: no cover
    config.add_route("root", "/")

    config.add_view(root, request_method="GET", route_name="root", renderer="root.mako")

    #
    # Board
    #

    config.add_route("board", "/{board}/")
    config.add_route("board_all", "/{board}/all/")
    config.add_route("board_new", "/{board}/new/")

    config.add_view(
        board_show,
        request_method="GET",
        route_name="board",
        renderer="boards/show.mako",
    )

    config.add_view(
        board_all,
        request_method="GET",
        route_name="board_all",
        renderer="boards/all.mako",
    )

    config.add_view(
        board_new_get,
        request_method="GET",
        route_name="board_new",
        renderer="boards/new.mako",
    )

    config.add_view(
        board_new_post,
        request_method="POST",
        route_name="board_new",
        renderer="boards/new.mako",
    )

    #
    # Topics
    #

    config.add_route("topic", "/{board:\w+}/{topic:\d+}/")
    config.add_route("topic_scoped", "/{board:\w+}/{topic:\d+}/{query}/")

    config.add_view(
        topic_show_get,
        request_method="GET",
        route_name="topic",
        renderer="topics/show.mako",
    )

    config.add_view(
        topic_show_post,
        request_method="POST",
        route_name="topic",
        renderer="topics/show.mako",
    )

    config.add_view(
        topic_show_get,
        request_method="GET",
        route_name="topic_scoped",
        renderer="topics/show.mako",
    )

    #
    # Error handling
    #

    config.add_view(error_bad_request, context=BadCSRFToken)
    config.add_view(error_not_found, context=NoResultFound)
    config.add_notfound_view(error_not_found, append_slash=True)

    config.scan()
