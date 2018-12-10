import json

from pyramid.csrf import check_csrf_token
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.security import remember, forget, authenticated_userid
from sqlalchemy.orm.exc import NoResultFound
from webob.multidict import MultiDict

from ..version import __VERSION__
from ..models.board import DEFAULT_BOARD_CONFIG
from ..forms import (
    AdminBanForm,
    AdminBanwordForm,
    AdminBoardForm,
    AdminBoardNewForm,
    AdminLoginForm,
    AdminPageForm,
    AdminPublicPageForm,
    AdminPublicPageNewForm,
    AdminSettingForm,
    AdminSetupForm,
    AdminTopicForm,
    PostForm,
    TopicForm,
)
from ..interfaces import (
    IBanCreateService,
    IBanQueryService,
    IBanUpdateService,
    IBanwordCreateService,
    IBanwordQueryService,
    IBanwordUpdateService,
    IBoardCreateService,
    IBoardQueryService,
    IBoardUpdateService,
    IPageCreateService,
    IPageDeleteService,
    IPageQueryService,
    IPageUpdateService,
    IPostCreateService,
    IPostDeleteService,
    IPostQueryService,
    ISettingQueryService,
    ISettingUpdateService,
    ITopicCreateService,
    ITopicDeleteService,
    ITopicQueryService,
    ITopicUpdateService,
    IUserCreateService,
    IUserLoginService,
    IUserSessionQueryService,
)


def login_get(request):
    """Display a login form.

    :param request: A :class:`pyramid.request.Request` object.
    """
    if authenticated_userid(request):
        return HTTPFound(location=request.route_path(route_name="admin_dashboard"))

    if _setup_required(None, request):
        return HTTPFound(location=request.route_path(route_name="admin_setup"))

    return {"form": AdminLoginForm(request=request)}


def login_post(request):
    """Perform user login.

    :param request: A :class:`pyramid.request.Request` object.
    """
    check_csrf_token(request)
    if authenticated_userid(request):
        raise HTTPForbidden

    form = AdminLoginForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"form": form}

    user_login_svc = request.find_service(IUserLoginService)
    if not user_login_svc.authenticate(form.username.data, form.password.data):
        return {"form": form}

    token = user_login_svc.token_for(form.username.data, request.client_addr)
    headers = remember(request, token)
    return HTTPFound(
        headers=headers, location=request.route_path(route_name="admin_dashboard")
    )


def logout_get(request):
    """Perform user logout.

    :param request: A :class:`pyramid.request.Request` object.
    """
    userid = authenticated_userid(request)
    if userid:
        user_login_svc = request.find_service(IUserLoginService)
        user_login_svc.revoke_token(userid, request.client_addr)

    headers = forget(request)
    return HTTPFound(
        headers=headers, location=request.route_path(route_name="admin_root")
    )


def setup_get(request):
    if not _setup_required(None, request):
        raise HTTPNotFound()

    return {"form": AdminSetupForm(request=request)}


def setup_post(request):
    if not _setup_required(None, request):
        raise HTTPNotFound()

    check_csrf_token(request)
    form = AdminSetupForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"form": form}

    setting_update_svc = request.find_service(ISettingUpdateService)
    setting_update_svc.update("setup.version", __VERSION__)

    user_create_svc = request.find_service(IUserCreateService)
    user_create_svc.create(
        None, form.username.data, form.password.data, form.name.data, ["admin"]
    )

    return HTTPFound(location=request.route_path(route_name="admin_root"))


def dashboard_get(request):
    user_login_svc = request.find_service(IUserLoginService)
    user = user_login_svc.user_from_token(
        request.authenticated_userid, request.client_addr
    )

    user_session_query_svc = request.find_service(IUserSessionQueryService)
    return {
        "user": user,
        "sessions": user_session_query_svc.list_recent_from_user_id(user.id),
    }


def bans_get(request):
    ban_query_svc = request.find_service(IBanQueryService)
    return {"bans": ban_query_svc.list_active()}


def bans_inactive_get(request):
    ban_query_svc = request.find_service(IBanQueryService)
    return {"bans": ban_query_svc.list_inactive()}


def ban_new_get(request):
    return {"form": AdminBanForm(request=request)}


