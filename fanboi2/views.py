import transaction
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from sqlalchemy.exc import IntegrityError
from .forms import TopicForm, PostForm
from .interfaces import IBoardResource, ITopicResource
from .models import Topic, Post, DBSession


@view_config(context='.resources.RootFactory', renderer='root.jinja2')
def root_view(request):
    boards = request.context.objs
    return locals()


@view_config(context=IBoardResource, renderer='boards/show.jinja2')
def board_view(request):
    board = request.context
    boards = request.context.boards
    topics = board.objs
    return locals()


@view_config(context=IBoardResource, renderer='boards/all.jinja2', name='all')
def all_board_view(request):
    board = request.context
    boards = request.context.boards
    topics = board.objs_all
    return locals()


@view_config(context=IBoardResource, renderer='boards/new.jinja2', name='new')
def new_board_view(request):
    board = request.context
    boards = request.context.boards
    form = TopicForm(request.params, request=request)
    if request.method == 'POST' and form.validate():
        post = Post(body=form.body.data, ip_address=request.remote_addr)
        post.topic = Topic(board=board.obj, title=form.title.data)
        DBSession.add(post)
        return HTTPFound(location=request.resource_path(board))
    return locals()


@view_config(context=ITopicResource, renderer='topics/show.jinja2')
def topic_view(request):
    topic = request.context
    board = request.context.board
    boards = request.context.boards
    posts = topic.objs
    form = PostForm(request.params, request=request)
    if request.method == 'POST' and form.validate():
        # INSERT a post will issue a SELECT subquery and may cause race
        # condition. In such case, our UNIQUE constraint on (topic, number)
        # will cause the driver to raise IntegrityError.
        max_attempts = 5
        while True:
            # Prevent posting to locked topic. It is handled here inside
            # retry to ensure post don't get through even the topic is locked
            # by another process while this retry is still running.
            #
            # Expire statement ensure status is reloaded on every retry.
            DBSession.expire(topic.obj, ['status'])
            if topic.obj.status != "open":
                return render_to_response('topics/error.jinja2',
                                          locals(),
                                          request=request)

            # Using SAVEPOINT to handle ROLLBACK in case of constraint error
            # so we don't have to abort transaction. zope.transaction will
            # handle transaction COMMIT (or ABORT) at the end of request.
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
                link = "%s-" % ((post.number - 4) if post.number > 4 else 1)
                return HTTPFound(location=request.resource_path(topic, link))
    return locals()
