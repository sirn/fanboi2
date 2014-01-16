import datetime
from pyramid.view import view_config as _view_config
from sqlalchemy.sql import or_, and_
from ..models import DBSession, Board, Topic


def json_view(**kwargs):
    kwargs['renderer'] = 'json'
    return _view_config(**kwargs)


@json_view(request_method='GET', route_name='api_boards')
def boards_get(request):
    """Retrieve a list of all boards."""
    return DBSession.query(Board).order_by(Board.title).all()


@json_view(request_method='GET', route_name='api_board')
def board_get(request):
    """Retrieve a full info of a single board."""
    return DBSession.query(Board).filter_by(
        slug=request.matchdict['board']
    ).one()


@json_view(request_method='GET', route_name='api_board_topics')
def board_topics_get(request):
    """Retrieve all available topics within a single board."""
    return board_get(request).topics. \
        filter(or_(Topic.status == "open",
                   and_(Topic.status != "open",
                        Topic.posted_at >= datetime.datetime.now() -
                        datetime.timedelta(days=7)))).all()


@json_view(request_method='POST', route_name='api_board_topics')
def board_topics_post(request):
    """Create a new topic."""
    pass


@json_view(request_method='GET', route_name='api_topic')
def topic_get(request):
    """Retrieve a full post info for an individual topic."""
    return DBSession.query(Topic).get(request.matchdict['topic'])


@json_view(request_method='GET', route_name='api_topic_posts')
def topic_posts_get(request):
    """Retrieve all posts in a single topic."""
    return topic_get(request).posts


@json_view(request_method='POST', route_name='api_topic_posts')
def topic_posts_post(request):
    """Create a new post within topic."""
    pass


@json_view(request_method='GET', route_name='api_topic_posts_scoped')
def topic_posts_scoped_get(request):
    """Retrieve all posts in a single topic matching criteria."""
    return topic_get(request).scoped_posts(request.matchdict['query'])
