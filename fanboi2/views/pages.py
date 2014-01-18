from pyramid.view import view_config
from fanboi2.views.api import boards_get, board_get, board_topics_get


@view_config(route_name='root', renderer='root.mako')
def root(request):
    boards = boards_get(request)
    return locals()


@view_config(route_name='board', renderer='boards/show.mako')
def board_show(request):
    board = board_get(request)
    topics = board_topics_get(request, board=board).limit(10)
    return locals()
