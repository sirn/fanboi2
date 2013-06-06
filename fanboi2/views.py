import transaction
from datetime import timedelta, datetime
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import undefer
from sqlalchemy.orm.exc import NoResultFound
from .forms import TopicForm, PostForm
from .models import Topic, Post, Board, DBSession


class BaseView(object):

    def __init__(self, request):
        self.request = request
        self.boards = DBSession.query(Board).order_by(Board.title).all()
        self._board = None
        self._topic = None

    def __call__(self):
        """Dispatch request into dispatcher with the same name as HTTP
        method. For example, a HTTP GET request will be dispatched to
        :meth:`self.GET` or HTTP POST to :meth:`self.POST`. If a dispatcher
        does not exist then :exception:`NotImplementedError` is raise.
        """
        dispatcher = self.request.method
        if hasattr(self, dispatcher):
            return getattr(self, self.request.method)()
        raise NotImplementedError

    @property
    def board(self):
        if not self._board and 'board' in self.request.matchdict:
            # We already loaded all board data, no need to query it again.
            s = str(self.request.matchdict['board'])
            self._board = next((b for b in self.boards if b.slug == s), None)
            if self._board is None:
                raise HTTPNotFound
        return self._board

    @property
    def topic(self):
        if not self._topic and 'topic' in self.request.matchdict:
            if self.board:
                try:
                    tid = int(self.request.matchdict['topic'])
                    self._topic = self.board.topics.filter_by(id=tid).one()
                except NoResultFound:
                    raise HTTPNotFound
        return self._topic


class RootView(BaseView):
    """List all boards."""

    def GET(self):
        return {'boards': self.boards}


class BoardView(BaseView):
    """Display board and all 10 recent posts regardless of its status."""

    def GET(self):
        topics = self.board.topics.limit(10).options(undefer('post_count'),
                                                     undefer('posted_at'))
        return {
            'boards': self.boards,
            'board': self.board,
            'topics': topics,
        }


class BoardAllView(BaseView):
    """Display board and all posts that are active or archived within the
    last week.
    """

    def GET(self):
        topics = self.board.topics.options(undefer('post_count'),
                                           undefer('posted_at')).\
            filter(or_(Topic.status == "open",
                       and_(Topic.status != "open",
                            Topic.posted_at >= datetime.now() - \
                                               timedelta(days=7))))
        return {
            'boards': self.boards,
            'board': self.board,
            'topics': topics,
        }


class BoardNewView(BaseView):
    """Display and handle creation of new topic."""

    def GET(self):
        form = TopicForm(self.request.params, request=self.request)
        return {
            'boards': self.boards,
            'board': self.board,
            'form': form,
        }

    def POST(self):
        raise NotImplementedError


class TopicView(BaseView):
    """Display topic and list all posts associated with board. If query is
    given to :attr:`self.request.matchdict` then only posts that satisfied
    the query criteria is shown.
    """

    def GET(self):
        posts = self.topic.scoped_posts(self.request.matchdict.get('query'))
        if posts:
            form = PostForm(self.request.params, request=self.request)
            return {
                'boards': self.boards,
                'board': self.board,
                'topic': self.topic,
                'posts': posts,
                'form': form,
            }
        else:
            raise HTTPNotFound

    def POST(self):
        raise NotImplementedError


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