def ban_new_post(request):
    check_csrf_token(request)

    form = AdminBanForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"form": form}

    ban_create_svc = request.find_service(IBanCreateService)
    ban = ban_create_svc.create(
        form.ip_address.data,
        description=form.description.data,
        duration=form.duration.data,
        scope=form.scope.data,
        active=form.active.data,
    )

    # Explicitly flush so that ID is available.
    dbsession = request.find_service(name="db")
    dbsession.flush()

    return HTTPFound(location=request.route_path(route_name="admin_ban", ban=ban.id))


def ban_get(request):
    ban_query_svc = request.find_service(IBanQueryService)
    ban_id = request.matchdict["ban"]
    return {"ban": ban_query_svc.ban_from_id(ban_id)}


def ban_edit_get(request):
    ban_query_svc = request.find_service(IBanQueryService)
    ban_id = request.matchdict["ban"]
    ban = ban_query_svc.ban_from_id(ban_id)
    return {"ban": ban, "form": AdminBanForm(obj=ban, request=request)}


def ban_edit_post(request):
    check_csrf_token(request)

    ban_query_svc = request.find_service(IBanQueryService)
    ban_id = request.matchdict["ban"]
    ban = ban_query_svc.ban_from_id(ban_id)
    form = AdminBanForm(request.POST, obj=ban, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"ban": ban, "form": form}

    ban_update_svc = request.find_service(IBanUpdateService)
    ban = ban_update_svc.update(
        ban.id,
        ip_address=form.ip_address.data,
        description=form.description.data,
        duration=form.duration.data,
        scope=form.scope.data,
        active=form.active.data,
    )
    return HTTPFound(location=request.route_path(route_name="admin_ban", ban=ban.id))


def banwords_get(request):
    banword_query_svc = request.find_service(IBanwordQueryService)
    return {"banwords": banword_query_svc.list_active()}


def banwords_inactive_get(request):
    banword_query_svc = request.find_service(IBanwordQueryService)
    return {"banwords": banword_query_svc.list_inactive()}


def banword_new_get(request):
    return {"form": AdminBanwordForm(request=request)}


def banword_new_post(request):
    check_csrf_token(request)

    form = AdminBanwordForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"form": form}

    banword_create_svc = request.find_service(IBanwordCreateService)
    banword = banword_create_svc.create(
        form.expr.data, description=form.description.data, active=form.active.data
    )

    # Explicitly flush so that ID is available.
    dbsession = request.find_service(name="db")
    dbsession.flush()

    return HTTPFound(
        location=request.route_path(route_name="admin_banword", banword=banword.id)
    )


def banword_get(request):
    banword_query_svc = request.find_service(IBanwordQueryService)
    banword_id = request.matchdict["banword"]
    return {"banword": banword_query_svc.banword_from_id(banword_id)}


def banword_edit_get(request):
    banword_query_svc = request.find_service(IBanwordQueryService)
    banword_id = request.matchdict["banword"]
    banword = banword_query_svc.banword_from_id(banword_id)
    return {"banword": banword, "form": AdminBanwordForm(obj=banword, request=request)}


def banword_edit_post(request):
    check_csrf_token(request)

    banword_query_svc = request.find_service(IBanwordQueryService)
    banword_id = request.matchdict["banword"]
    banword = banword_query_svc.banword_from_id(banword_id)
    form = AdminBanwordForm(request.POST, obj=banword, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"banword": banword, "form": form}

    banword_update_svc = request.find_service(IBanwordUpdateService)
    banword = banword_update_svc.update(
        banword.id,
        expr=form.expr.data,
        description=form.description.data,
        active=form.active.data,
    )
    return HTTPFound(
        location=request.route_path(route_name="admin_banword", banword=banword.id)
    )


def boards_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    return {"boards": board_query_svc.list_all()}


def board_new_get(request):
    form = AdminBoardNewForm(request=request)
    form.settings.data = json.dumps(DEFAULT_BOARD_CONFIG, indent=4, sort_keys=True)
    return {"form": form}


