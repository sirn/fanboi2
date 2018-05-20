from ..interfaces import \
    IBoardCreateService,\
    IBoardQueryService,\
    IBoardUpdateService,\
    IFilterService,\
    IIdentityService,\
    IPageCreateService,\
    IPageDeleteService,\
    IPageQueryService,\
    IPageUpdateService,\
    IPostCreateService,\
    IPostDeleteService,\
    IPostQueryService,\
    IRateLimiterService,\
    IRuleBanCreateService,\
    IRuleBanQueryService,\
    IRuleBanUpdateService,\
    ISettingQueryService,\
    ISettingUpdateService,\
    ITaskQueryService,\
    ITopicCreateService,\
    ITopicDeleteService,\
    ITopicQueryService,\
    ITopicUpdateService,\
    IUserCreateService,\
    IUserLoginService,\
    IUserQueryService,\
    IUserSessionQueryService

from .board import BoardCreateService, BoardQueryService
from .board import BoardUpdateService
from .filter_ import FilterService
from .identity import IdentityService
from .page import PageCreateService, PageDeleteService
from .page import PageQueryService, PageUpdateService
from .post import PostCreateService, PostDeleteService
from .post import PostQueryService
from .rate_limiter import RateLimiterService
from .rule import RuleBanCreateService, RuleBanQueryService
from .rule import RuleBanUpdateService
from .setting import SettingQueryService, SettingUpdateService
from .task import TaskQueryService
from .topic import TopicCreateService, TopicDeleteService
from .topic import TopicQueryService, TopicUpdateService
from .user import UserCreateService, UserLoginService
from .user import UserQueryService, UserSessionQueryService


def includeme(config):  # pragma: no cover

    # Board Create

    def board_create_factory(context, request):
        dbsession = request.find_service(name='db')
        return BoardCreateService(dbsession)

    config.register_service_factory(
        board_create_factory,
        IBoardCreateService)

    # Board Query

    def board_query_factory(context, request):
        dbsession = request.find_service(name='db')
        return BoardQueryService(dbsession)

    config.register_service_factory(
        board_query_factory,
        IBoardQueryService)

    # Board Update

    def board_update_factory(context, request):
        dbsession = request.find_service(name='db')
        return BoardUpdateService(dbsession)

    config.register_service_factory(
        board_update_factory,
        IBoardUpdateService)

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

    # Page Create

    def page_create_factory(context, request):
        dbsession = request.find_service(name='db')
        cache_region = request.find_service(name='cache')
        return PageCreateService(dbsession, cache_region)

    config.register_service_factory(
        page_create_factory,
        IPageCreateService)

    # Page Delete

    def page_delete_factory(context, request):
        dbsession = request.find_service(name='db')
        cache_region = request.find_service(name='cache')
        return PageDeleteService(dbsession, cache_region)

    config.register_service_factory(
        page_delete_factory,
        IPageDeleteService)

    # Page Query

    def page_query_factory(context, request):
        dbsession = request.find_service(name='db')
        cache_region = request.find_service(name='cache')
        return PageQueryService(dbsession, cache_region)

    config.register_service_factory(
        page_query_factory,
        IPageQueryService)

    # Page Update

    def page_update_factory(context, request):
        dbsession = request.find_service(name='db')
        cache_region = request.find_service(name='cache')
        return PageUpdateService(dbsession, cache_region)

    config.register_service_factory(
        page_update_factory,
        IPageUpdateService)

    # Post Create

    def post_create_factory(context, request):
        dbsession = request.find_service(name='db')
        identity_svc = request.find_service(IIdentityService)
        setting_query_svc = request.find_service(ISettingQueryService)
        user_query_svc = request.find_service(IUserQueryService)
        return PostCreateService(
            dbsession,
            identity_svc,
            setting_query_svc,
            user_query_svc)

    config.register_service_factory(
        post_create_factory,
        IPostCreateService)

    # Post Delete

    def post_delete_factory(context, request):
        dbsession = request.find_service(name='db')
        return PostDeleteService(dbsession)

    config.register_service_factory(
        post_delete_factory,
        IPostDeleteService)

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

    # RuleBan create

    def rule_ban_create_factory(context, request):
        dbsession = request.find_service(name='db')
        return RuleBanCreateService(dbsession)

    config.register_service_factory(
        rule_ban_create_factory,
        IRuleBanCreateService)

    # RuleBan query

    def rule_ban_query_factory(context, request):
        dbsession = request.find_service(name='db')
        return RuleBanQueryService(dbsession)

    config.register_service_factory(
        rule_ban_query_factory,
        IRuleBanQueryService)

    # RuleBan update

    def rule_ban_update_factory(context, request):
        dbsession = request.find_service(name='db')
        return RuleBanUpdateService(dbsession)

    config.register_service_factory(
        rule_ban_update_factory,
        IRuleBanUpdateService)

    # Setting Query

    def setting_query_factory(context, request):
        dbsession = request.find_service(name='db')
        cache_region = request.find_service(name='cache')
        return SettingQueryService(dbsession, cache_region)

    config.register_service_factory(
        setting_query_factory,
        ISettingQueryService)

    # Setting Update

    def setting_update_factory(context, request):
        dbsession = request.find_service(name='db')
        cache_region = request.find_service(name='cache')
        return SettingUpdateService(dbsession, cache_region)

    config.register_service_factory(
        setting_update_factory,
        ISettingUpdateService)

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
        user_query_svc = request.find_service(IUserQueryService)
        return TopicCreateService(
            dbsession,
            identity_svc,
            setting_query_svc,
            user_query_svc)

    config.register_service_factory(
        topic_create_factory,
        ITopicCreateService)

    # Topic Delete

    def topic_delete_factory(context, request):
        dbsession = request.find_service(name='db')
        return TopicDeleteService(dbsession)

    config.register_service_factory(
        topic_delete_factory,
        ITopicDeleteService)

    # Topic Query

    def topic_query_factory(context, request):
        dbsession = request.find_service(name='db')
        return TopicQueryService(dbsession)

    config.register_service_factory(
        topic_query_factory,
        ITopicQueryService)

    # Topic Update

    def topic_update_factory(context, request):
        dbsession = request.find_service(name='db')
        return TopicUpdateService(dbsession)

    config.register_service_factory(
        topic_update_factory,
        ITopicUpdateService)

    # User create

    def user_create_factory(context, request):
        dbsession = request.find_service(name='db')
        identity_svc = request.find_service(IIdentityService)
        return UserCreateService(dbsession, identity_svc)

    config.register_service_factory(
        user_create_factory,
        IUserCreateService)

    # User Login

    def user_login_factory(context, request):
        dbsession = request.find_service(name='db')
        return UserLoginService(dbsession)

    config.register_service_factory(
        user_login_factory,
        IUserLoginService)

    # User Query

    def user_query_factory(context, request):
        dbsession = request.find_service(name='db')
        return UserQueryService(dbsession)

    config.register_service_factory(
        user_query_factory,
        IUserQueryService)

    # User Query

    def user_session_query_factory(context, request):
        dbsession = request.find_service(name='db')
        return UserSessionQueryService(dbsession)

    config.register_service_factory(
        user_session_query_factory,
        IUserSessionQueryService)
