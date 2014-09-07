import mock
import unittest
from fanboi2.tests import ModelMixin, ViewMixin


class DummyAsyncResult(object):

    def __init__(self, state, _data=None, _raise=None):
        self.state = state
        self._data = _data
        self._raise = _raise

    def get(self):
        if self._raise is not None:
            raise self._raise
        return self._data


class TestBaseView(ViewMixin, ModelMixin, unittest.TestCase):

    def _makeOne(self):
        from fanboi2.views import BaseView

        class _MockView(BaseView):
            pass

        return _MockView

    def test_init(self):
        board1 = self._makeBoard(title="General", slug="general")
        board2 = self._makeBoard(title="Foobar", slug="foo")
        view = self._makeOne()(self.request)
        self.assertEqual(view.request, self.request)
        self.assertEqual(view.board, None)
        self.assertEqual(view.topic, None)
        self.assertListEqual(view.boards, [board2, board1])

    def test_board(self):
        board1 = self._makeBoard(title="General", slug="general")
        board2 = self._makeBoard(title="Foobar", slug="foo")
        request = self._GET()
        request.matchdict['board'] = 'foo'
        view = self._makeOne()(request)
        self.assertEqual(view.board, board2)

    def test_board_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = self._GET()
        request.matchdict['board'] = 'foo'
        view = self._makeOne()(request)
        with self.assertRaises(HTTPNotFound):
            assert not view.board

    def test_topic(self):
        board = self._makeBoard(title="General", slug="general")
        topic1 = self._makeTopic(board=board, title="Foobar")
        topic2 = self._makeTopic(board=board, title="Hello")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic2.id)
        view = self._makeOne()(request)
        self.assertEqual(view.board, board)
        self.assertEqual(view.topic, topic2)

    def test_topic_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        board = self._makeBoard(title="General", slug="general")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = '2943'
        view = self._makeOne()(request)
        with self.assertRaises(HTTPNotFound):
            assert not view.topic

    def test_topic_wrong_board(self):
        from pyramid.httpexceptions import HTTPNotFound
        board1 = self._makeBoard(title="General", slug="general")
        board2 = self._makeBoard(title="Foobar", slug="foo")
        topic1 = self._makeTopic(board=board1, title="Foobar")
        topic2 = self._makeTopic(board=board2, title="Hello")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic2.id)
        view = self._makeOne()(request)
        with self.assertRaises(HTTPNotFound):
            assert not view.topic

    def test_topic_no_board(self):
        request = self._GET()
        request.matchdict['topic'] = '2943'
        view = self._makeOne()(request)
        self.assertEqual(view.board, None)
        self.assertEqual(view.topic, None)

    def test_call_unimplemented(self):
        request = self._GET()
        view = self._makeOne()(request)
        with self.assertRaises(NotImplementedError):
            assert not view()


class TestBaseTaskView(ViewMixin, ModelMixin, unittest.TestCase):

    def _makeOne(self):
        from fanboi2.views import BaseView, BaseTaskView

        class _MockView(BaseTaskView, BaseView):
            pass

        return _MockView

    def test_get_dispatch_initial(self):
        request = self._GET()
        view = self._makeOne()(request)
        with mock.patch.object(view, 'GET_initial') as get_call:
            get_call.assert_called_once()

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_get_dispatch_success(self, async):
        from celery.states import SUCCESS
        request = self._GET({'task': '1234'})
        board = self._makeBoard(title='Foobar', slug='foobar')
        async.return_value = DummyAsyncResult(SUCCESS, ('board', board.id))
        view = self._makeOne()(request)
        with mock.patch.object(view, 'GET_success') as get_call:
            assert view()
            get_call.assert_called_once_with(board)

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_get_dispatch_task(self, async):
        from celery.states import PENDING
        async.return_value = DummyAsyncResult(PENDING)
        request = self._GET({'task': '1234'})
        view = self._makeOne()(request)
        with mock.patch.object(view, 'GET_task') as get_call:
            assert view()
            get_call.assert_called_once_with()

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_get_dispatch_failure(self, async):
        from celery.states import SUCCESS
        async.return_value = DummyAsyncResult(SUCCESS, ('failure', 'foobar'))
        request = self._GET({'task': '1234'})
        view = self._makeOne()(request)
        with mock.patch.object(view, 'GET_failure') as get_call:
            assert view()
            get_call.assert_called_once_with('foobar')


