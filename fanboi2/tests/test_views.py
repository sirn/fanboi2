import mock
import unittest
from fanboi2.tests import ViewMixin, ModelMixin, TaskMixin, DummyAsyncResult


class TestApiViews(ViewMixin, ModelMixin, TaskMixin, unittest.TestCase):

    def test_root(self):
        from fanboi2.views.api import root
        request = self._GET()
        self.assertEqual(root(request), {})

    def test_boards_get(self):
        from fanboi2.views.api import boards_get
        board1 = self._makeBoard(title='Foobar', slug='foobar')
        board2 = self._makeBoard(title='Foobaz', slug='foobaz')
        board3 = self._makeBoard(title='Demo', slug='foodemo')
        request = self._GET()
        response = list(boards_get(request))
        self.assertSAEqual(response, [board3, board1, board2])

    def test_board_get(self):
        from fanboi2.views.api import board_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        request = self._GET()
        request.matchdict['board'] = board.slug
        response = board_get(request)
        self.assertSAEqual(response, board)

    def test_board_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.api import board_get
        request = self._GET()
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            board_get(request)

    def test_board_topics_get(self):
        from fanboi2.views.api import board_topics_get

        def _make_topic(days=0, **kwargs):
            from datetime import datetime, timedelta
            topic = self._makeTopic(**kwargs)
            self._makePost(
                topic=topic,
                body='Hello',
                created_at=datetime.now() - timedelta(days=days))
            return topic

        board1 = self._makeBoard(title='Foobar', slug='foobar')
        board2 = self._makeBoard(title='Demo', slug='demo')
        topic1 = _make_topic(0, board=board1, title='Foo')
        topic2 = _make_topic(1, board=board1, title='Foo')
        topic3 = _make_topic(2, board=board1, title='Foo')
        topic4 = _make_topic(3, board=board1, title='Foo')
        topic5 = _make_topic(4, board=board1, title='Foo', status='locked')
        topic6 = _make_topic(5, board=board1, title='Foo', status='archived')
        topic7 = _make_topic(6, board=board1, title='Foo')
        topic8 = _make_topic(7, board=board1, title='Foo')
        topic9 = _make_topic(8, board=board1, title='Foo')
        topic10 = _make_topic(10, board=board1, title='Foo')
        topic11 = _make_topic(11, board=board1, title='Foo')

        _make_topic(0, board=board2, title='Foo')
        _make_topic(9, board=board1, title='Foo', status='archived')
        _make_topic(9, board=board1, title='Foo', status='locked')

        request = self._GET()
        request.matchdict['board'] = board1.slug
        response = board_topics_get(request)
        self.assertSAEqual(response, [
            topic1,
            topic2,
            topic3,
            topic4,
            topic5,
            topic6,
            topic7,
            topic8,
            topic9,
            topic10,
            topic11,
        ])

    def test_board_topics_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.api import board_topics_get
        request = self._GET()
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            board_topics_get(request)

    # noinspection PyUnresolvedReferences
    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_topic.delay')
    def test_board_topics_post(self, add_, limit_):
        from fanboi2.views.api import board_topics_post
        board = self._makeBoard(title='Foobar', slug='foobar')

        request = self._POST({'title': 'Thread thread', 'body': 'Words words'})
        request.matchdict['board'] = board.slug
        self._makeConfig(request, self._makeRegistry())
        add_.return_value = mock_response = mock.Mock(id='task-uuid')

        response = board_topics_post(request)
        self.assertEqual(response, mock_response)
        limit_.assert_called_with(board.settings['post_delay'])
        add_.assert_called_with(
            request=mock.ANY,
            board_id=board.id,
            title='Thread thread',
            body='Words words',
        )

    # noinspection PyUnresolvedReferences
    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_topic.delay')
    def test_board_topics_post_json(self, add_, limit_):
        from fanboi2.views.api import board_topics_post
        board = self._makeBoard(title='Foobar', slug='foobar')

        request = self._json_POST({'title': 'Thread', 'body': 'Words words'})
        request.matchdict['board'] = board.slug
        self._makeConfig(request, self._makeRegistry())
        add_.return_value = mock_response = mock.Mock(id='task-uuid')

        response = board_topics_post(request)
        self.assertEqual(response, mock_response)
        limit_.assert_called_with(board.settings['post_delay'])
        add_.assert_called_with(
            request=mock.ANY,
            board_id=board.id,
            title='Thread',
            body='Words words',
        )

    def test_board_topics_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.api import board_topics_post
        request = self._POST({'title': 'Thread thread', 'body': 'Words words'})
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            board_topics_post(request)

    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_topic.delay')
    def test_board_topics_post_failed(self, add_, limit_):
        from fanboi2.errors import ParamsInvalidError
        from fanboi2.models import DBSession, Topic
        from fanboi2.views.api import board_topics_post
        board = self._makeBoard(title='Foobar', slug='foobar')

        request = self._POST({'title': 'Thread thread', 'body': ''})
        request.matchdict['board'] = board.slug
        self._makeConfig(request, self._makeRegistry())
        with self.assertRaises(ParamsInvalidError):
            board_topics_post(request)

        self.assertFalse(limit_.called)
        self.assertFalse(add_.called)
        self.assertEqual(DBSession.query(Topic).count(), 0)

    @mock.patch('fanboi2.utils.RateLimiter.timeleft')
    @mock.patch('fanboi2.utils.RateLimiter.limited')
    @mock.patch('fanboi2.tasks.add_topic.delay')
    def test_board_topics_post_limited(self, add_, limited_, time_):
        from fanboi2.errors import RateLimitedError
        from fanboi2.models import DBSession, Topic
        from fanboi2.views.api import board_topics_post
        board = self._makeBoard(title='Foobar', slug='foobar')

        request = self._POST({'title': 'Thread thread', 'body': 'Words words'})
        request.matchdict['board'] = board.slug
        self._makeConfig(request, self._makeRegistry())
        limited_.return_value = True
        time_.return_value = 10
        with self.assertRaises(RateLimitedError):
            board_topics_post(request)

        self.assertFalse(add_.called)
        self.assertTrue(limited_.called)
        self.assertTrue(time_.called)
        self.assertEqual(DBSession.query(Topic).count(), 0)

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_task_get(self, result_):
        from fanboi2.views.api import task_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Words words')
        result_.return_value = async_result = DummyAsyncResult(
            'dummy',
            'success',
            ['topic', topic.id])

        request = self._GET()
        request.matchdict['task'] = 'dummy'
        response = task_get(request)
        self.assertEqual(response.id, async_result.id)
        self.assertEqual(response.object, topic)
        result_.assert_called_with('dummy')

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_task_get_failure(self, result_):
        from fanboi2.errors import SpamRejectedError
        from fanboi2.views.api import task_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Words words')
        result_.return_value = DummyAsyncResult('dummy', 'success', [
            'failure',
            'spam_rejected'])

        request = self._GET()
        request.matchdict['task'] = 'dummy'
        with self.assertRaises(SpamRejectedError):
            task_get(request)

    def test_topic_get(self):
        from fanboi2.views.api import topic_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Demo')
        request = self._GET()
        request.matchdict['topic'] = topic.id
        response = topic_get(request)
        self.assertSAEqual(response, topic)

    def test_topic_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.api import topic_get
        request = self._GET()
        request.matchdict['topic'] = '1234'
        with self.assertRaises(NoResultFound):
            topic_get(request)

    def test_topic_posts_get(self):
        from fanboi2.views.api import topic_posts_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic1 = self._makeTopic(board=board, title='Demo')
        topic2 = self._makeTopic(board=board, title='Demo 2')
        post1 = self._makePost(topic=topic1, body='Lorem ipsum')
        post2 = self._makePost(topic=topic1, body='Dolor sit amet')
        self._makePost(topic=topic2, body='Foobar baz')

        request = self._GET()
        request.matchdict['topic'] = topic1.id
        response = topic_posts_get(request)
        self.assertSAEqual(response, [post1, post2])

    def test_topic_posts_query(self):
        from fanboi2.views.api import topic_posts_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Demo')
        post = self._makePost(topic=topic, body='Lorem ipsum')
        self._makePost(topic=topic, body='Dolor sit amet')

        request = self._GET()
        request.matchdict['topic'] = topic.id
        request.matchdict['query'] = post.number
        response = topic_posts_get(request)
        self.assertSAEqual(response, [post])

    def test_topic_posts_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.api import topic_posts_get
        request = self._GET()
        request.matchdict['topic'] = '1234'
        with self.assertRaises(NoResultFound):
            topic_posts_get(request)

    # noinspection PyUnresolvedReferences
    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_post.delay')
    def test_topic_posts_post(self, add_, limit_):
        from fanboi2.views.api import topic_posts_post
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Words')

        request = self._POST({'body': 'Words words'})
        request.matchdict['topic'] = topic.id
        self._makeConfig(request, self._makeRegistry())
        add_.return_value = mock_response = mock.Mock(id='task-uuid')

        response = topic_posts_post(request)
        self.assertEqual(response, mock_response)
        limit_.assert_called_with(board.settings['post_delay'])
        add_.assert_called_with(
            request=mock.ANY,
            topic_id=topic.id,
            body='Words words',
            bumped=False,
        )

    # noinspection PyUnresolvedReferences
    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_post.delay')
    def test_topic_posts_post_json(self, add_, limit_):
        from fanboi2.views.api import topic_posts_post
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Words')

        request = self._json_POST({'body': 'Words words'})
        request.matchdict['topic'] = topic.id
        self._makeConfig(request, self._makeRegistry())
        add_.return_value = mock_response = mock.Mock(id='task-uuid')

        response = topic_posts_post(request)
        self.assertEqual(response, mock_response)
        limit_.assert_called_with(board.settings['post_delay'])
        add_.assert_called_with(
            request=mock.ANY,
            topic_id=topic.id,
            body='Words words',
            bumped=False,
        )

    def test_topic_posts_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.api import topic_posts_post
        request = self._POST({'body': 'Words words'})
        request.matchdict['topic'] = '12345'
        with self.assertRaises(NoResultFound):
            topic_posts_post(request)

    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_post.delay')
    def test_topic_posts_post_failed(self, add_, limit_):
        from fanboi2.errors import ParamsInvalidError
        from fanboi2.models import DBSession, Post
        from fanboi2.views.api import topic_posts_post
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Words words')
        post_count = DBSession.query(Post).count()

        request = self._POST({'body': ''})
        request.matchdict['topic'] = topic.id
        self._makeConfig(request, self._makeRegistry())
        with self.assertRaises(ParamsInvalidError):
            topic_posts_post(request)

        self.assertFalse(limit_.called)
        self.assertFalse(add_.called)
        self.assertEqual(DBSession.query(Post).count(), post_count)

    @mock.patch('fanboi2.utils.RateLimiter.timeleft')
    @mock.patch('fanboi2.utils.RateLimiter.limited')
    @mock.patch('fanboi2.tasks.add_post.delay')
    def test_topic_posts_post_limited(self, add_, limited_, time_):
        from fanboi2.errors import RateLimitedError
        from fanboi2.models import DBSession, Post
        from fanboi2.views.api import topic_posts_post
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Words words')
        post_count = DBSession.query(Post).count()

        request = self._POST({'body': 'Words words'})
        request.matchdict['topic'] = topic.id
        self._makeConfig(request, self._makeRegistry())
        limited_.return_value = True
        time_.return_value = 10
        with self.assertRaises(RateLimitedError):
            topic_posts_post(request)

        self.assertFalse(add_.called)
        self.assertTrue(limited_.called)
        self.assertTrue(time_.called)
        self.assertEqual(DBSession.query(Post).count(), post_count)

    def test_error_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        from fanboi2.views.api import error_not_found
        request = self._makeRequest(path='/foobar')
        response = error_not_found(HTTPNotFound(), request)
        self.assertEqual(request.response.status, '404 Not Found')
        self.assertEqual(response['type'], 'error')
        self.assertEqual(response['status'], 'not_found')
        self.assertEqual(
            response['message'],
            'The resource GET /foobar could not be found.')

    def test_error_base_handler(self):
        from fanboi2.errors import BaseError
        from fanboi2.views.api import error_base_handler
        request = self._makeRequest(path='/foobar')
        exc = BaseError()
        response = error_base_handler(exc, request)
        self.assertEqual(request.response.status, exc.http_status)
        self.assertEqual(response, exc)

    def test_api_routes_predicates(self):
        from fanboi2.views.api import _api_routes_only
        request = self._makeRequest(path='/api/test')
        self.assertTrue(_api_routes_only(None, request))

    def test_api_routes_predicates_not_api(self):
        from fanboi2.views.api import _api_routes_only
        request = self._makeRequest(path='/foobar/api')
        self.assertFalse(_api_routes_only(None, request))



