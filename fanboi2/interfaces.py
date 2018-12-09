# flake8: noqa B902

from zope.interface import Interface


class IBanCreateService(Interface):
    def create(ip_address, description=None, duration=None, scope=None, active=True):
        pass


class IBanQueryService(Interface):
    def list_active():
        pass

    def list_inactive():
        pass

    def is_banned(ip_address, scopes):
        pass

    def ban_from_id(id):
        pass


class IBanUpdateService(Interface):
    def update(ban_id, **kwargs):
        pass


class IBanwordCreateService(Interface):
    def create(expr, description=None, active=True):
        pass


class IBanwordQueryService(Interface):
    def list_active():
        pass

    def list_inactive():
        pass

    def is_banned(text):
        pass

    def banword_from_id(id):
        pass


class IBanwordUpdateService(Interface):
    def update(banword_id, **kwargs):
        pass


class IBoardCreateService(Interface):
    def create(slug, title, description, status, agreements, settings):
        pass


class IBoardQueryService(Interface):
    def list_all():
        pass

    def list_active():
        pass

    def board_from_slug(board_slug):
        pass


class IBoardUpdateService(Interface):
    def update(slug, **kwargs):
        pass


class IFilterService(Interface):
    def evaluate(payload):
        pass


class IIdentityService(Interface):
    def identity_for(**kwargs):
        pass

    def identity_with_tz_for(tz, **kwargs):
        pass


class IPageCreateService(Interface):
    def create(slug, title, body):
        pass


class IPageDeleteService(Interface):
    def delete(slug):
        pass


class IPageQueryService(Interface):
    def list_public():
        pass

    def list_internal():
        pass

    def public_page_from_slug(slug):
        pass

    def internal_page_from_slug(slug):
        pass

    def internal_body_from_slug(slug):
        pass


class IPageUpdateService(Interface):
    def update(slug, **kwargs):
        pass

    def update_internal(slug, **kwargs):
        pass


class IPostCreateService(Interface):
    def enqueue(topic_id, body, bumped, ip_address):
        pass

    def create(topic_id, body, bumped, ip_address, payload):
        pass

    def create_with_user(topic_id, user_id, body, bumped, ip_address):
        pass


class IPostDeleteService(Interface):
    def delete_from_topic_id(topic_id, number):
        pass


class IPostQueryService(Interface):
    def list_from_topic_id(topic_id, query=None):
        pass

    def was_recently_seen(ip_address):
        pass


class IRateLimiterService(Interface):
    def limit_for(seconds, **kwargs):
        pass

    def is_limited(**kwargs):
        pass

    def time_left(**kwargs):
        pass


class ISettingQueryService(Interface):
    def list_all():
        pass

    def value_from_key(key, use_cache=True, safe_keys=False):
        pass

    def reload_cache(key):
        pass


class ISettingUpdateService(Interface):
    def update(key, value):
        pass


class ITaskQueryService(Interface):
    def result_from_uid(task_uid):
        pass


class ITopicCreateService(Interface):
    def enqueue(board_slug, title, body, ip_address, payload):
        pass

    def create(board_slug, title, body, ip_address):
        pass

    def create_with_user(board_slug, user_id, title, body, ip_address):
        pass


class ITopicDeleteService(Interface):
    def delete(topic_id):
        pass


class ITopicQueryService(Interface):
    def list_from_board_slug(board_slug):
        pass

    def list_recent_from_board_slug(board_slug):
        pass

    def list_recent():
        pass

    def topic_from_id(topic_id):
        pass


class ITopicUpdateService(Interface):
    def update(topic_id, **kwargs):
        pass


class IUserCreateService(Interface):
    def create(username, password, parent, groups):
        pass


class IUserLoginService(Interface):
    def authenticate(username, password):
        pass

    def user_from_token(token, ip_address):
        pass

    def groups_from_token(token, ip_address):
        pass

    def revoke_token(token, ip_address):
        pass

    def mark_seen(token, ip_address, revocation=3600):
        pass

    def token_for(username, ip_address):
        pass


class IUserQueryService(Interface):
    def user_from_id(id):
        pass


class IUserSessionQueryService(Interface):
    def list_recent_from_user_id(user_id):
        pass
