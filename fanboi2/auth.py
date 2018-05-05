from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.events import NewRequest
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow
from pyramid.security import authenticated_userid

from .interfaces import IUserLoginService


SESSION_TOKEN_VALIDITY = 3600
SESSION_TOKEN_REISSUE = 300


class Root(object):  # pragma: no cover
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request


def groupfinder(userid, request):
    """Resolve the given :param:`userid` (the session token) into a list of
    group names prefixed with ``g:`` to indicate group permissions.
    """
    if userid is None:
        return None
    user_login_svc = request.find_service(IUserLoginService)
    groups = user_login_svc.groups_from_token(userid, request.client_addr)
    if groups is None:
        return None
    return ['g:%s' % (g,) for g in groups]


def mark_user_seen(ev):
    userid = authenticated_userid(ev.request)
    if userid is not None:
        user_login_svc = ev.request.find_service(IUserLoginService)
        user_login_svc.mark_seen(userid, ev.request.client_addr)


def includeme(config):  # pragma: no cover
    authz_policy = ACLAuthorizationPolicy()
    authn_policy = AuthTktAuthenticationPolicy(
        config.registry.settings['auth.secret'],
        callback=groupfinder,
        timeout=SESSION_TOKEN_VALIDITY,
        reissue_time=SESSION_TOKEN_REISSUE,
        cookie_name='_auth',
        http_only=True,
        secure=config.registry.settings['server.secure'])

    config.add_subscriber(mark_user_seen, NewRequest)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_root_factory(Root)
