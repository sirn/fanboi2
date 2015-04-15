import json
import unittest
from pyramid import testing
from fanboi2.tests import ModelMixin, RegistryMixin, TaskMixin, DummyAsyncResult


class TestJSONRenderer(RegistryMixin, unittest.TestCase):

    def _getTargetFunction(self):
        from fanboi2.serializers import initialize_renderer
        return initialize_renderer()

    def _makeOne(self, object, request=None):
        if request is None:
            request = testing.DummyRequest()
        renderer = self._getTargetFunction()(None)
        return json.loads(renderer(object, {'request': request}))

    def test_datetime(self):
        from datetime import datetime, timezone
        self.assertEqual(
            self._makeOne(datetime(2013, 1, 2, 0, 4, 1, 0, timezone.utc)),
            '2013-01-02T00:04:01+00:00')


class TestJSONRendererWithModel(ModelMixin, RegistryMixin, unittest.TestCase):

    def _getTargetFunction(self):
        from fanboi2.serializers import initialize_renderer
        return initialize_renderer()

    def _makeOne(self, object, request=None):
        if request is None:  # pragma: no cover
            request = testing.DummyRequest()
        renderer = self._getTargetFunction()(None)
        return json.loads(renderer(object, {'request': request}))

    def test_query(self):
        from fanboi2.models import DBSession
        from fanboi2.models import Board
        board1 = self._makeBoard(title='Foobar', slug='bar')
        board2 = self._makeBoard(title='Foobaz', slug='baz')
        request = self._makeRequest()
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('api_board', '/board/{board}/')
        response = self._makeOne(
            DBSession.query(Board).order_by(Board.title),
            request=request)
        self.assertIsInstance(response, list)
        self.assertEqual(response[0]['title'], board1.title)
        self.assertEqual(response[1]['title'], board2.title)

    def test_board(self):
        board = self._makeBoard(title='Foobar', slug='foo')
        request = self._makeRequest()
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('api_board', '/board/{board}/')
        response = self._makeOne(board, request=request)
        self.assertEqual(response['type'], 'board')
        self.assertEqual(response['title'], 'Foobar')
        self.assertEqual(response['slug'], 'foo')
        self.assertEqual(response['path'], '/board/foo/')
        self.assertIn('id', response)
        self.assertIn('agreements', response)
        self.assertIn('description', response)
        self.assertIn('settings', response)
        self.assertNotIn('topics', response)

    def test_board_with_topics(self):
        board = self._makeBoard(title='Foobar', slug='foo')
        request = self._makeRequest(params={'topics': True})
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('api_board', '/board/{board}/')
        response = self._makeOne(board, request=request)
        self.assertIn('topics', response)

    def test_topic(self):
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Heavenly Moon')
        request = self._makeRequest()
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('api_topic', '/topic/{topic}/')
        response = self._makeOne(topic, request=request)
        self.assertEqual(response['type'], 'topic')
        self.assertEqual(response['title'], 'Heavenly Moon')
        self.assertEqual(response['board_id'], board.id)
        self.assertEqual(response['path'], '/topic/%s/' % topic.id)
        self.assertIn('bumped_at', response)
        self.assertIn('created_at', response)
        self.assertIn('post_count', response)
        self.assertIn('posted_at', response)
        self.assertIn('status', response)
        self.assertNotIn('posts', response)

    def test_topic_with_posts(self):
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Heavenly Moon')
        request = self._makeRequest(params={'posts': True})
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('api_topic', '/topic/{topic}/')
        response = self._makeOne(topic, request=request)
        self.assertEqual(response['title'], 'Heavenly Moon')
        self.assertEqual(response['board_id'], board.id)
        self.assertIn('posts', response)

    def test_post(self):
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Baz')
        post = self._makePost(topic=topic, body='Hello, world!')
        request = self._makeRequest()
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('api_topic_posts_scoped', '/topic/{topic}/{query}/')
        response = self._makeOne(post, request=request)
        self.assertEqual(response['type'], 'post')
        self.assertEqual(response['body'], 'Hello, world!')
        self.assertEqual(response['topic_id'], topic.id)
        self.assertEqual(
            response['path'],
            '/topic/%s/%s/' % (topic.id, post.number))
        self.assertIn('bumped', response)
        self.assertIn('created_at', response)
        self.assertIn('ident', response)
        self.assertIn('name', response)
        self.assertIn('number', response)
        self.assertNotIn('ip_address', response)
        self.assertNotIn('body_formatted', response)

    def test_post_with_formatted(self):
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Baz')
        post = self._makePost(topic=topic, body='Hello, world!')
        request = self._makeRequest(params={'formatted': True})
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('api_topic_posts_scoped', '/topic/{topic}/{query}/')
        response = self._makeOne(post, request=request)
        self.assertEqual(response['body_formatted'], '<p>Hello, world!</p>')


class TestJSONRendererWithTask(
        TaskMixin,
        ModelMixin,
        RegistryMixin,
        unittest.TestCase):

    def _getTargetFunction(self):
        from fanboi2.serializers import initialize_renderer
        return initialize_renderer()

    def _makeOne(self, object, request=None):
        if request is None:  # pragma: no cover
            request = testing.DummyRequest()
        renderer = self._getTargetFunction()(None)
        return json.loads(renderer(object, {'request': request}))

    def test_result_proxy(self):
        from fanboi2.tasks import ResultProxy
        request = self._makeRequest()
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('api_task', '/task/{task}/')
        result_proxy = ResultProxy(DummyAsyncResult('demo', 'pending'))
        response = self._makeOne(result_proxy, request=request)
        self.assertEqual(response['type'], 'task')
        self.assertEqual(response['status'], 'pending')
        self.assertEqual(response['id'], 'demo')
        self.assertEqual(response['path'], '/task/demo/')
        self.assertNotIn('data', response)

    def test_result_proxy_success(self):
        from fanboi2.tasks import ResultProxy
        board = self._makeBoard(title='Foobar', slug='foo')
        request = self._makeRequest()
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('api_task', '/task/{task}/')
        config.add_route('api_board', '/board/{board}/')
        result = ['board', board.id]
        result_proxy = ResultProxy(DummyAsyncResult('demo', 'success', result))
        response = self._makeOne(result_proxy, request=request)
        self.assertEqual(response['type'], 'task')
        self.assertEqual(response['status'], 'success')
        self.assertEqual(response['id'], 'demo')
        self.assertEqual(response['path'], '/task/demo/')
        self.assertIn('data', response)

    def test_async_result(self):
        from fanboi2.tasks import celery
        request = self._makeRequest()
        config = self._makeConfig(request, self._makeRegistry())
        config.add_route('api_task', '/task/{task}/')
        async_result = celery.AsyncResult('demo')
        response = self._makeOne(async_result, request=request)
        self.assertEqual(response['type'], 'task')
        self.assertEqual(response['status'], 'queued')
        self.assertEqual(response['id'], 'demo')
        self.assertEqual(response['path'], '/task/demo/')
