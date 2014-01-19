from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from fanboi2.forms import PostForm
from fanboi2.views.api import boards_get, board_get, board_topics_get, \
    topic_get, topic_posts_get


@view_config(route_name='root', renderer='root.mako')
def root(request):
    """Display a list of all boards."""
    boards = boards_get(request)
    return locals()


@view_config(route_name='board', renderer='boards/show.mako')
def board_show(request):
    """Display a single board with its related topics."""
    board = board_get(request)
    topics = board_topics_get(request).limit(10)
    return locals()


@view_config(route_name='topic', renderer='topics/show.mako')
@view_config(route_name='topic_scoped', renderer='topics/show.mako')
def topic_show(request):
    """Display a single topic with its related posts."""
    board = board_get(request)
    topic = topic_get(request)
    if not topic.board_id == board.id:
        raise HTTPNotFound
    posts = topic_posts_get(request)
    form = PostForm(request=request)
    return locals()