class TestPageViews(ViewMixin, unittest.TestCase):

    def test_root(self):
        from fanboi2.views.pages import root
        board1 = self._makeBoard(title='Foobar', slug='foobar')
        board2 = self._makeBoard(title='Foobaz', slug='foobaz')
        board3 = self._makeBoard(title='Demo', slug='foodemo')
        request = self._GET()
        response = root(request)
        self.assertSAEqual(response['boards'], [
            board3,
            board1,
            board2,
        ])

    def test_board_show(self):
        from fanboi2.views.pages import board_show

        def _make_topic(days=0, **kwargs):
            from datetime import datetime, timedelta
            topic = self._makeTopic(**kwargs)
            self._makePost(
                topic=topic,
                body='Hello',
                created_at=datetime.now() - timedelta(days=days))
            return topic

        board1 = self._makeBoard(title='Foobar', slug='foobar')
        board2 = self._makeBoard(title='Demo', slug='demo')
        topic1 = _make_topic(0, board=board1, title='Foo')
        topic2 = _make_topic(1, board=board1, title='Foo')
        topic3 = _make_topic(2, board=board1, title='Foo')
        topic4 = _make_topic(3, board=board1, title='Foo')
        topic5 = _make_topic(4, board=board1, title='Foo', status='locked')
        topic6 = _make_topic(5, board=board1, title='Foo', status='archived')
        topic7 = _make_topic(6, board=board1, title='Foo')
        topic8 = _make_topic(7, board=board1, title='Foo')
        topic9 = _make_topic(8, board=board1, title='Foo')
        topic10 = _make_topic(10, board=board1, title='Foo')

        _make_topic(0, board=board2, title='Foo')
        _make_topic(9, board=board1, title='Foo', status='archived')
        _make_topic(9, board=board1, title='Foo', status='locked')
        _make_topic(11, board=board1, title='Foo')

        request = self._GET()
        request.matchdict['board'] = board1.slug
        response = board_show(request)
        self.assertSAEqual(response['board'], board1)
        self.assertSAEqual(response['topics'], [
            topic1,
            topic2,
            topic3,
            topic4,
            topic5,
            topic6,
            topic7,
            topic8,
            topic9,
            topic10,
        ])

    def test_board_show_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.pages import board_show
        request = self._GET()
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            board_show(request)

    def test_board_all(self):
        from fanboi2.views.pages import board_all

        def _make_topic(days=0, **kwargs):
            from datetime import datetime, timedelta
            topic = self._makeTopic(**kwargs)
            self._makePost(
                topic=topic,
                body='Hello',
                created_at=datetime.now() - timedelta(days=days))
            return topic

        board1 = self._makeBoard(title='Foobar', slug='foobar')
        board2 = self._makeBoard(title='Demo', slug='demo')
        topic1 = _make_topic(0, board=board1, title='Foo')
        topic2 = _make_topic(1, board=board1, title='Foo')
        topic3 = _make_topic(2, board=board1, title='Foo')
        topic4 = _make_topic(3, board=board1, title='Foo')
        topic5 = _make_topic(4, board=board1, title='Foo', status='locked')
        topic6 = _make_topic(5, board=board1, title='Foo', status='archived')
        topic7 = _make_topic(6, board=board1, title='Foo')
        topic8 = _make_topic(7, board=board1, title='Foo')
        topic9 = _make_topic(8, board=board1, title='Foo')
        topic10 = _make_topic(10, board=board1, title='Foo')
        topic11 = _make_topic(11, board=board1, title='Foo')

        _make_topic(0, board=board2, title='Foo')
        _make_topic(9, board=board1, title='Foo', status='archived')
        _make_topic(9, board=board1, title='Foo', status='locked')

        request = self._GET()
        request.matchdict['board'] = board1.slug
        response = board_all(request)
        self.assertSAEqual(response['board'], board1)
        self.assertSAEqual(response['topics'], [
            topic1,
            topic2,
            topic3,
            topic4,
            topic5,
            topic6,
            topic7,
            topic8,
            topic9,
            topic10,
            topic11,
        ])

    def test_board_all_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.pages import board_all
        request = self._GET()
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            board_all(request)

    def test_board_new_get(self):
        from fanboi2.views.pages import board_new_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        request = self._GET()
        request.matchdict['board'] = board.slug
        self._makeConfig(request, self._makeRegistry())
        response = board_new_get(request)
        self.assertSAEqual(response['board'], board)

    # noinspection PyUnresolvedReferences
    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_board_new_get_task(self, result_):
        from fanboi2.views.pages import board_new_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['topic', topic.id])

        request = self._GET()
        request.matchdict['board'] = board.slug
        request.params['task'] = 'dummy'
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('topic', '/{board}/{topic}')

        response = board_new_get(request)
        location = '/%s/%s' % (board.slug, topic.id)
        self.assertEqual(response.location, location)
        result_.assert_called_with('dummy')

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_board_new_get_task_wait(self, result_):
        from fanboi2.views.pages import board_new_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        result_.return_value = DummyAsyncResult('dummy', 'pending')

        request = self._GET()
        request.matchdict['board'] = board.slug
        request.params['task'] = 'dummy'
        config = self._makeConfig(request, self._makeRegistry())
        config.testing_add_renderer('boards/new_wait.mako')

        board_new_get(request)
        result_.assert_called_with('dummy')

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_board_new_get_spam_rejected(self, result_):
        from fanboi2.views.pages import board_new_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        result_.return_value = DummyAsyncResult('dummy', 'success', [
            'failure',
            'spam_rejected'])

        request = self._GET()
        request.matchdict['board'] = board.slug
        request.params['task'] = 'dummy'
        config = self._makeConfig(request, self._makeRegistry())
        config.testing_add_renderer('boards/error_spam.mako')

        response = board_new_get(request)
        result_.assert_called_with('dummy')
        self.assertEqual(response.status, '422 Unprocessable Entity')

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_board_new_get_dnsbl_rejected(self, result_):
        from fanboi2.views.pages import board_new_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        result_.return_value = DummyAsyncResult('dummy', 'success', [
            'failure',
            'dnsbl_rejected'])

        request = self._GET()
        request.matchdict['board'] = board.slug
        request.params['task'] = 'dummy'
        config = self._makeConfig(request, self._makeRegistry())
        config.testing_add_renderer('boards/error_dnsbl.mako')

        response = board_new_get(request)
        result_.assert_called_with('dummy')
        self.assertEqual(response.status, '422 Unprocessable Entity')

    def test_board_new_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.pages import board_new_get
        request = self._GET()
        request.matchdict['board'] = 'notexists'
        with self.assertRaises(NoResultFound):
            board_new_get(request)

    # noinspection PyUnresolvedReferences
    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_topic.delay')
    def test_board_new_post(self, add_, limit_):
        from fanboi2.views.pages import board_new_post
        board = self._makeBoard(title='Foobar', slug='foobar')

        request = self._POST({'title': 'Thread thread', 'body': 'Words words'})
        request.matchdict['board'] = board.slug
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('board_new', '/{board}/new')
        add_.return_value = mock.Mock(id='task-uuid')

        response = board_new_post(self._make_csrf(request))
        self.assertEqual(response.location, '/foobar/new?task=task-uuid')
        limit_.assert_called_with(board.settings['post_delay'])
        add_.assert_called_with(
            request=mock.ANY,
            board_id=board.id,
            title='Thread thread',
            body='Words words',
        )

    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_topic.delay')
    def test_board_new_post_failed(self, add_, limit_):
        from fanboi2.models import DBSession, Topic
        from fanboi2.views.pages import board_new_post
        board = self._makeBoard(title='Foobar', slug='foobar')

        request = self._POST({'title': 'Thread thread', 'body': ''})
        request.matchdict['board'] = board.slug
        self._makeConfig(request, self._makeRegistry())

        response = board_new_post(self._make_csrf(request))
        self.assertFalse(limit_.called)
        self.assertFalse(add_.called)
        self.assertEqual(DBSession.query(Topic).count(), 0)
        self.assertEqual(response['form'].title.data, 'Thread thread')
        self.assertDictEqual(response['form'].errors, {
            'body': ['This field is required.']
        })

    @mock.patch('fanboi2.utils.RateLimiter.timeleft')
    @mock.patch('fanboi2.utils.RateLimiter.limited')
    @mock.patch('fanboi2.tasks.add_topic.delay')
    def test_board_new_post_limited(self, add_, limited_, time_):
        from fanboi2.models import DBSession, Topic
        from fanboi2.views.pages import board_new_post
        board = self._makeBoard(title='Foobar', slug='foobar')

        request = self._POST({'title': 'Thread thread', 'body': 'Words words'})
        request.matchdict['board'] = board.slug
        config = self._makeConfig(request, self._makeRegistry())
        config.testing_add_renderer('boards/error_rate.mako')
        limited_.return_value = True
        time_.return_value = 10

        board_new_post(self._make_csrf(request))
        self.assertFalse(add_.called)
        self.assertTrue(limited_.called)
        self.assertTrue(time_.called)
        self.assertEqual(DBSession.query(Topic).count(), 0)

    def test_board_new_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.pages import board_new_post
        request = self._POST({'title': 'Thread thread', 'body': 'Words words'})
        request.matchdict['board'] = 'notexists'
        self._makeConfig(request, self._makeRegistry())
        with self.assertRaises(NoResultFound):
            board_new_post(self._make_csrf(request))

    def test_topic_show_get(self):
        from fanboi2.views.pages import topic_show_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic1 = self._makeTopic(board=board, title='Foobar')
        post1 = self._makePost(topic=topic1, body='Words')
        post2 = self._makePost(topic=topic1, body='Words')
        topic2 = self._makeTopic(board=board, title='Foobaz')
        self._makePost(topic=topic2, body='Words')

        request = self._GET()
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic1.id
        self._makeConfig(request, self._makeRegistry())

        response = topic_show_get(request)
        self.assertSAEqual(response['board'], board)
        self.assertSAEqual(response['topic'], topic1)
        self.assertSAEqual(response['posts'], [post1, post2])

    def test_topic_show_get_query(self):
        from fanboi2.views.pages import topic_show_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Demo')
        post = self._makePost(topic=topic, body='Lorem ipsum')
        self._makePost(topic=topic, body='Dolor sit amet')

        request = self._GET()
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.matchdict['query'] = post.number
        self._makeConfig(request, self._makeRegistry())

        response = topic_show_get(request)
        self.assertSAEqual(response['posts'], [post])

    # noinspection PyUnresolvedReferences
    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_topic_show_get_task(self, result_):
        from fanboi2.views.pages import topic_show_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Lorem ipsum')
        self._makePost(topic=topic, body='Dolor sit amet')
        post = self._makePost(topic=topic, body='Foobar baz')
        result_.return_value = DummyAsyncResult(
            'dummy',
            'success',
            ['post', post.id])

        request = self._GET()
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.params['task'] = 'dummy'
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('topic_scoped', '/{board}/{topic}/{query}')

        response = topic_show_get(request)
        location = '/%s/%s/l10' % (board.slug, topic.id)
        self.assertEqual(response.location, location)
        result_.assert_called_with('dummy')

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_topic_show_get_task_wait(self, result_):
        from fanboi2.views.pages import topic_show_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Lorem ipsum')
        self._makePost(topic=topic, body='Dolor sit amet')
        result_.return_value = DummyAsyncResult('dummy', 'pending')

        request = self._GET()
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.params['task'] = 'dummy'
        config = self._makeConfig(request, self._makeRegistry())
        config.testing_add_renderer('topics/show_wait.mako')

        topic_show_get(request)
        result_.assert_called_with('dummy')

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_topic_show_get_spam_rejected(self, result_):
        from fanboi2.views.pages import topic_show_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Lorem ipsum')
        self._makePost(topic=topic, body='Dolor sit amet')
        result_.return_value = DummyAsyncResult('dummy', 'success', [
            'failure',
            'spam_rejected'])

        request = self._GET()
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.params['task'] = 'dummy'
        config = self._makeConfig(request, self._makeRegistry())
        config.testing_add_renderer('topics/error_spam.mako')

        response = topic_show_get(request)
        result_.assert_called_with('dummy')
        self.assertEqual(response.status, '422 Unprocessable Entity')

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_topic_show_get_status_rejected(self, result_):
        from fanboi2.views.pages import topic_show_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Lorem ipsum')
        self._makePost(topic=topic, body='Dolor sit amet')
        result_.return_value = DummyAsyncResult('dummy', 'success', [
            'failure',
            'status_rejected',
            'archived'])

        request = self._GET()
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        request.params['task'] = 'dummy'
        config = self._makeConfig(request, self._makeRegistry())
        config.testing_add_renderer('topics/error_status.mako')

        response = topic_show_get(request)
        result_.assert_called_with('dummy')
        self.assertEqual(response.status, '422 Unprocessable Entity')

    def test_topic_show_get_topic_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.pages import topic_show_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        request = self._GET()
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = '12345'
        with self.assertRaises(NoResultFound):
            topic_show_get(request)

    def test_topic_show_get_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from fanboi2.views.pages import topic_show_get
        board1 = self._makeBoard(title='Foobar', slug='foobar')
        board2 = self._makeBoard(title='Foobaz', slug='foobaz')
        topic = self._makeTopic(board=board1, title='Foobar')
        request = self._GET()
        request.matchdict['board'] = board2.slug
        request.matchdict['topic'] = topic.id
        with self.assertRaises(HTTPNotFound):
            topic_show_get(request)

    # noinspection PyUnresolvedReferences
    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_post.delay')
    def test_topic_show_post(self, add_, limit_):
        from fanboi2.views.pages import topic_show_post
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Words')

        request = self._POST({'body': 'Words words'})
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('topic', '/{board}/{topic}')
        add_.return_value = mock.Mock(id='task-uuid')

        response = topic_show_post(self._make_csrf(request))
        location = '/%s/%s?task=task-uuid' % (board.slug, topic.id)
        self.assertEqual(response.location, location)
        limit_.assert_called_with(board.settings['post_delay'])
        add_.assert_called_with(
            request=mock.ANY,
            topic_id=topic.id,
            body='Words words',
            bumped=False,
        )

    def test_topic_show_post_board_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.pages import topic_show_get
        request = self._POST({'body': 'Words words'})
        request.matchdict['board'] = 'notexists'
        self._makeConfig(request, self._makeRegistry())
        with self.assertRaises(NoResultFound):
            topic_show_get(self._make_csrf(request))

    def test_topic_show_post_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from fanboi2.views.pages import topic_show_get
        board = self._makeBoard(title='Foobar', slug='foobar')
        request = self._POST({'body': 'Words words'})
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = '12345'
        self._makeConfig(request, self._makeRegistry())
        with self.assertRaises(NoResultFound):
            topic_show_get(self._make_csrf(request))

    def test_topic_show_post_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        from fanboi2.views.pages import topic_show_post
        board1 = self._makeBoard(title='Foobar', slug='foobar')
        board2 = self._makeBoard(title='Foobaz', slug='foobaz')
        topic = self._makeTopic(board=board1, title='Foobar')
        request = self._POST({'body': 'Words words'})
        request.matchdict['board'] = board2.slug
        request.matchdict['topic'] = topic.id
        self._makeConfig(request, self._makeRegistry())
        with self.assertRaises(HTTPNotFound):
            topic_show_post(self._make_csrf(request))

    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_post.delay')
    def test_topic_show_post_failed(self, add_, limit_):
        from fanboi2.models import DBSession, Post
        from fanboi2.views.pages import topic_show_post
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Words words')
        post_count = DBSession.query(Post).count()

        request = self._POST({'body': ''})
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        self._makeConfig(request, self._makeRegistry())

        response = topic_show_post(self._make_csrf(request))
        self.assertFalse(limit_.called)
        self.assertFalse(add_.called)
        self.assertEqual(DBSession.query(Post).count(), post_count)
        self.assertSAEqual(response['topic'], topic)
        self.assertDictEqual(response['form'].errors, {
            'body': ['This field is required.']
        })

    @mock.patch('fanboi2.utils.RateLimiter.timeleft')
    @mock.patch('fanboi2.utils.RateLimiter.limited')
    @mock.patch('fanboi2.tasks.add_post.delay')
    def test_board_show_post_limited(self, add_, limited_, time_):
        from fanboi2.models import DBSession, Post
        from fanboi2.views.pages import topic_show_post
        board = self._makeBoard(title='Foobar', slug='foobar')
        topic = self._makeTopic(board=board, title='Foobar')
        self._makePost(topic=topic, body='Words words')
        post_count = DBSession.query(Post).count()

        request = self._POST({'body': 'Words words'})
        request.matchdict['board'] = board.slug
        request.matchdict['topic'] = topic.id
        config = self._makeConfig(request, self._makeRegistry())
        config.testing_add_renderer('topics/error_rate.mako')
        limited_.return_value = True
        time_.return_value = 10

        topic_show_post(self._make_csrf(request))
        self.assertFalse(add_.called)
        self.assertTrue(limited_.called)
        self.assertTrue(time_.called)
        self.assertEqual(DBSession.query(Post).count(), post_count)

    def test_error_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        from fanboi2.views.pages import error_not_found
        request = self._makeRequest(path='/foobar')
        config = self._makeConfig(request, self._makeRegistry())
        config.testing_add_renderer('not_found.mako')
        response = error_not_found(HTTPNotFound(), request)
        self.assertEqual(response.status, '404 Not Found')