def board_new_post(request):
    check_csrf_token(request)

    form = AdminBoardNewForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"form": form}

    board_create_svc = request.find_service(IBoardCreateService)
    db_settings = json.loads(form.settings.data)
    settings = DEFAULT_BOARD_CONFIG.update(db_settings)
    board = board_create_svc.create(
        form.slug.data,
        title=form.title.data,
        description=form.description.data,
        status=form.status.data,
        agreements=form.agreements.data,
        settings=settings,
    )

    return HTTPFound(
        location=request.route_path(route_name="admin_board", board=board.slug)
    )


def board_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    return {"board": board_query_svc.board_from_slug(board_slug)}


def board_edit_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)
    form = AdminBoardForm(obj=board, request=request)
    form.settings.data = json.dumps(board.settings, indent=4, sort_keys=True)
    return {"board": board, "form": form}


def board_edit_post(request):
    check_csrf_token(request)

    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    form = AdminBoardForm(request.POST, obj=board, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"board": board, "form": form}

    board_update_svc = request.find_service(IBoardUpdateService)
    board = board_update_svc.update(
        board.slug,
        title=form.title.data,
        description=form.description.data,
        status=form.status.data,
        agreements=form.agreements.data,
        settings=json.loads(form.settings.data),
    )
    return HTTPFound(
        location=request.route_path(route_name="admin_board", board=board.slug)
    )


def board_topics_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    topic_query_svc = request.find_service(ITopicQueryService)
    board_slug = request.matchdict["board"]
    return {
        "board": board_query_svc.board_from_slug(board_slug),
        "topics": topic_query_svc.list_from_board_slug(board_slug),
    }


def board_topic_new_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    user_login_svc = request.find_service(IUserLoginService)
    board_slug = request.matchdict["board"]
    return {
        "user": user_login_svc.user_from_token(
            request.authenticated_userid, request.client_addr
        ),
        "board": board_query_svc.board_from_slug(board_slug),
        "form": TopicForm(request=request),
    }


def board_topic_new_post(request):
    check_csrf_token(request)

    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    user_login_svc = request.find_service(IUserLoginService)
    user_ip_address = request.client_addr
    user = user_login_svc.user_from_token(request.authenticated_userid, user_ip_address)

    form = TopicForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"board": board, "user": user, "form": form}

    topic_create_svc = request.find_service(ITopicCreateService)
    topic = topic_create_svc.create_with_user(
        board.slug, user.id, form.title.data, form.body.data, user_ip_address
    )

    dbsession = request.find_service(name="db")
    dbsession.flush()
    return HTTPFound(
        location=request.route_path(
            route_name="admin_board_topic", board=board.slug, topic=topic.id
        )
    )


def board_topic_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    topic_query_svc = request.find_service(ITopicQueryService)
    topic_id = request.matchdict["topic"]
    topic = topic_query_svc.topic_from_id(topic_id)
    if topic.board_id != board.id:
        raise HTTPNotFound(request.path)

    post_query_svc = request.find_service(IPostQueryService)
    query = None
    if "query" in request.matchdict:
        query = request.matchdict["query"]

    posts = post_query_svc.list_from_topic_id(topic_id, query)
    if not posts:
        raise HTTPNotFound(request.path)

    user_login_svc = request.find_service(IUserLoginService)
    return {
        "board": board,
        "topic": topic,
        "posts": posts,
        "user": user_login_svc.user_from_token(
            request.authenticated_userid, request.client_addr
        ),
        "form": PostForm(request=request),
    }


def board_topic_post(request):
    check_csrf_token(request)

    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    topic_query_svc = request.find_service(ITopicQueryService)
    topic_id = request.matchdict["topic"]
    topic = topic_query_svc.topic_from_id(topic_id)
    if topic.board_id != board.id:
        raise HTTPNotFound(request.path)

    user_login_svc = request.find_service(IUserLoginService)
    user_ip_address = request.client_addr
    user = user_login_svc.user_from_token(request.authenticated_userid, user_ip_address)

    form = PostForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"board": board, "topic": topic, "user": user, "form": form}

    post_create_svc = request.find_service(IPostCreateService)
    post_create_svc.create_with_user(
        topic.id, user.id, form.body.data, form.bumped.data, user_ip_address
    )

    return HTTPFound(
        location=request.route_path(
            route_name="admin_board_topic_posts",
            board=board.slug,
            topic=topic.id,
            query="recent",
        )
    )


