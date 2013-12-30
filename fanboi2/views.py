from celery import states
from datetime import timedelta, datetime
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.response import Response
from sqlalchemy import or_, and_
from sqlalchemy.orm import undefer
from sqlalchemy.orm.exc import NoResultFound
from .forms import TopicForm, PostForm
from .models import Topic, Post, Board, DBSession
from .tasks import celery, add_topic, add_post, TaskException
from .utils import RateLimiter, serialize_request


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


class BaseTaskView(object):
    """Second-level dispatcher. If ``task`` is present in params, it will try
    to retrieve the specific task ID from :class:`celery.AsyncResult` then
    determine if the task is success and calls :meth:`GET_success`,
    :meth:`GET_failure` or :meth:`GET_task` accordingly.
    """

    def _serialize(self, objtuple):
        key, value = objtuple
        return DBSession.query({
            'post': Post,
            'topic': Topic,
            'board': Board,
            }[key]).get(value)

    # noinspection PyUnresolvedReferences
    def GET(self):
        if 'task' in self.request.params:
            task = celery.AsyncResult(self.request.params['task'])

            if task.state == states.SUCCESS:
                obj = self._serialize(task.get())
                return self.GET_success(obj)

            elif task.state == states.FAILURE:
                try:
                    task.get()
                except TaskException as exc:
                    return self.GET_failure(exc.args[0])

            else:
                return self.GET_task()

        else:
            return self.GET_initial()

    def GET_initial(self):  # pragma: no cover
        raise NotImplementedError

    def GET_task(self):  # pragma: no cover
        return self.GET_failure('task')

    def GET_success(self, obj):  # pragma: no cover
        raise NotImplementedError

    def GET_failure(self, error):  # pragma: no cover
        raise NotImplementedError


class RootView(BaseView):
    """List all boards."""

    def GET(self):
        return {'boards': self.boards}


class BoardView(BaseView):
    """Display board and all 10 recent posts regardless of its status."""

    def GET(self):
        topics = self.board.topics.limit(10).all()
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
                                               timedelta(days=7)))).\
            all()
        return {
            'boards': self.boards,
            'board': self.board,
            'topics': topics,
        }


class BoardNewView(BaseTaskView, BaseView):
    """Display and handle creation of new topic."""

    def GET_initial(self):
        form = TopicForm(self.request.params, request=self.request)
        return {
            'boards': self.boards,
            'board': self.board,
            'form': form,
        }

    def GET_success(self, topic):
        return HTTPFound(location=self.request.route_path(
            route_name='topic_scoped',
            board=topic.board.slug,
            topic=topic.id,
            query='l5'))

    def GET_failure(self, error):
        return render_to_response('boards/error.jinja2', {
            'error': error,
            'boards': self.boards,
            'board': self.board,
        }, request=self.request)

    def POST(self):
        form = TopicForm(self.request.params, request=self.request)

        if form.validate():
            ratelimit = RateLimiter(self.request, namespace=self.board.slug)
            if ratelimit.limited():
                return render_to_response('boards/error_rate.jinja2', {
                    'seconds': ratelimit.timeleft(),
                    'boards': self.boards,
                    'board': self.board,
                }, request=self.request)

            task = add_topic.delay(
                request=serialize_request(self.request),
                board_id=self.board.id,
                title=form.title.data,
                body=form.body.data)

            ratelimit.limit(self.board.settings['post_delay'])
            return HTTPFound(location=self.request.route_path(
                route_name='board_new',
                board=self.board.slug,
                _query={'task': task.id}))

        return {
            'boards': self.boards,
            'board': self.board,
            'form': form,
        }


class TopicView(BaseTaskView, BaseView):
    """Display topic and list all posts associated with board. If query is
    given to :attr:`self.request.matchdict` then only posts that satisfied
    the query criteria is shown.
    """

    def GET_initial(self):
        posts = self.topic.scoped_posts(self.request.matchdict.get('query'))
        if posts:
            form = PostForm(self.request.params,
                            obj=Post(bumped=True),
                            request=self.request)
            return {
                'boards': self.boards,
                'board': self.board,
                'topic': self.topic,
                'posts': posts,
                'form': form,
            }
        else:
            raise HTTPNotFound

    def GET_success(self, post):
        return HTTPFound(location=self.request.route_path(
            route_name='topic_scoped',
            board=self.topic.board.slug,
            topic=self.topic.id,
            query='l5'))

    def GET_failure(self, error):
        return render_to_response('topics/error.jinja2', {
            'error': error,
            'boards': self.boards,
            'board': self.board,
            'topic': self.topic,
        }, request=self.request)

    def POST(self):
        form = PostForm(self.request.params, request=self.request)

        if form.validate():
            ratelimit = RateLimiter(self.request, namespace=self.board.slug)
            if ratelimit.limited():
                return render_to_response('topics/error_rate.jinja2', {
                    'seconds': ratelimit.timeleft(),
                    'boards': self.boards,
                    'board': self.board,
                    'topic': self.topic,
                }, request=self.request)

            task = add_post.delay(
                request=serialize_request(self.request),
                topic_id=self.topic.id,
                body=form.body.data,
                bumped=form.bumped.data)

            ratelimit.limit(self.board.settings['post_delay'])
            return HTTPFound(location=self.request.route_path(
                route_name='topic',
                board=self.topic.board.slug,
                topic=self.topic.id,
                _query={'task': task.id}))

        return {
            'boards': self.boards,
            'board': self.board,
            'topic': self.topic,
            'posts': self.topic.posts,
            'form': form,
       }
