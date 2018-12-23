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
    IFilterService,
    IIdentityService,
    IPageCreateService,
    IPageDeleteService,
    IPageQueryService,
    IPageUpdateService,
    IPostCreateService,
    IPostDeleteService,
    IPostQueryService,
    IRateLimiterService,
    IScopeService,
    ISettingQueryService,
    ISettingUpdateService,
    ITaskQueryService,
    ITopicCreateService,
    ITopicDeleteService,
    ITopicQueryService,
    ITopicUpdateService,
    IUserCreateService,
    IUserLoginService,
    IUserQueryService,
    IUserSessionQueryService,
)

from .ban import BanCreateService, BanQueryService, BanUpdateService
from .banword import BanwordCreateService, BanwordQueryService, BanwordUpdateService
from .board import BoardCreateService, BoardQueryService, BoardUpdateService
from .filter_ import FilterService
from .identity import IdentityService
from .page import (
    PageCreateService,
    PageDeleteService,
    PageQueryService,
    PageUpdateService,
)
from .post import PostCreateService, PostDeleteService, PostQueryService
from .rate_limiter import RateLimiterService
from .scope import ScopeService
from .setting import SettingQueryService, SettingUpdateService
from .task import TaskQueryService
from .topic import (
    TopicCreateService,
    TopicDeleteService,
    TopicQueryService,
    TopicUpdateService,
)
from .user import (
    UserCreateService,
    UserLoginService,
    UserQueryService,
    UserSessionQueryService,
)


def _make_factory(cls, *services):  # pragma: no cover
    def _factory(context, request):
        return cls(
            *(
                request.find_service(name=s)
                if isinstance(s, str)
                else request.find_service(s)
                for s in services
            )
        )

    return _factory


SERVICES = (
    (IBanCreateService, BanCreateService, "db"),
    (IBanQueryService, BanQueryService, "db", IScopeService),
    (IBanUpdateService, BanUpdateService, "db"),
    (IBanwordCreateService, BanwordCreateService, "db"),
    (IBanwordQueryService, BanwordQueryService, "db", IScopeService),
    (IBanwordUpdateService, BanwordUpdateService, "db"),
    (IBoardCreateService, BoardCreateService, "db"),
    (IBoardQueryService, BoardQueryService, "db"),
    (IBoardUpdateService, BoardUpdateService, "db"),
    (IIdentityService, IdentityService, "redis", ISettingQueryService),
    (IPageCreateService, PageCreateService, "db", "cache"),
    (IPageDeleteService, PageDeleteService, "db", "cache"),
    (IPageQueryService, PageQueryService, "db", "cache"),
    (IPageUpdateService, PageUpdateService, "db", "cache"),
    (
        IPostCreateService,
        PostCreateService,
        "db",
        IIdentityService,
        ISettingQueryService,
        IUserQueryService,
    ),
    (IPostDeleteService, PostDeleteService, "db"),
    (IPostQueryService, PostQueryService, "db"),
    (IRateLimiterService, RateLimiterService, "redis"),
    (IScopeService, ScopeService),
    (ISettingQueryService, SettingQueryService, "db", "cache"),
    (ISettingUpdateService, SettingUpdateService, "db", "cache"),
    (ITaskQueryService, TaskQueryService),
    (
        ITopicCreateService,
        TopicCreateService,
        "db",
        IIdentityService,
        ISettingQueryService,
        IUserQueryService,
    ),
    (ITopicDeleteService, TopicDeleteService, "db"),
    (ITopicQueryService, TopicQueryService, "db", IBoardQueryService),
    (ITopicUpdateService, TopicUpdateService, "db"),
    (IUserCreateService, UserCreateService, "db", IIdentityService),
    (IUserLoginService, UserLoginService, "db"),
    (IUserQueryService, UserQueryService, "db"),
    (IUserSessionQueryService, UserSessionQueryService, "db"),
)


def includeme(config):  # pragma: no cover
    def filter_factory(context, request):
        filters = request.registry["filters"]

        def service_query_fn(*a, **k):
            return request.find_service(*a, **k)

        return FilterService(filters, service_query_fn)

    config.register_service_factory(filter_factory, IFilterService)

    for interface, class_, *services in SERVICES:
        config.register_service_factory(_make_factory(class_, *services), interface)
