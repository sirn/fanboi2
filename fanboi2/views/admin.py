import json

from pyramid.csrf import check_csrf_token
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from pyramid.security import remember, forget, authenticated_userid
from sqlalchemy.orm.exc import NoResultFound
from webob.multidict import MultiDict

from ..version import __VERSION__
from ..models.board import DEFAULT_BOARD_CONFIG
from ..forms import \
    AdminBoardForm,\
    AdminBoardNewForm,\
    AdminLoginForm,\
    AdminPageForm,\
    AdminPublicPageForm,\
    AdminPublicPageNewForm,\
    AdminRuleBanForm,\
    AdminSettingForm,\
    AdminSetupForm
from ..interfaces import \
    IBoardCreateService,\
    IBoardQueryService,\
    IBoardUpdateService,\
    IPageCreateService,\
    IPageDeleteService,\
    IPageQueryService,\
    IPageUpdateService,\
    IRuleBanCreateService,\
    IRuleBanQueryService,\
    IRuleBanUpdateService,\
    ISettingQueryService,\
    ISettingUpdateService,\
    ITopicQueryService,\
    IUserCreateService,\
    IUserLoginService


def login_get(request):
    """Display a login form.

    :param request: A :class:`pyramid.request.Request` object.
    """
    if authenticated_userid(request):
        return HTTPFound(
            location=request.route_path(
                route_name='admin_dashboard'))

    if _setup_required(None, request):
        return HTTPFound(
            location=request.route_path(
                route_name='admin_setup'))

    form = AdminLoginForm(request=request)
    return {
        'form': form
    }


def login_post(request):
    """Perform user login.

    :param request: A :class:`pyramid.request.Request` object.
    """
    check_csrf_token(request)
    if authenticated_userid(request):
        raise HTTPForbidden

    form = AdminLoginForm(request.POST, request=request)
    if not form.validate():
        request.response.status = '400 Bad Request'
        return {
            'form': form,
        }

    user_login_svc = request.find_service(IUserLoginService)
    if not user_login_svc.authenticate(form.username.data, form.password.data):
        request.session.flash('Username or password is invalid.', 'error')
        return {
            'form': form,
        }

    token = user_login_svc.token_for(form.username.data, request.client_addr)
    headers = remember(request, token)
    return HTTPFound(
        headers=headers,
        location=request.route_path(
            route_name='admin_dashboard'))


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
        headers=headers,
        location=request.route_path(
            route_name='admin_root'))


def setup_get(request):
    if not _setup_required(None, request):
        raise HTTPNotFound()

    form = AdminSetupForm(request=request)
    return {
        'form': form
    }


def setup_post(request):
    if not _setup_required(None, request):
        raise HTTPNotFound()

    check_csrf_token(request)
    form = AdminSetupForm(request.POST, request=request)
    if not form.validate():
        request.response.status = '400 Bad Request'
        return {
            'form': form,
        }

    setting_update_svc = request.find_service(ISettingUpdateService)
    setting_update_svc.update('setup.version', __VERSION__)

    user_create_svc = request.find_service(IUserCreateService)
    user_create_svc.create(
        None,
        form.username.data,
        form.password.data,
        form.name.data,
        ['admin'])

    request.session.flash('Successfully setup initial user.', 'success')
    return HTTPFound(
        location=request.route_path(
            route_name='admin_root'))


def dashboard_get(request):
    return {}


def bans_get(request):
    rule_ban_query_svc = request.find_service(IRuleBanQueryService)
    bans = rule_ban_query_svc.list_active()
    return {
        'bans': bans
    }


def bans_inactive_get(request):
    rule_ban_query_svc = request.find_service(IRuleBanQueryService)
    bans = rule_ban_query_svc.list_inactive()
    return {
        'bans': bans
    }


def ban_new_get(request):
    form = AdminRuleBanForm(request=request)
    return {
        'form': form
    }


def ban_new_post(request):
    check_csrf_token(request)

    form = AdminRuleBanForm(request.POST, request=request)
    if not form.validate():
        request.response.status = '400 Bad Request'
        return {
            'form': form,
        }

    rule_ban_create_svc = request.find_service(IRuleBanCreateService)
    rule_ban = rule_ban_create_svc.create(
        form.ip_address.data,
        description=form.description.data,
        duration=form.duration.data,
        scope=form.scope.data,
        active=form.active.data)

    # Explicitly flush so that ID is available.
    dbsession = request.find_service(name='db')
    dbsession.flush()

    return HTTPFound(
        location=request.route_path(
            route_name='admin_ban',
            ban=rule_ban.id))


