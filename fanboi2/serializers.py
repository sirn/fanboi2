import datetime
import pytz
from fanboi2.helpers.formatters import format_post, format_page


def _datetime_adapter(obj, request):
    """Serialize :type:`datetime.datetime` object into a string.

    :param obj: A :class:`datetime.datetime` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: datetime.datetime
    :type request: pyramid.request.Request
    """
    settings = request.registry.settings
    assert isinstance(settings, dict)
    tz = pytz.timezone(settings['app.timezone'])
    return obj.astimezone(tz).isoformat()


def _sqlalchemy_query_adapter(obj, request):
    """Serialize SQLAlchemy query into a list.

    :param obj: An iterable SQLAlchemy's :class:`sqlalchemy.orm.Query` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: sqlalchemy.orm.Query
    :type request: pyramid.request.Request
    """
    return [item for item in obj]


def _board_serializer(obj, request):
    """Serialize :class:`fanboi2.models.Board` into a :type:`dict`.

    :param obj: A :class:`fanboi2.models.Board` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: fanboi2.models.Board
    :type request: pyramid.request.Request
    :rtype: dict
    """
    result = {
        'type': 'board',
        'id': obj.id,
        'agreements': obj.agreements,
        'description': obj.description,
        'settings': obj.settings,
        'slug': obj.slug,
        'title': obj.title,
        'path': request.route_path('api_board', board=obj.slug),
    }
    if request.params.get('topics'):
        result['topics'] = obj.topics.limit(10)
    return result


def _topic_serializer(obj, request):
    """Serialize :class:`fanboi2.models.Topic` into a :type:`dict`.

    :param obj: A :class:`fanboi2.models.Topic` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: fanboi2.models.Topic
    :type request: pyramid.request.Request
    :rtype: dict
    """
    result = {
        'type': 'topic',
        'id': obj.id,
        'board_id': obj.board_id,
        'bumped_at': obj.meta.bumped_at,
        'created_at': obj.created_at,
        'post_count': obj.meta.post_count,
        'posted_at': obj.meta.posted_at,
        'status': obj.status,
        'title': obj.title,
        'path': request.route_path('api_topic', topic=obj.id),
    }
    if request.params.get('posts'):
        result['posts'] = obj.recent_posts()
    return result


def _post_serializer(obj, request):
    """Serialize :class:`fanboi2.models.Post` into a :type:`dict`.

    :param obj: A :class:`fanboi2.models.Post` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: fanboi2.models.Post
    :type request: pyramid.request.Request
    :rtype: dict
    """
    return {
        'type': 'post',
        'id': obj.id,
        'body': obj.body,
        'body_formatted': format_post(None, request, obj),
        'bumped': obj.bumped,
        'created_at': obj.created_at,
        'ident': obj.ident,
        'name': obj.name,
        'number': obj.number,
        'topic_id': obj.topic_id,
        'path': request.route_path(
            'api_topic_posts_scoped',
            topic=obj.topic_id,
            query=obj.number,
        ),
    }


def _page_serializer(obj, request):
    """Serialize :class:`fanboi2.models.Page` into a :type:`dict`.

    :param obj: A :class:`fanboi2.models.Page` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: fanboi2.models.Page
    :type request: pyramid.request.Request
    :rtype: dict
    """
    return {
        'type': 'page',
        'id': obj.id,
        'body': obj.body,
        'body_formatted': format_page(None, request, obj),
        'formatter': obj.formatter,
        'namespace': obj.namespace,
        'slug': obj.slug,
        'title': obj.title,
        'updated_at': obj.updated_at or obj.created_at,
        'path': request.route_path(
            'api_page',
            page=obj.slug,
        ),
    }


def _result_proxy_serializer(obj, request):
    """Serialize :class:`fanboi2.tasks.ResultProxy` into a :type:`dict`.

    :param obj: A :class:`fanboi2.tasks.ResultProxy` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: fanboi2.tasks.ResultProxy
    :type request: pyramid.request.Request
    :rtype: dict
    """
    result = {
        'type': 'task',
        'id': obj.id,
        'status': obj.status.lower(),
        'path': request.route_path('api_task', task=obj.id),
    }
    if obj.success():
        result['data'] = obj.object
    return result


def _async_result_serializer(obj, request):
    """Serialize :class:`celery.result.AsyncResult` into a :type:`dict`.

    :param obj: A :class:`celery.result.AsyncResult` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: celery.result.AsyncResult
    :type request: pyramid.request.Request
    :rtype: dict
    """
    return {
        'type': 'task',
        'id': obj.id,
        'status': 'queued',
        'path': request.route_path('api_task', task=obj.id),
    }


def _base_error_serializer(obj, request):
    """Serialize :class:`fanboi2.errors.BaseError` and its subclasses
    into :type:`dict` using message and the name defined in the class.

    :param obj: A :class:`fanboi2.errors.BaseError` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: fanboi2.errors.BaseError
    :type request: pyramid.request.Request
    :rtype: dict
    """
    return {
        'type': 'error',
        'status': obj.name,
        'message': obj.message(request)
    }


def initialize_renderer():
    from celery.result import AsyncResult
    from pyramid.renderers import JSON
    from sqlalchemy.orm import Query
    from fanboi2.models import Board, Topic, Post, Page
    from fanboi2.errors import BaseError
    from fanboi2.tasks import ResultProxy
    json_renderer = JSON()
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


def includeme(config):  # pragma: no cover
    json_renderer = initialize_renderer()
    config.add_renderer('json', json_renderer)
