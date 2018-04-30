from zope.interface import Interface


class IBoardQueryService(Interface):
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
    def is_banned(ip_address, scopes):
        pass


class ISettingQueryService(Interface):
    def value_from_key(key):
        pass

    def reload(key):
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

    def topic_from_id(topic_id):
        pass