def ban_get(request):
    rule_ban_query_svc = request.find_service(IRuleBanQueryService)
    rule_ban_id = request.matchdict['ban']
    rule_ban = rule_ban_query_svc.rule_ban_from_id(rule_ban_id)
    return {
        'ban': rule_ban
    }


def ban_edit_get(request):
    rule_ban_query_svc = request.find_service(IRuleBanQueryService)
    rule_ban_id = request.matchdict['ban']
    rule_ban = rule_ban_query_svc.rule_ban_from_id(rule_ban_id)
    form = AdminRuleBanForm(obj=rule_ban, request=request)
    return {
        'ban': rule_ban,
        'form': form
    }


def ban_edit_post(request):
    check_csrf_token(request)

    rule_ban_query_svc = request.find_service(IRuleBanQueryService)
    rule_ban_id = request.matchdict['ban']
    rule_ban = rule_ban_query_svc.rule_ban_from_id(rule_ban_id)
    form = AdminRuleBanForm(request.POST, obj=rule_ban, request=request)
    if not form.validate():
        request.response.status = '400 Bad Request'
        return {
            'ban': rule_ban,
            'form': form,
        }

    rule_ban_update_svc = request.find_service(IRuleBanUpdateService)
    rule_ban = rule_ban_update_svc.update(
        rule_ban.id,
        ip_address=form.ip_address.data,
        description=form.description.data,
        duration=form.duration.data,
        scope=form.scope.data,
        active=form.active.data)
    return HTTPFound(
        location=request.route_path(
            route_name='admin_ban',
            ban=rule_ban.id))


def boards_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    boards = board_query_svc.list_all()
    return {
        'boards': boards
    }


def board_new_get(request):
    form = AdminBoardNewForm(request=request)
    form.settings.data = json.dumps(
        DEFAULT_BOARD_CONFIG,
        indent=4,
        sort_keys=True)
    return {
        'form': form
    }


def board_new_post(request):
    check_csrf_token(request)

    form = AdminBoardNewForm(request.POST, request=request)
    if not form.validate():
        request.response.status = '400 Bad Request'
        return {
            'form': form
        }

    board_create_svc = request.find_service(IBoardCreateService)
    board = board_create_svc.create(
        form.slug.data,
        title=form.title.data,
        description=form.description.data,
        status=form.status.data,
        agreements=form.agreements.data,
        settings=json.loads(form.settings.data))

    return HTTPFound(
        location=request.route_path(
            route_name='admin_board',
            board=board.slug))


def board_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict['board']
    board = board_query_svc.board_from_slug(board_slug)
    return {
        'board': board,
    }


def board_edit_get(request):
    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict['board']
    board = board_query_svc.board_from_slug(board_slug)
    form = AdminBoardForm(obj=board, request=request)
    form.settings.data = json.dumps(board.settings, indent=4, sort_keys=True)
    return {
        'board': board,
        'form': form
    }


def board_edit_post(request):
    check_csrf_token(request)

    board_query_svc = request.find_service(IBoardQueryService)
    board_slug = request.matchdict['board']
    board = board_query_svc.board_from_slug(board_slug)

    form = AdminBoardForm(request.POST, obj=board, request=request)
    if not form.validate():
        request.response.status = '400 Bad Request'
        return {
            'board': board,
            'form': form
        }

    board_update_svc = request.find_service(IBoardUpdateService)
    board = board_update_svc.update(
        board.slug,
        title=form.title.data,
        description=form.description.data,
        status=form.status.data,
        agreements=form.agreements.data,
        settings=json.loads(form.settings.data))
    return HTTPFound(
        location=request.route_path(
            route_name='admin_board',
            board=board.slug))


def topics_get(request):
    topic_query_svc = request.find_service(ITopicQueryService)
    topics = topic_query_svc.list_recent()
    return {
        'topics': topics
    }


def topic_new_get(request):
    return {}


def topic_new_post(request):
    check_csrf_token(request)
    return {}


def topic_get(request):
    return {}


def topic_post(request):
    check_csrf_token(request)
    return {}


def topic_delete_post(request):
    check_csrf_token(request)
    return {}


def topic_post_get(request):
    return {}


def topic_post_delete_post(request):
    check_csrf_token(request)
    return {}


def pages_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    pages = page_query_svc.list_public()
    pages_internal = page_query_svc.list_internal()
    return {
        'pages': pages,
        'pages_internal': pages_internal,
    }


def page_new_get(request):
    form = AdminPublicPageNewForm(request=request)
    return {
        'form': form
    }


