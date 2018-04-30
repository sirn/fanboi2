from ..interfaces import \
    IBoardQueryService,\
    IFilterService,\
    IIdentityService,\
    IPageQueryService,\
    IPostCreateService,\
    IPostQueryService,\
    IRateLimiterService,\
    IRuleBanQueryService, \
    ISettingQueryService,\
    ITaskQueryService,\
    ITopicCreateService,\
    ITopicQueryService

from .board import BoardQueryService
from .filter_ import FilterService
from .identity import IdentityService
from .page import PageQueryService
from .post import PostCreateService, PostQueryService
from .rate_limiter import RateLimiterService
from .rule import RuleBanQueryService
from .setting import SettingQueryService
from .task import TaskQueryService
from .topic import TopicCreateService, TopicQueryService


def includeme(config):  # pragma: no cover

    # Board Query

    def board_query_factory(context, request):
        dbsession = request.find_service(name='db')
        return BoardQueryService(dbsession)

    config.register_service_factory(
        board_query_factory,
        IBoardQueryService)

    # Filter

    def filter_factory(context, request):
        filters = request.registry['filters']

        def service_query_fn(*a, **k):
            return request.find_service(*a, **k)

        return FilterService(filters, service_query_fn)

    config.register_service_factory(
        filter_factory,
        IFilterService)

    # Identity

    def identity_factory(context, request):
        redis_conn = request.find_service(name='redis')
        setting_query_svc = request.find_service(ISettingQueryService)
        ident_size = setting_query_svc.value_from_key('app.ident_size')
        return IdentityService(redis_conn, ident_size)

    config.register_service_factory(
        identity_factory,
        IIdentityService)

    # Page Query

    def page_query_factory(context, request):
        dbsession = request.find_service(name='db')
        return PageQueryService(dbsession)

    config.register_service_factory(
        page_query_factory,
        IPageQueryService)

    # Post Create

    def post_create_factory(context, request):
        dbsession = request.find_service(name='db')
        identity_svc = request.find_service(IIdentityService)
        setting_query_svc = request.find_service(ISettingQueryService)
        return PostCreateService(dbsession, identity_svc, setting_query_svc)

    config.register_service_factory(
        post_create_factory,
        IPostCreateService)

    # Post Query

    def post_query_factory(context, request):
        dbsession = request.find_service(name='db')
        return PostQueryService(dbsession)

    config.register_service_factory(
        post_query_factory,
        IPostQueryService)

    # Rate Limiter

    def rate_limiter_factory(context, request):
        redis_conn = request.find_service(name='redis')
        return RateLimiterService(redis_conn)

    config.register_service_factory(
        rate_limiter_factory,
        IRateLimiterService)

    # RuleBan query

    def rule_ban_query_factory(context, request):
        dbsession = request.find_service(name='db')
        return RuleBanQueryService(dbsession)

    config.register_service_factory(
        rule_ban_query_factory,
        IRuleBanQueryService)

    # Setting Query

    def setting_query_factory(context, request):
        dbsession = request.find_service(name='db')
        cache_region = request.find_service(name='cache')
        return SettingQueryService(dbsession, cache_region)

    config.register_service_factory(
        setting_query_factory,
        ISettingQueryService)

    # Task Query

    def task_query_factory(context, request):
        return TaskQueryService()

    config.register_service_factory(
        task_query_factory,
        ITaskQueryService)

    # Topic Create

    def topic_create_factory(context, request):
        dbsession = request.find_service(name='db')
        identity_svc = request.find_service(IIdentityService)
        setting_query_svc = request.find_service(ISettingQueryService)
        return TopicCreateService(dbsession, identity_svc, setting_query_svc)

    config.register_service_factory(
        topic_create_factory,
        ITopicCreateService)

    # Topic Query

    def topic_query_factory(context, request):
        dbsession = request.find_service(name='db')
        return TopicQueryService(dbsession)

    config.register_service_factory(
        topic_query_factory,
        ITopicQueryService)
