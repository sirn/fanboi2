import json
import unittest
from pyramid import testing
from fanboi2.tests import ModelMixin


class TestJSONRenderer(unittest.TestCase):

    def _getTargetFunction(self):
        from fanboi2.serializers import json_renderer
        return json_renderer

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


class TestJSONRendererWithModel(ModelMixin, unittest.TestCase):

    def _getTargetFunction(self):
        from fanboi2.serializers import json_renderer
        return json_renderer

    def _makeOne(self, object, request=None):
        if request is None:
            request = testing.DummyRequest()
        renderer = self._getTargetFunction()(None)
        return json.loads(renderer(object, {'request': request}))

    def test_query(self):
        from fanboi2.models import DBSession
        from fanboi2.models import Board
        board1 = self._makeBoard(title='Foobar', slug='bar')
        board2 = self._makeBoard(title='Foobaz', slug='baz')
        response = self._makeOne(DBSession.query(Board).order_by(Board.title))
        self.assertIsInstance(response, list)
        self.assertEqual(response[0]['title'], board1.title)
        self.assertEqual(response[1]['title'], board2.title)

    def test_board(self):
        board = self._makeBoard(title='Foobar', slug='foo')
        response = self._makeOne(board)
        self.assertEqual(response['title'], 'Foobar')
        self.assertEqual(response['slug'], 'foo')
        self.assertIn('id', response)
        self.assertIn('agreements', response)
        self.assertIn('description', response)
        self.assertIn('settings', response)

    def test_topic(self):
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Heavenly Moon')
        response = self._makeOne(topic)
        self.assertEqual(response['title'], 'Heavenly Moon')
        self.assertEqual(response['board_id'], board.id)
        self.assertIn('bumped_at', response)
        self.assertIn('created_at', response)
        self.assertIn('post_count', response)
        self.assertIn('posted_at', response)
        self.assertIn('status', response)

    def test_post(self):
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Baz')
        post = self._makePost(topic=topic, body='Hello, world!')
        response = self._makeOne(post)
        self.assertEqual(response['body'], 'Hello, world!')
        self.assertEqual(response['body_formatted'], '<p>Hello, world!</p>')
        self.assertEqual(response['topic_id'], topic.id)
        self.assertIn('bumped', response)
        self.assertIn('created_at', response)
        self.assertIn('ident', response)
        self.assertIn('name', response)
        self.assertIn('number', response)
        self.assertNotIn('ip_address', response)
