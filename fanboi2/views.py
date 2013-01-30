import transaction
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.exc import IntegrityError
from .forms import TopicForm, PostForm
from .models import Topic, Post, DBSession


def root_view(request):
    boards = request.context.objs
    return locals()


def board_view(request):
    board = request.context
    boards = board.__parent__.objs
    topics = board.objs
    return locals()


def new_board_view(request):
    board = request.context
    boards = board.__parent__.objs
    form = TopicForm(request.params)
    if request.method == 'POST' and form.validate():
        post = Post(body=form.body.data, ip_address=request.remote_addr)
        post.topic = Topic(board=board.obj, title=form.title.data)
        DBSession.add(post)
        return HTTPFound(location=request.resource_url(board))
    return locals()


def topic_view(request):
    topic = request.context
    board = topic.__parent__
    boards = board.__parent__.objs
    posts = topic.objs
    form = PostForm(request.params)
    if request.method == 'POST' and form.validate():
        # INSERT a post will issue subquery and may cause race condition.
        # TODO: Switch to use tm.attempts to handle this.
        # See also https://github.com/Pylons/pyramid_tm/pull/8
        max_attempts = 5
        while True:
            sp = transaction.savepoint()
            try:
                post = Post(topic=topic.obj, ip_address=request.remote_addr)
                form.populate_obj(post)
                DBSession.add(post)
                DBSession.flush()
            except IntegrityError:
                sp.rollback()
                max_attempts -= 1
                if not max_attempts:
                    raise
            else:
                return HTTPFound(location=request.resource_url(topic))
    return locals()
