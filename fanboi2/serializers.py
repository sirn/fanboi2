import datetime
from pyramid.renderers import JSON
from sqlalchemy.orm import Query
from .models import Board, Topic, Post
from .formatters import format_post


json_renderer = JSON()


def _datetime_adapter(obj, request):
    """Serialize :type:`datetime.datetime` object into a string.

    :param obj: A :class:`datetime.datetime` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: datetime.datetime
    :type request: pyramid.request.Request
    """
    return obj.isoformat()

json_renderer.add_adapter(datetime.datetime, _datetime_adapter)


def _sqlalchemy_query_adapter(obj, request):
    """Serialize SQLAlchemy query into a list.

    :param obj: An iterable SQLAlchemy's :class:`sqlalchemy.orm.Query` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: sqlalchemy.orm.Query
    :type request: pyramid.request.Request
    """
    return [item for item in obj]

json_renderer.add_adapter(Query, _sqlalchemy_query_adapter)


def board_serializer(obj, request):
    """Serialize :class:`fanboi2.models.Board` into a :type:`dict`.

    :param obj: A :class:`fanboi2.models.Board` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: fanboi2.models.Board
    :type request: pyramid.request.Request
    :rtype: dict
    """
    return {
        'id': obj.id,
        'agreements': obj.agreements,
        'description': obj.description,
        'settings': obj.settings,
        'slug': obj.slug,
        'title': obj.title,
    }

json_renderer.add_adapter(Board, board_serializer)


def topic_serializer(obj, request):
    """Serialize :class:`fanboi2.models.Topic` into a :type:`dict`.

    :param obj: A :class:`fanboi2.models.Topic` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: fanboi2.models.Topic
    :type request: pyramid.request.Request
    :rtype: dict
    """
    return {
        'id': obj.id,
        'board_id': obj.board_id,
        'bumped_at': obj.bumped_at,
        'created_at': obj.created_at,
        'post_count': obj.post_count,
        'posted_at': obj.posted_at,
        'status': obj.status,
        'title': obj.title,
    }

json_renderer.add_adapter(Topic, topic_serializer)


def post_serializer(obj, request):
    """Serialize :class:`fanboi2.models.Post` into a :type:`dict`.

    :param obj: A :class:`fanboi2.models.Post` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: fanboi2.models.Post
    :type request: pyramid.request.Request
    :rtype: dict
    """
    return {
        'id': obj.id,
        'body': obj.body,
        'body_formatted': format_post(None, request, obj),
        'bumped': obj.bumped,
        'created_at': obj.created_at,
        'ident': obj.ident,
        'name': obj.name,
        'number': obj.number,
        'topic_id': obj.topic_id,
    }

json_renderer.add_adapter(Post, post_serializer)