def board_topic_edit_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    topic_query_svc = request.find_service(ITopicQueryService)
    topic_id = request.matchdict["topic"]
    topic = topic_query_svc.topic_from_id(topic_id)
    if topic.board_id != board.id:
        raise HTTPNotFound(request.path)

    return {
        "board": board,
        "topic": topic,
        "form": AdminTopicForm(obj=topic, request=request),
    }


def board_topic_edit_post(request):
    check_csrf_token(request)

    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    topic_query_svc = request.find_service(ITopicQueryService)
    topic_id = request.matchdict["topic"]
    topic = topic_query_svc.topic_from_id(topic_id)
    if topic.board_id != board.id:
        raise HTTPNotFound(request.path)

    form = AdminTopicForm(request.POST, obj=topic, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"board": board, "topic": topic, "form": form}

    topic_update_svc = request.find_service(ITopicUpdateService)
    topic_update_svc.update(topic.id, status=form.status.data)
    return HTTPFound(
        location=request.route_path(
            route_name="admin_board_topic_posts",
            board=board.slug,
            topic=topic.id,
            query="recent",
        )
    )


def board_topic_delete_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    topic_query_svc = request.find_service(ITopicQueryService)
    topic_id = request.matchdict["topic"]
    topic = topic_query_svc.topic_from_id(topic_id)
    if topic.board_id != board.id:
        raise HTTPNotFound(request.path)

    return {"board": board, "topic": topic}


def board_topic_delete_post(request):
    check_csrf_token(request)

    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    topic_query_svc = request.find_service(ITopicQueryService)
    topic_id = request.matchdict["topic"]
    topic = topic_query_svc.topic_from_id(topic_id)
    if topic.board_id != board.id:
        raise HTTPNotFound(request.path)

    topic_delete_svc = request.find_service(ITopicDeleteService)
    topic_delete_svc.delete(topic_id)
    return HTTPFound(
        location=request.route_path(route_name="admin_board_topics", board=board.slug)
    )


def board_topic_posts_delete_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    topic_query_svc = request.find_service(ITopicQueryService)
    topic_id = request.matchdict["topic"]
    topic = topic_query_svc.topic_from_id(topic_id)
    if topic.board_id != board.id:
        raise HTTPNotFound(request.path)

    post_query_svc = request.find_service(IPostQueryService)
    query = None
    if "query" in request.matchdict:
        query = request.matchdict["query"]

    posts = post_query_svc.list_from_topic_id(topic_id, query)
    if not posts:
        raise HTTPNotFound(request.path)

    if posts[0].number == 1:
        return render_to_response(
            "admin/boards/topics/posts/delete_error.mako",
            {"board": board, "topic": topic, "posts": posts, "query": query},
            request=request,
        )

    return {"board": board, "topic": topic, "posts": posts, "query": query}


def board_topic_posts_delete_post(request):
    check_csrf_token(request)

    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict["board"]
    board = board_query_svc.board_from_slug(board_slug)

    topic_query_svc = request.find_service(ITopicQueryService)
    topic_id = request.matchdict["topic"]
    topic = topic_query_svc.topic_from_id(topic_id)
    if topic.board_id != board.id:
        raise HTTPNotFound(request.path)

    post_query_svc = request.find_service(IPostQueryService)
    query = None
    if "query" in request.matchdict:
        query = request.matchdict["query"]

    posts = post_query_svc.list_from_topic_id(topic_id, query)
    if not posts or posts[0].number == 1:
        raise HTTPNotFound(request.path)

    post_delete_svc = request.find_service(IPostDeleteService)
    for post in posts:
        post_delete_svc.delete_from_topic_id(post.topic_id, post.number)

    return HTTPFound(
        location=request.route_path(
            route_name="admin_board_topic_posts",
            board=board.slug,
            topic=topic.id,
            query="recent",
        )
    )


def pages_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    return {
        "pages": page_query_svc.list_public(),
        "pages_internal": page_query_svc.list_internal(),
    }


def page_new_get(request):
    return {"form": AdminPublicPageNewForm(request=request)}


def page_new_post(request):
    check_csrf_token(request)

    form = AdminPublicPageNewForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"form": form}

    page_create_svc = request.find_service(IPageCreateService)
    page = page_create_svc.create(
        form.slug.data, title=form.title.data, body=form.body.data
    )

    return HTTPFound(
        location=request.route_path(route_name="admin_page", page=page.slug)
    )


