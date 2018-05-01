from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow


class Root(object):
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request


def includeme(config):  # pragma: no cover
    authz_policy = ACLAuthorizationPolicy()
    authn_policy = AuthTktAuthenticationPolicy(
        config.registry.settings['auth.secret'])

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_root_factory(Root)