def page_new_post(request):
    check_csrf_token(request)

    form = AdminPublicPageNewForm(request.POST, request=request)
    if not form.validate():
        request.response.status = '400 Bad Request'
        return {
            'form': form
        }

    page_create_svc = request.find_service(IPageCreateService)
    page = page_create_svc.create(
        form.slug.data,
        title=form.title.data,
        body=form.body.data)

    return HTTPFound(
        location=request.route_path(
            route_name='admin_page',
            page=page.slug))


def page_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict['page']
    page = page_query_svc.public_page_from_slug(page_slug)
    return {
        'page': page
    }


def page_edit_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict['page']
    page = page_query_svc.public_page_from_slug(page_slug)
    form = AdminPublicPageForm(obj=page, request=request)
    return {
        'page': page,
        'form': form,
    }


def page_edit_post(request):
    check_csrf_token(request)

    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict['page']
    page = page_query_svc.public_page_from_slug(page_slug)
    form = AdminPublicPageForm(request.POST, obj=page, request=request)
    if not form.validate():
        request.response.status = '400 Bad Request'
        return {
            'page': page,
            'form': form
        }

    page_update_svc = request.find_service(IPageUpdateService)
    page = page_update_svc.update(
        page.slug,
        title=form.title.data,
        body=form.body.data)
    return HTTPFound(
        location=request.route_path(
            route_name='admin_page',
            page=page.slug))


def page_delete_post(request):
    check_csrf_token(request)

    page_delete_svc = request.find_service(IPageDeleteService)
    page_slug = request.matchdict['page']
    page_delete_svc.delete(page_slug)
    return HTTPFound(
        location=request.route_path(
            route_name='admin_pages'))


def page_internal_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict['page']

    try:
        page = page_query_svc.internal_page_from_slug(page_slug)
    except NoResultFound:
        page = None
    except ValueError:
        raise HTTPNotFound()

    return {
        'page_slug': page_slug,
        'page': page
    }


def page_internal_edit_get(request):
    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict['page']
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
    return {
        'page_slug': page_slug,
        'page': page,
        'form': form
    }


def page_internal_edit_post(request):
    check_csrf_token(request)

    page_query_svc = request.find_service(IPageQueryService)
    page_slug = request.matchdict['page']
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
        request.response.status = '400 Bad Request'
        return {
            'page_slug': page_slug,
            'page': page,
            'form': form
        }

    if page:
        page_update_svc = request.find_service(IPageUpdateService)
        page = page_update_svc.update_internal(
            page.slug,
            body=form.body.data)
    else:
        page_create_svc = request.find_service(IPageCreateService)
        page = page_create_svc.create_internal(
            page_slug,
            body=form.body.data)
    return HTTPFound(
        location=request.route_path(
            route_name='admin_page_internal',
            page=page.slug))


def page_internal_delete_post(request):
    check_csrf_token(request)

    page_delete_svc = request.find_service(IPageDeleteService)
    page_slug = request.matchdict['page']
    page_delete_svc.delete_internal(page_slug)
    return HTTPFound(
        location=request.route_path(
            route_name='admin_pages'))


def settings_get(request):
    setting_query_svc = request.find_service(ISettingQueryService)
    settings = setting_query_svc.list_all()
    return {
        'settings': settings,
    }


def setting_get(request):
    setting_query_svc = request.find_service(ISettingQueryService)
    setting_key = request.matchdict['setting']

    try:
        value = setting_query_svc.value_from_key(
            setting_key,
            use_cache=False,
            safe_keys=True)
    except KeyError:
        raise HTTPNotFound()

    form = AdminSettingForm(
        MultiDict({'value': json.dumps(value, indent=4, sort_keys=True)}),
        request=request)

    return {
        'key': setting_key,
        'form': form,
    }


def setting_post(request):
    check_csrf_token(request)

    setting_query_svc = request.find_service(ISettingQueryService)
    setting_key = request.matchdict['setting']

    try:
        setting_query_svc.value_from_key(
            setting_key,
            use_cache=False,
            safe_keys=True)
    except KeyError:
        raise HTTPNotFound()

    form = AdminSettingForm(request.POST, request=request)
    if not form.validate():
        request.response.status = '400 Bad Request'
        return {
            'key': setting_key,
            'form': form,
        }

    setting_update_svc = request.find_service(ISettingUpdateService)
    setting_update_svc.update(setting_key, json.loads(form.value.data))
    return HTTPFound(
        location=request.route_path(
            route_name='admin_settings'))