def page_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict["page"]
    return {"page": page_query_svc.public_page_from_slug(page_slug)}


def page_edit_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict["page"]
    page = page_query_svc.public_page_from_slug(page_slug)
    return {"page": page, "form": AdminPublicPageForm(obj=page, request=request)}


def page_edit_post(request):
    check_csrf_token(request)

    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict["page"]
    page = page_query_svc.public_page_from_slug(page_slug)
    form = AdminPublicPageForm(request.POST, obj=page, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"page": page, "form": form}

    page_update_svc = request.find_service(IPageUpdateService)
    page = page_update_svc.update(page.slug, title=form.title.data, body=form.body.data)
    return HTTPFound(
        location=request.route_path(route_name="admin_page", page=page.slug)
    )


def page_delete_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict["page"]
    return {"page": page_query_svc.public_page_from_slug(page_slug)}


def page_delete_post(request):
    check_csrf_token(request)

    page_delete_svc = request.find_service(IPageDeleteService)
    page_slug = request.matchdict["page"]
    page_delete_svc.delete(page_slug)
    return HTTPFound(location=request.route_path(route_name="admin_pages"))


def page_internal_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict["page"]

    try:
        page = page_query_svc.internal_page_from_slug(page_slug)
    except NoResultFound:
        page = None
    except ValueError:
        raise HTTPNotFound()

    return {"page_slug": page_slug, "page": page}


def page_internal_edit_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict["page"]
    try:
        page = page_query_svc.internal_page_from_slug(page_slug)
    except ValueError:
        raise HTTPNotFound()
    except NoResultFound:
        page = None

    if page:
        form = AdminPageForm(obj=page, request=request)
    else:
        form = AdminPageForm(request=request)
    return {"page_slug": page_slug, "page": page, "form": form}


def page_internal_edit_post(request):
    check_csrf_token(request)

    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict["page"]
    try:
        page = page_query_svc.internal_page_from_slug(page_slug)
    except ValueError:
        raise HTTPNotFound()
    except NoResultFound:
        page = None

    if page:
        form = AdminPageForm(request.POST, obj=page, request=request)
    else:
        form = AdminPageForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"page_slug": page_slug, "page": page, "form": form}

    if page:
        page_update_svc = request.find_service(IPageUpdateService)
        page = page_update_svc.update_internal(page.slug, body=form.body.data)
    else:
        page_create_svc = request.find_service(IPageCreateService)
        page = page_create_svc.create_internal(page_slug, body=form.body.data)
    return HTTPFound(
        location=request.route_path(route_name="admin_page_internal", page=page.slug)
    )


def page_internal_delete_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict["page"]

    try:
        page = page_query_svc.internal_page_from_slug(page_slug)
    except ValueError:
        raise HTTPNotFound()

    return {"page": page}


def page_internal_delete_post(request):
    check_csrf_token(request)

    page_delete_svc = request.find_service(IPageDeleteService)
    page_slug = request.matchdict["page"]
    page_delete_svc.delete_internal(page_slug)
    return HTTPFound(location=request.route_path(route_name="admin_pages"))


def settings_get(request):
    setting_query_svc = request.find_service(ISettingQueryService)
    return {"settings": setting_query_svc.list_all()}


def setting_get(request):
    setting_query_svc = request.find_service(ISettingQueryService)
    setting_key = request.matchdict["setting"]

    try:
        value = setting_query_svc.value_from_key(
            setting_key, use_cache=False, safe_keys=True
        )
    except KeyError:
        raise HTTPNotFound()

    form = AdminSettingForm(
        MultiDict({"value": json.dumps(value, indent=4, sort_keys=True)}),
        request=request,
    )

    return {"key": setting_key, "form": form}


def setting_post(request):
    check_csrf_token(request)

    setting_query_svc = request.find_service(ISettingQueryService)
    setting_key = request.matchdict["setting"]

    try:
        setting_query_svc.value_from_key(setting_key, use_cache=False, safe_keys=True)
    except KeyError:
        raise HTTPNotFound()

    form = AdminSettingForm(request.POST, request=request)
    if not form.validate():
        request.response.status = "400 Bad Request"
        return {"key": setting_key, "form": form}

    setting_update_svc = request.find_service(ISettingUpdateService)
    setting_update_svc.update(setting_key, json.loads(form.value.data))
    return HTTPFound(location=request.route_path(route_name="admin_settings"))


