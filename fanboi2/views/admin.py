from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from pyramid.csrf import check_csrf_token
from pyramid.security import remember, forget, authenticated_userid

from ..version import __VERSION__
from ..forms import AdminLoginForm, AdminSetupForm
from ..interfaces import ISettingQueryService, ISettingUpdateService
from ..interfaces import IUserCreateService, IUserLoginService


def login_get(request):
    """Display a login form.

    :param request: A :class:`pyramid.request.Request` object.
    """
    if authenticated_userid(request):
        return HTTPFound(
            location=request.route_path(route_name='admin_dashboard'))

    if _setup_required(None, request):
        return HTTPFound(
            location=request.route_path(route_name='admin_setup'))

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
        location=request.route_path(route_name='admin_dashboard'),
        headers=headers)


def logout_get(request):
    """Perform user logout.

    :param request: A :class:`pyramid.request.Request` object.
    """
    headers = forget(request)
    return HTTPFound(
        location=request.route_path(route_name='admin_root'),
        headers=headers)


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
        form.username.data,
        form.password.data,
        None)

    request.session.flash('Successfully setup initial user.', 'success')
    return HTTPFound(location=request.route_path(route_name='admin_root'))


def dashboard_get(request):
    return {}


def _setup_required(context, request):
    """A predicate for :meth:`pyramid.config.add_view` that returns
    :type:`True` if an application requrie a setup or upgrade.
    """
    setting_query_svc = request.find_service(ISettingQueryService)
    return setting_query_svc.value_from_key('setup.version') is None


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
        permission='dashboard')

    #
    # Bans
    #

    config.add_route('admin_bans', '/bans/')
    config.add_route('admin_ban', '/bans/{ban:\d+}/')

    #
    # Boards
    #

    config.add_route('admin_boards', '/boards/')
    config.add_route('admin_board', '/boards/{board}/')

    #
    # Topics
    #

    config.add_route('admin_topics', '/topics/')
    config.add_route('admin_topic', '/topics/{topic:\d+}/')

    #
    # Pages
    #

    config.add_route('admin_pages', '/pages/')
    config.add_route('admin_page', '/pages/{namespace}/{page:.*}/')

    #
    # Settings
    #

    config.add_route('admin_settings', '/settings/')
    config.add_route('admin_setting', '/settings/{setting}/')

    #
    # Users
    #

    config.add_route('admin_users', '/users/')
    config.add_route('admin_user', '/users/{user}/')

    config.scan()