import datetime
import re
from typing import Any, List

import pytz
from celery.result import AsyncResult  # type: ignore
from pyramid.config import Configurator  # type: ignore
from pyramid.renderers import JSON as JSONRenderer  # type: ignore
from pyramid.request import Request  # type: ignore
from sqlalchemy.orm import Query

from ..errors import BaseError
from ..helpers.formatters import format_page, format_post
from ..interfaces import ISettingQueryService
from ..models import Board, Page, Post, Topic
from ..tasks import ResultProxy

TRUTHY_RE = re.compile("^Y|y|T|t|[1-9]")

# See https://github.com/python/mypy/issues/731
JSON = Any


def _truthy(request: Request, key: str) -> bool:
    """Check that ``key`` in the request params is a truthy value."""
    if key not in request.params:
        return False
    val = str(request.params.get(key, "false"))
    return bool(TRUTHY_RE.match(val))


def _datetime_adapter(obj: datetime.datetime, request: Request) -> str:
    """serializea :type:`datetime.datetime` object into a string."""
    setting_query_svc = request.find_service(ISettingQueryService)
    tz = pytz.timezone(setting_query_svc.value_from_key("app.time_zone"))
    return obj.astimezone(tz).isoformat()


def _sqlalchemy_query_adapter(obj: Query, request: Request) -> List[Any]:
    """Serialize SQLAlchemy query into a list."""
    return [item for item in obj]


def _board_serializer(
    obj: Board,
    request: Request,
) -> JSON:
    """Serialize :class:`fanboi2.models.Board` into a :type:`dict`."""
    result = {
        "type": "board",
        "id": obj.id,
        "agreements": obj.agreements,
        "description": obj.description,
        "settings": obj.settings,
        "slug": obj.slug,
        "status": obj.status,
        "title": obj.title,
        "path": request.route_path("api_board", board=obj.slug),
    }
    if _truthy(request, "topics") and not _truthy(request, "board"):
        result["topics"] = obj.topics.limit(10)
    return result


def _topic_serializer(
    obj: Topic,
    request: Request,
) -> JSON:
    """Serialize :class:`fanboi2.models.Topic` into a :type:`dict`."""
    result = {
        "type": "topic",
        "id": obj.id,
        "board_id": obj.board_id,
        "bumped_at": obj.meta.bumped_at,
        "created_at": obj.created_at,
        "post_count": obj.meta.post_count,
        "posted_at": obj.meta.posted_at,
        "status": obj.status,
        "title": obj.title,
        "path": request.route_path("api_topic", topic=obj.id),
    }
    if _truthy(request, "board"):
        result["board"] = obj.board
    if _truthy(request, "posts") and not _truthy(request, "topic"):
        result["posts"] = obj.recent_posts()
    return result


def _post_serializer(
    obj: Post,
    request: Request,
) -> JSON:
    """Serialize :class:`fanboi2.models.Post` into a :type:`dict`."""
    result = {
        "type": "post",
        "id": obj.id,
        "body": obj.body,
        "body_formatted": format_post(None, request, obj),
        "bumped": obj.bumped,
        "created_at": obj.created_at,
        "ident": obj.ident,
        "ident_type": obj.ident_type,
        "name": obj.name,
        "number": obj.number,
        "topic_id": obj.topic_id,
        "path": request.route_path(
            "api_topic_posts_scoped", topic=obj.topic_id, query=obj.number
        ),
    }
    if _truthy(request, "topic"):
        result["topic"] = obj.topic
    return result


def _page_serializer(
    obj: Page,
    request: Request,
) -> JSON:
    """Serialize :class:`fanboi2.models.Page` into a :type:`dict`."""
    return {
        "type": "page",
        "id": obj.id,
        "body": obj.body,
        "body_formatted": format_page(None, request, obj),
        "formatter": obj.formatter,
        "namespace": obj.namespace,
        "slug": obj.slug,
        "title": obj.title,
        "updated_at": obj.updated_at or obj.created_at,
        "path": request.route_path("api_page", page=obj.slug),
    }


def _result_proxy_serializer(
    obj: ResultProxy,
    request: Request,
) -> JSON:
    """Serialize :class:`fanboi2.tasks.ResultProxy` into a :type:`dict`."""
    result = {
        "type": "task",
        "id": obj.id,
        "status": obj.status.lower(),
        "path": request.route_path("api_task", task=obj.id),
    }
    if obj.success():
        result["data"] = obj.deserialize(request)
    return result


def _async_result_serializer(
    obj: AsyncResult,
    request: Request,
) -> JSON:
    """Serialize :class:`celery.result.AsyncResult` into a :type:`dict`."""
    return {
        "type": "task",
        "id": obj.id,
        "status": "queued",
        "path": request.route_path("api_task", task=obj.id),
    }


def _base_error_serializer(
    obj: BaseError,
    request: Request,
) -> JSON:
    """
    Serialize :class:`fanboi2.errors.BaseError` and its subclasses
    into :type:`dict` using message and the name defined in the class.
    """
    return {"type": "error", "status": obj.name, "message": obj.message(request)}


def initialize_renderer() -> JSONRenderer:
    json_renderer = JSONRenderer()
    json_renderer.add_adapter(datetime.datetime, _datetime_adapter)
    json_renderer.add_adapter(Query, _sqlalchemy_query_adapter)
    json_renderer.add_adapter(Board, _board_serializer)
    json_renderer.add_adapter(Topic, _topic_serializer)
    json_renderer.add_adapter(Post, _post_serializer)
    json_renderer.add_adapter(Page, _page_serializer)
    json_renderer.add_adapter(ResultProxy, _result_proxy_serializer)
    json_renderer.add_adapter(AsyncResult, _async_result_serializer)
    json_renderer.add_adapter(BaseError, _base_error_serializer)
    return json_renderer


def includeme(config: Configurator):  # pragma: no cover
    json_renderer = initialize_renderer()
    config.add_renderer("json", json_renderer)
