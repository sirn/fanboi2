import datetime
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config as view_config
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import or_, and_
from ..models import DBSession, Board, Topic


def json_view(**kwargs):
    """Works similar to :function:`pyramid.views.view_config` but always
    assume JSON renderer regardless of what renderer is given.
    """
    kwargs['renderer'] = 'json'
    return view_config(**kwargs)


def wrap_no_result_found(func):
    """Wrap :exception:`NoResultFound` into :exception:`HTTPNotFound`."""
    def wrapper(request):
        try:
            return func(request)
        except NoResultFound:
            raise HTTPNotFound(request.path)
    return wrapper



@view_config(request_method='GET', route_name='api_root', renderer='api.mako')
def root(request):
    """Display an API documentation view."""
    return {}


@json_view(request_method='GET', route_name='api_boards')
@wrap_no_result_found
def boards_get(request):
    """Retrieve a list of all boards.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: sqlalchemy.orm.Query
    """
    return DBSession.query(Board).order_by(Board.title)


@json_view(request_method='GET', route_name='api_board')
@wrap_no_result_found
def board_get(request):
    """Retrieve a full info of a single board.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: sqlalchemy.orm.Query
    """
    return DBSession.query(Board).\
        filter_by(slug=request.matchdict['board']).\
        one()


@json_view(request_method='GET', route_name='api_board_topics')
@wrap_no_result_found
def board_topics_get(request):
    """Retrieve all available topics within a single board.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: sqlalchemy.orm.Query
    """
    return board_get(request).topics. \
        filter(or_(Topic.status == "open",
                   and_(Topic.status != "open",
                        Topic.posted_at >= datetime.datetime.now() -
                        datetime.timedelta(days=7))))


@json_view(request_method='POST', route_name='api_board_topics')
@wrap_no_result_found
def board_topics_post(request):
    """Create a new topic."""
    pass


@json_view(request_method='GET', route_name='api_topic')
@wrap_no_result_found
def topic_get(request):
    """Retrieve a full post info for an individual topic.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: sqlalchemy.orm.Query
    """
    return DBSession.query(Topic).\
        filter_by(id=request.matchdict['topic']).\
        one()


@json_view(request_method='GET', route_name='api_topic_posts')
@json_view(request_method='GET', route_name='api_topic_posts_scoped')
@wrap_no_result_found
def topic_posts_get(request):
    """Retrieve all posts in a single topic or by or by search criteria.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: sqlalchemy.orm.Query
    """
    topic = topic_get(request)
    if 'query' in request.matchdict:
        return topic.scoped_posts(request.matchdict['query'])
    return topic.posts


@json_view(request_method='POST', route_name='api_topic_posts')
@wrap_no_result_found
def topic_posts_post(request):
    """Create a new post within topic."""
    pass
