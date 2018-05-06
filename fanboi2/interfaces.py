from zope.interface import Interface


class IBoardQueryService(Interface):
    def list_all():
        pass

    def list_active():
        pass

    def board_from_slug(board_slug):
        pass


class IFilterService(Interface):
    def evaluate(payload={}):
        pass


class IIdentityService(Interface):
    def identity_for(**kwargs):
        pass


class IPageQueryService(Interface):
    def list_public():
        pass

    def list_internal():
        pass

    def public_page_from_slug(page_slug):
        pass

    def internal_page_from_slug(page_slug):
        pass


class IPostCreateService(Interface):
    def enqueue(topic_id, body, bumped, ip_address, payload={}):
        pass

    def create(topic_id, body, bumped, ip_address, payload={}):
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


class IRuleBanQueryService(Interface):
    def list_active():
        pass

    def list_inactive():
        pass

    def is_banned(ip_address, scopes):
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
    def enqueue(board_slug, title, body, ip_address, payload={}):
        pass

    def create(board_slug, title, body, ip_address, payload={}):
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