class TestRootView(ViewMixin, ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.views import RootView
        return RootView

    def test_get(self):
        board1 = self._makeBoard(title="General", slug="general")
        board2 = self._makeBoard(title="Foobar", slug="foo")
        request = self._GET()
        response = self._getTargetClass()(request)()
        self.assertListEqual(response["boards"], [board2, board1])


class TestBoardView(ViewMixin, ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.views import BoardView
        return BoardView

    def test_get(self):
        def _make_topic(days=0, **kwargs):
            from datetime import datetime, timedelta
            topic = self._makeTopic(**kwargs)
            self._makePost(
                topic=topic,
                body="Hello",
                created_at=datetime.now() - timedelta(days=days))
            return topic

        board = self._makeBoard(title="General", slug="general")
        topic1 = _make_topic(0, board=board, title="Foo1")
        topic2 = _make_topic(1, board=board, title="Foo2")
        topic3 = _make_topic(2, board=board, title="Foo3")
        topic4 = _make_topic(3, board=board, title="Foo4")
        topic5 = _make_topic(4, board=board, title="Foo5", status="locked")
        topic6 = _make_topic(5, board=board, title="Foo6", status="archived")
        topic7 = _make_topic(6, board=board, title="Foo7")
        topic8 = _make_topic(7, board=board, title="Foo8")
        topic9 = _make_topic(8, board=board, title="Foo9")
        topic10 = _make_topic(9, board=board, title="Foo10")
        topic11 = _make_topic(10, board=board, title="Foo11")
        request = self._GET()
        request.matchdict['board'] = 'general'
        response = self._getTargetClass()(request)()
        self.assertEqual(response["board"], board)
        self.assertListEqual(response["boards"], [board])
        self.assertListEqual(
            response["topics"], [
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
            ]
        )

    def test_get_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = self._GET()
        request.matchdict['board'] = 'general'
        with self.assertRaises(HTTPNotFound):
            assert not self._getTargetClass()(request)()


class TestBoardAllView(ViewMixin, ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.views import BoardAllView
        return BoardAllView

    def test_get(self):
        def _make_topic(days=0, **kwargs):
            from datetime import datetime, timedelta
            topic = self._makeTopic(**kwargs)
            self._makePost(
                topic=topic,
                body="Hello",
                created_at=datetime.now() - timedelta(days=days))
            return topic

        board = self._makeBoard(title="General", slug="general")
        topic1 = _make_topic(0, board=board, title="Foo1")
        topic2 = _make_topic(5, board=board, title="Foo2", status="locked")
        topic3 = _make_topic(6, board=board, title="Foo3", status="archived")
        topic4 = _make_topic(7, board=board, title="Foo4", status="locked")
        topic5 = _make_topic(8, board=board, title="Foo5", status="archived")
        request = self._GET()
        request.matchdict['board'] = 'general'
        response = self._getTargetClass()(request)()
        self.assertEqual(response["board"], board)
        self.assertListEqual(response["boards"], [board])
        self.assertListEqual(
            response["topics"], [
                topic1,
                topic2,
                topic3,
            ]
        )

    def test_get_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = self._GET()
        request.matchdict['board'] = 'general'
        with self.assertRaises(HTTPNotFound):
            assert not self._getTargetClass()(request)()


class TestBoardNewView(ViewMixin, ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.views import BoardNewView
        return BoardNewView

    def test_get(self):
        board = self._makeBoard(title="General", slug="general")
        request = self._GET()
        request.matchdict['board'] = 'general'
        response = self._getTargetClass()(request)()
        self.assertListEqual(response["boards"], [board])
        self.assertDictEqual(response["form"].errors, {})
        self.assertEqual(response["board"], board)

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_get_success(self, async):
        from celery.states import SUCCESS
        board = self._makeBoard(title='General', slug='general')
        topic = self._makeTopic(board=board, title='Hello, world!')
        request = self._GET({'task': 1234})
        request.matchdict['board'] = 'general'
        async.return_value = DummyAsyncResult(SUCCESS, ('topic', topic.id))
        self.config.add_route('topic_scoped', '/{board}/{topic}/{query}')
        response = self._getTargetClass()(request)()
        self.assertEqual(response.location, "/general/%s/l5" % topic.id)

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_get_failure(self, async):
        from celery.states import SUCCESS
        async.return_value = DummyAsyncResult(SUCCESS, ('failure', 'foobar'))
        self.config.testing_add_renderer('boards/error.jinja2')
        request = self._GET({'task': '1234'})
        response = self._getTargetClass()(request)()
        self.assertEqual(response.status_int, 200)

    def test_get_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = self._GET()
        request.matchdict['board'] = 'general'
        with self.assertRaises(HTTPNotFound):
            assert not self._getTargetClass()(request)()

    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_topic.delay')
    def test_post(self, add_topic, limit_call):
        board = self._makeBoard(title="General", slug="general")
        request = self._make_csrf(self._POST({
            'title': "One more thing...",
            'body': "And now for something completely different...",
        }))
        request.matchdict['board'] = 'general'
        self.config.add_route('board_new', '/{board}/new')
        add_topic.return_value = mock.Mock(id=123)
        response = self._getTargetClass()(request)()
        self.assertEqual(response.location, "/general/new?task=123")
        limit_call.assert_called_with(board.settings['post_delay'])
        add_topic.assert_called_with(
            request=mock.ANY,
            board_id=board.id,
            title='One more thing...',
            body='And now for something completely different...',
        )

    def test_post_failure(self):
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title="General", slug="general")
        request = self._make_csrf(self._POST({
            'title': "One more thing...",
            'body': "",
        }))
        request.matchdict['board'] = 'general'
        response = self._getTargetClass()(request)()

        self.assertEqual(DBSession.query(Topic).count(), 0)
        self.assertEqual(response["form"].title.data, 'One more thing...')
        self.assertDictEqual(response["form"].errors, {
            'body': ['This field is required.']
        })

    @mock.patch('fanboi2.utils.RateLimiter.limited')
    @mock.patch('fanboi2.utils.RateLimiter.timeleft')
    def test_post_limited(self, timeleft_call, limited_call):
        from fanboi2.models import DBSession, Topic
        self._makeBoard(title="General", slug="general")
        request = self._make_csrf(self._POST({
            'title': "Flooding the board!!1",
            'body': "LOLUSUX!!11",
        }))
        request.matchdict['board'] = 'general'
        limited_call.return_value = True
        timeleft_call.return_value = 10
        self.config.testing_add_renderer('boards/error_rate.jinja2')
        self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Topic).count(), 0)
        self.assertTrue(limited_call.called)
        self.assertTrue(timeleft_call.called)


class TestTopicView(ViewMixin, ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.views import TopicView
        return TopicView

    def test_get(self):
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        post1 = self._makePost(topic=topic, body="Hello, world!")
        post2 = self._makePost(topic=topic, body="Boring post is boring!")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        response = self._getTargetClass()(request)()
        self.assertListEqual(response["boards"], [board])
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)
        self.assertEqual(response["form"].bumped.data, True)
        self.assertDictEqual(response["form"].errors, {})
        self.assertListEqual(response["posts"], [post1, post2])

    def test_get_scoped(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Hello, world!")
        post1 = self._makePost(topic=topic, body="Boring test is boring!")
        post2 = self._makePost(topic=topic, body="Boring post is boring!")
        request = self._GET()
        request.matchdict['board'] = 'foo'
        request.matchdict['topic'] = str(topic.id)
        request.matchdict['query'] = '2'
        response = self._getTargetClass()(request)()
        self.assertListEqual(response["boards"], [board])
        self.assertEqual(response["board"], board)
        self.assertEqual(response["topic"], topic)
        self.assertDictEqual(response["form"].errors, {})
        self.assertListEqual(response["posts"], [post2])

    def test_get_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        board = self._makeBoard(title="General", slug="general")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = '2943'
        with self.assertRaises(HTTPNotFound):
            assert not self._getTargetClass()(request)()

    def test_get_empty_posts(self):
        from pyramid.httpexceptions import HTTPNotFound
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Hello, world!")
        request = self._GET()
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        with self.assertRaises(HTTPNotFound):
            assert not self._getTargetClass()(request)()

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_get_success(self, async):
        from celery.states import SUCCESS
        board = self._makeBoard(title='General', slug='general')
        topic = self._makeTopic(board=board, title='Hello, world!')
        post = self._makePost(topic=topic, body='Foobar!')
        request = self._GET({'task': 1234})
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        async.return_value = DummyAsyncResult(SUCCESS, ('post', post.id))
        self.config.add_route('topic_scoped', '/{board}/{topic}/{query}')
        response = self._getTargetClass()(request)()
        self.assertEqual(response.location, "/general/%s/l5" % topic.id)

    @mock.patch('fanboi2.tasks.celery.AsyncResult')
    def test_get_failure(self, async):
        from celery.states import SUCCESS
        async.return_value = DummyAsyncResult(SUCCESS, ('failure', 'foobar'))
        self.config.testing_add_renderer('topics/error.jinja2')
        request = self._GET({'task': '1234'})
        response = self._getTargetClass()(request)()
        self.assertEqual(response.status_int, 200)

    @mock.patch('fanboi2.utils.RateLimiter.limit')
    @mock.patch('fanboi2.tasks.add_post.delay')
    def test_post(self, add_post, limit_call):
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        request = self._make_csrf(self._POST({'body': "Boring post..."}))
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        self.config.add_route('topic', '/{board}/{topic}')
        add_post.return_value = mock.Mock(id=3124)
        response = self._getTargetClass()(request)()
        self.assertEqual(response.location, "/general/%s?task=3124" % topic.id)
        limit_call.assert_called_with(board.settings['post_delay'])
        add_post.assert_called_with(
            request=mock.ANY,
            topic_id=topic.id,
            body='Boring post...',
            bumped=False,
        )

    def test_post_failure(self):
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        request = self._make_csrf(self._POST({'body': 'x'}))
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        response = self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Post).count(), 0)
        self.assertEqual(response["form"].body.data, 'x')
        self.assertDictEqual(response["form"].errors, {
            'body': ['Field must be between 2 and 4000 characters long.'],
        })

    @mock.patch('fanboi2.utils.RateLimiter.limited')
    @mock.patch('fanboi2.utils.RateLimiter.timeleft')
    def test_post_limited(self, timeleft_call, limited_call):
        from fanboi2.models import DBSession, Post
        board = self._makeBoard(title="General", slug="general")
        topic = self._makeTopic(board=board, title="Spam spam spam")
        request = self._make_csrf(self._POST({'body': 'Blah, blah, blah!'}))
        request.matchdict['board'] = 'general'
        request.matchdict['topic'] = str(topic.id)
        limited_call.return_value = True
        timeleft_call.return_value = 10
        self.config.testing_add_renderer('topics/error_rate.jinja2')
        self._getTargetClass()(request)()
        self.assertEqual(DBSession.query(Post).count(), 0)
        self.assertTrue(limited_call.called)
        self.assertTrue(timeleft_call.called)