def _setup_required(context, request):
    """A predicate for :meth:`pyramid.config.add_view` that returns
    :type:`True` if an application requrie a setup or upgrade.
    """
    setting_query_svc = request.find_service(ISettingQueryService)
    return setting_query_svc.value_from_key("setup.version", use_cache=False) is None


def includeme(config):  # pragma: no cover
    config.add_route("admin_root", "/")

    config.add_view(
        login_get,
        request_method="GET",
        route_name="admin_root",
        renderer="admin/login.mako",
    )

    config.add_view(
        login_post,
        request_method="POST",
        route_name="admin_root",
        renderer="admin/login.mako",
    )

    #
    # Logout
    #

    config.add_route("admin_logout", "/logout/")

    config.add_view(logout_get, request_method="GET", route_name="admin_logout")

    #
    # Initial setup
    #

    config.add_route("admin_setup", "/setup/")

    config.add_view(
        setup_get,
        request_method="GET",
        route_name="admin_setup",
        renderer="admin/setup.mako",
        custom_predicates=[_setup_required],
    )

    config.add_view(
        setup_post,
        request_method="POST",
        route_name="admin_setup",
        renderer="admin/setup.mako",
        custom_predicates=[_setup_required],
    )

    #
    # Dashboard
    #

    config.add_route("admin_dashboard", "/dashboard/")

    config.add_view(
        dashboard_get,
        request_method="GET",
        route_name="admin_dashboard",
        renderer="admin/dashboard.mako",
        permission="manage",
    )

    #
    # Bans
    #

    config.add_route("admin_bans", "/bans/")
    config.add_route("admin_bans_inactive", "/bans/inactive/")
    config.add_route("admin_ban_new", "/bans/new/")
    config.add_route("admin_ban", "/bans/{ban:\d+}/")
    config.add_route("admin_ban_edit", "/bans/{ban:\d+}/edit/")

    config.add_view(
        bans_get,
        request_method="GET",
        route_name="admin_bans",
        renderer="admin/bans/all.mako",
        permission="manage",
    )

    config.add_view(
        bans_inactive_get,
        request_method="GET",
        route_name="admin_bans_inactive",
        renderer="admin/bans/inactive.mako",
        permission="manage",
    )

    config.add_view(
        ban_new_get,
        request_method="GET",
        route_name="admin_ban_new",
        renderer="admin/bans/new.mako",
        permission="manage",
    )

    config.add_view(
        ban_new_post,
        request_method="POST",
        route_name="admin_ban_new",
        renderer="admin/bans/new.mako",
        permission="manage",
    )

    config.add_view(
        ban_get,
        request_method="GET",
        route_name="admin_ban",
        renderer="admin/bans/show.mako",
        permission="manage",
    )

    config.add_view(
        ban_edit_get,
        request_method="GET",
        route_name="admin_ban_edit",
        renderer="admin/bans/edit.mako",
        permission="manage",
    )

    config.add_view(
        ban_edit_post,
        request_method="POST",
        route_name="admin_ban_edit",
        renderer="admin/bans/edit.mako",
        permission="manage",
    )

    #
    # Banwords
    #

    config.add_route("admin_banwords", "/banwords/")
    config.add_route("admin_banwords_inactive", "/banwords/inactive/")
    config.add_route("admin_banword_new", "/banwords/new/")
    config.add_route("admin_banword", "/banwords/{banword:\d+}/")
    config.add_route("admin_banword_edit", "/banwords/{banword:\d+}/edit/")

    config.add_view(
        banwords_get,
        request_method="GET",
        route_name="admin_banwords",
        renderer="admin/banwords/all.mako",
        permission="manage",
    )

    config.add_view(
        banwords_inactive_get,
        request_method="GET",
        route_name="admin_banwords_inactive",
        renderer="admin/banwords/inactive.mako",
        permission="manage",
    )

    config.add_view(
        banword_new_get,
        request_method="GET",
        route_name="admin_banword_new",
        renderer="admin/banwords/new.mako",
        permission="manage",
    )

    config.add_view(
        banword_new_post,
        request_method="POST",
        route_name="admin_banword_new",
        renderer="admin/banwords/new.mako",
        permission="manage",
    )

    config.add_view(
        banword_get,
        request_method="GET",
        route_name="admin_banword",
        renderer="admin/banwords/show.mako",
        permission="manage",
    )

    config.add_view(
        banword_edit_get,
        request_method="GET",
        route_name="admin_banword_edit",
        renderer="admin/banwords/edit.mako",
        permission="manage",
    )

    config.add_view(
        banword_edit_post,
        request_method="POST",
        route_name="admin_banword_edit",
        renderer="admin/banwords/edit.mako",
        permission="manage",
    )

    #
    # Boards
    #

    config.add_route("admin_boards", "/boards/")
    config.add_route("admin_board_new", "/boards/new/")
    config.add_route("admin_board", "/boards/{board}/")
    config.add_route("admin_board_edit", "/boards/{board}/edit/")
    config.add_route("admin_board_topics", "/boards/{board}/topics/")
    config.add_route("admin_board_topic_new", "/boards/{board}/topics/new/")
    config.add_route("admin_board_topic", "/boards/{board}/{topic:\d+}/")
    config.add_route("admin_board_topic_edit", "/boards/{board}/{topic:\d+}/edit/")
    config.add_route("admin_board_topic_delete", "/boards/{board}/{topic:\d+}/delete/")
    config.add_route(
        "admin_board_topic_posts_delete", "/boards/{board}/{topic:\d+}/{query}/delete/"
    )
    config.add_route("admin_board_topic_posts", "/boards/{board}/{topic:\d+}/{query}/")

    config.add_view(
        boards_get,
        request_method="GET",
        route_name="admin_boards",
        renderer="admin/boards/all.mako",
        permission="manage",
    )

    config.add_view(
        board_new_get,
        request_method="GET",
        route_name="admin_board_new",
        renderer="admin/boards/new.mako",
        permission="manage",
    )

    config.add_view(
        board_new_post,
        request_method="POST",
        route_name="admin_board_new",
        renderer="admin/boards/new.mako",
        permission="manage",
    )

    config.add_view(
        board_get,
        request_method="GET",
        route_name="admin_board",
        renderer="admin/boards/show.mako",
        permission="manage",
    )

    config.add_view(
        board_edit_get,
        request_method="GET",
        route_name="admin_board_edit",
        renderer="admin/boards/edit.mako",
        permission="manage",
    )

    config.add_view(
        board_edit_post,
        request_method="POST",
        route_name="admin_board_edit",
        renderer="admin/boards/edit.mako",
        permission="manage",
    )

    config.add_view(
        board_topics_get,
        request_method="GET",
        route_name="admin_board_topics",
        renderer="admin/boards/topics/all.mako",
        permission="manage",
    )

    config.add_view(
        board_topic_new_get,
        request_method="GET",
        route_name="admin_board_topic_new",
        renderer="admin/boards/topics/new.mako",
        permission="manage",
    )

    config.add_view(
        board_topic_new_post,
        request_method="POST",
        route_name="admin_board_topic_new",
        renderer="admin/boards/topics/new.mako",
        permission="manage",
    )

    config.add_view(
        board_topic_get,
        request_method="GET",
        route_name="admin_board_topic",
        renderer="admin/boards/topics/show.mako",
        permission="manage",
    )

    config.add_view(
        board_topic_post,
        request_method="POST",
        route_name="admin_board_topic",
        renderer="admin/boards/topics/show.mako",
        permission="manage",
    )

    config.add_view(
        board_topic_edit_get,
        request_method="GET",
        route_name="admin_board_topic_edit",
        renderer="admin/boards/topics/edit.mako",
        permission="manage",
    )

    config.add_view(
        board_topic_edit_post,
        request_method="POST",
        route_name="admin_board_topic_edit",
        renderer="admin/boards/topics/edit.mako",
        permission="manage",
    )

    config.add_view(
        board_topic_delete_get,
        request_method="GET",
        route_name="admin_board_topic_delete",
        renderer="admin/boards/topics/delete.mako",
        permission="manage",
    )

    config.add_view(
        board_topic_delete_post,
        request_method="POST",
        route_name="admin_board_topic_delete",
        permission="manage",
    )

    config.add_view(
        board_topic_posts_delete_get,
        request_method="GET",
        route_name="admin_board_topic_posts_delete",
        renderer="admin/boards/topics/posts/delete.mako",
        permission="manage",
    )

    config.add_view(
        board_topic_posts_delete_post,
        request_method="POST",
        route_name="admin_board_topic_posts_delete",
        permission="manage",
    )

    config.add_view(
        board_topic_get,
        request_method="GET",
        route_name="admin_board_topic_posts",
        renderer="admin/boards/topics/show.mako",
        permission="manage",
    )

    #
    # Pages
    #

    config.add_route("admin_pages", "/pages/")
    config.add_route("admin_page_new", "/pages/new/")
    config.add_route("admin_page_edit", "/pages/public/{page:.*}/edit/")
    config.add_route("admin_page_delete", "/pages/public/{page:.*}/delete/")
    config.add_route("admin_page", "/pages/public/{page:.*}/")
    config.add_route("admin_page_internal_edit", "/pages/internal/{page:.*}/edit/")
    config.add_route("admin_page_internal_delete", "/pages/internal/{page:.*}/delete/")
    config.add_route("admin_page_internal", "/pages/internal/{page:.*}/")

    config.add_view(
        pages_get,
        request_method="GET",
        route_name="admin_pages",
        renderer="admin/pages/all.mako",
        permission="manage",
    )

    config.add_view(
        page_new_get,
        request_method="GET",
        route_name="admin_page_new",
        renderer="admin/pages/new.mako",
        permission="manage",
    )

    config.add_view(
        page_new_post,
        request_method="POST",
        route_name="admin_page_new",
        renderer="admin/pages/new.mako",
        permission="manage",
    )

    config.add_view(
        page_get,
        request_method="GET",
        route_name="admin_page",
        renderer="admin/pages/show.mako",
        permission="manage",
    )

    config.add_view(
        page_edit_get,
        request_method="GET",
        route_name="admin_page_edit",
        renderer="admin/pages/edit.mako",
        permission="manage",
    )

    config.add_view(
        page_edit_post,
        request_method="POST",
        route_name="admin_page_edit",
        renderer="admin/pages/edit.mako",
        permission="manage",
    )

    config.add_view(
        page_delete_get,
        request_method="GET",
        route_name="admin_page_delete",
        renderer="admin/pages/delete.mako",
        permission="manage",
    )

    config.add_view(
        page_delete_post,
        request_method="POST",
        route_name="admin_page_delete",
        permission="manage",
    )

    config.add_view(
        page_internal_get,
        request_method="GET",
        route_name="admin_page_internal",
        renderer="admin/pages/show_internal.mako",
        permission="manage",
    )

    config.add_view(
        page_internal_edit_get,
        request_method="GET",
        route_name="admin_page_internal_edit",
        renderer="admin/pages/edit_internal.mako",
        permission="manage",
    )

    config.add_view(
        page_internal_edit_post,
        request_method="POST",
        route_name="admin_page_internal_edit",
        renderer="admin/pages/edit_internal.mako",
        permission="manage",
    )

    config.add_view(
        page_internal_delete_get,
        request_method="GET",
        route_name="admin_page_internal_delete",
        renderer="admin/pages/delete_internal.mako",
        permission="manage",
    )

    config.add_view(
        page_internal_delete_post,
        request_method="POST",
        route_name="admin_page_internal_delete",
        permission="manage",
    )

    #
    # Settings
    #

    config.add_route("admin_settings", "/settings/")
    config.add_route("admin_setting", "/settings/{setting}/")

    config.add_view(
        settings_get,
        request_method="GET",
        route_name="admin_settings",
        renderer="admin/settings/all.mako",
        permission="manage",
    )

    config.add_view(
        setting_get,
        request_method="GET",
        route_name="admin_setting",
        renderer="admin/settings/show.mako",
        permission="manage",
    )

    config.add_view(
        setting_post,
        request_method="POST",
        route_name="admin_setting",
        renderer="admin/settings/show.mako",
        permission="manage",
    )

    config.scan()
