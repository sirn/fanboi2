from pyramid.httpexceptions import HTTPFound
from fanboi2.forms import TopicForm
from fanboi2.models import Topic, Post, DBSession

def root_view(request):
    boards = request.context.objs
    return locals()


def board_view(request):
    boards = request.context.__parent__.objs
    board = request.context
    topics = request.context.objs
    return locals()


def new_board_view(request):
    boards = request.context.__parent__.objs
    board = request.context
    form = TopicForm(request.params)
    if request.method == 'POST' and form.validate():
        post = Post()
        post.body = form.body.data
        post.topic = Topic(board=board.obj, title=unicode(form.title.data))
        DBSession.add(post)
        return HTTPFound(location=request.resource_url(board))
    return locals()