def _setup_required(context, request):
    """A predicate for :meth:`pyramid.config.add_view` that returns
    :type:`True` if an application requrie a setup or upgrade.
    """
    setting_query_svc = request.find_service(ISettingQueryService)
    return setting_query_svc.value_from_key(
        'setup.version',
        use_cache=False) is None


def includeme(config):  # pragma: no cover
    config.add_route('admin_root', '/')

    config.add_view(
        login_get,
        request_method='GET',
        route_name='admin_root',
        renderer='admin/login.mako')

    config.add_view(
        login_post,
        request_method='POST',
        route_name='admin_root',
        renderer='admin/login.mako')

    #
    # Logout
    #

    config.add_route('admin_logout', '/logout/')

    config.add_view(
        logout_get,
        request_method='GET',
        route_name='admin_logout')

    #
    # Initial setup
    #

    config.add_route('admin_setup', '/setup/')

    config.add_view(
        setup_get,
        request_method='GET',
        route_name='admin_setup',
        renderer='admin/setup.mako',
        custom_predicates=[_setup_required])

    config.add_view(
        setup_post,
        request_method='POST',
        route_name='admin_setup',
        renderer='admin/setup.mako',
        custom_predicates=[_setup_required])

    #
    # Dashboard
    #

    config.add_route('admin_dashboard', '/dashboard/')

    config.add_view(
        dashboard_get,
        request_method='GET',
        route_name='admin_dashboard',
        renderer='admin/dashboard.mako',
        permission='manage')

    #
    # Bans
    #

    config.add_route('admin_bans', '/bans/')
    config.add_route('admin_bans_inactive', '/bans/inactive/')
    config.add_route('admin_ban_new', '/bans/new/')
    config.add_route('admin_ban', '/bans/{ban:\d+}/')
    config.add_route('admin_ban_edit', '/bans/{ban:\d+}/edit/')

    config.add_view(
        bans_get,
        request_method='GET',
        route_name='admin_bans',
        renderer='admin/bans/all.mako',
        permission='manage')

    config.add_view(
        bans_inactive_get,
        request_method='GET',
        route_name='admin_bans_inactive',
        renderer='admin/bans/inactive.mako',
        permission='manage')

    config.add_view(
        ban_new_get,
        request_method='GET',
        route_name='admin_ban_new',
        renderer='admin/bans/new.mako',
        permission='manage')

    config.add_view(
        ban_new_post,
        request_method='POST',
        route_name='admin_ban_new',
        renderer='admin/bans/new.mako',
        permission='manage')

    config.add_view(
        ban_get,
        request_method='GET',
        route_name='admin_ban',
        renderer='admin/bans/show.mako',
        permission='manage')

    config.add_view(
        ban_edit_get,
        request_method='GET',
        route_name='admin_ban_edit',
        renderer='admin/bans/edit.mako',
        permission='manage')

    config.add_view(
        ban_edit_post,
        request_method='POST',
        route_name='admin_ban_edit',
        renderer='admin/bans/edit.mako',
        permission='manage')

    #
    # Boards
    #

    config.add_route('admin_boards', '/boards/')
    config.add_route('admin_board_new', '/boards/new/')
    config.add_route('admin_board', '/boards/{board}/')
    config.add_route('admin_board_edit', '/boards/{board}/edit/')

    config.add_view(
        boards_get,
        request_method='GET',
        route_name='admin_boards',
        renderer='admin/boards/all.mako',
        permission='manage')

    config.add_view(
        board_new_get,
        request_method='GET',
        route_name='admin_board_new',
        renderer='admin/boards/new.mako',
        permission='manage')

    config.add_view(
        board_new_post,
        request_method='POST',
        route_name='admin_board_new',
        renderer='admin/boards/new.mako',
        permission='manage')

    config.add_view(
        board_get,
        request_method='GET',
        route_name='admin_board',
        renderer='admin/boards/show.mako',
        permission='manage')

    config.add_view(
        board_edit_get,
        request_method='GET',
        route_name='admin_board_edit',
        renderer='admin/boards/edit.mako',
        permission='manage')

    config.add_view(
        board_edit_post,
        request_method='POST',
        route_name='admin_board_edit',
        renderer='admin/boards/edit.mako',
        permission='manage')

    #
    # Topics
    #

    config.add_route('admin_topics', '/topics/')
    config.add_route('admin_topic_new', '/topics/new/')
    config.add_route('admin_topic', '/topics/{topic:\d+}/')
    config.add_route('admin_topic_delete', '/topics/{topic:\d+}/delete/')
    config.add_route('admin_topic_post', '/topics/{topic:\d+}/{post:\d+}/')
    config.add_route(
        'admin_topic_post_delete',
        '/topics/{topic:\d+}/{post:\d+}/delete/')

    config.add_view(
        topics_get,
        request_method='GET',
        route_name='admin_topics',
        renderer='admin/topics/all.mako',
        permission='manage')

    config.add_view(
        topic_new_get,
        request_method='GET',
        route_name='admin_topic_new',
        renderer='admin/topics/new.mako',
        permission='manage')

    config.add_view(
        topic_new_post,
        request_method='POST',
        route_name='admin_topic_new',
        renderer='admin/topics/new.mako',
        permission='manage')

    config.add_view(
        topic_get,
        request_method='GET',
        route_name='admin_topic',
        renderer='admin/topics/show.mako',
        permission='manage')

    config.add_view(
        topic_post,
        request_method='POST',
        route_name='admin_topic',
        renderer='admin/topics/show.mako',
        permission='manage')

    config.add_view(
        topic_delete_post,
        request_method='POST',
        route_name='admin_topic_delete',
        permission='manage')

    config.add_view(
        topic_post_get,
        request_method='GET',
        route_name='admin_topic_post',
        renderer='admin/topics/post.mako',
        permission='manage')

    config.add_view(
        topic_post_delete_post,
        request_method='POST',
        route_name='admin_topic_post_delete',
        permission='manage')

    #
    # Pages
    #

    config.add_route('admin_pages', '/pages/')
    config.add_route('admin_page_new', '/pages/new/')
    config.add_route('admin_page_edit', '/pages/public/{page:.*}/edit/')
    config.add_route('admin_page_delete', '/pages/public/{page:.*}/delete/')
    config.add_route('admin_page', '/pages/public/{page:.*}/')
    config.add_route(
        'admin_page_internal_edit',
        '/pages/internal/{page:.*}/edit/')
    config.add_route(
        'admin_page_internal_delete',
        '/pages/internal/{page:.*}/delete/')
    config.add_route('admin_page_internal', '/pages/internal/{page:.*}/')

    config.add_view(
        pages_get,
        request_method='GET',
        route_name='admin_pages',
        renderer='admin/pages/all.mako',
        permission='manage')

    config.add_view(
        page_new_get,
        request_method='GET',
        route_name='admin_page_new',
        renderer='admin/pages/new.mako',
        permission='manage')

    config.add_view(
        page_new_post,
        request_method='POST',
        route_name='admin_page_new',
        renderer='admin/pages/new.mako',
        permission='manage')

    config.add_view(
        page_get,
        request_method='GET',
        route_name='admin_page',
        renderer='admin/pages/show.mako',
        permission='manage')

    config.add_view(
        page_edit_get,
        request_method='GET',
        route_name='admin_page_edit',
        renderer='admin/pages/edit.mako',
        permission='manage')

    config.add_view(
        page_edit_post,
        request_method='POST',
        route_name='admin_page_edit',
        renderer='admin/pages/edit.mako',
        permission='manage')

    config.add_view(
        page_delete_post,
        request_method='POST',
        route_name='admin_page_delete',
        permission='manage')

    config.add_view(
        page_internal_get,
        request_method='GET',
        route_name='admin_page_internal',
        renderer='admin/pages/show_internal.mako',
        permission='manage')

    config.add_view(
        page_internal_edit_get,
        request_method='GET',
        route_name='admin_page_internal_edit',
        renderer='admin/pages/edit_internal.mako',
        permission='manage')

    config.add_view(
        page_internal_edit_post,
        request_method='POST',
        route_name='admin_page_internal_edit',
        renderer='admin/pages/edit_internal.mako',
        permission='manage')

    config.add_view(
        page_internal_delete_post,
        request_method='POST',
        route_name='admin_page_internal_delete',
        permission='manage')

    #
    # Settings
    #

    config.add_route('admin_settings', '/settings/')
    config.add_route('admin_setting', '/settings/{setting}/')

    config.add_view(
        settings_get,
        request_method='GET',
        route_name='admin_settings',
        renderer='admin/settings/all.mako',
        permission='manage')

    config.add_view(
        setting_get,
        request_method='GET',
        route_name='admin_setting',
        renderer='admin/settings/show.mako',
        permission='manage')

    config.add_view(
        setting_post,
        request_method='POST',
        route_name='admin_setting',
        renderer='admin/settings/show.mako',
        permission='manage')

    config.scan()
