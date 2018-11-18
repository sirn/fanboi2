import unittest

from . import ModelSessionMixin


class TestPostModel(ModelSessionMixin, unittest.TestCase):
    def test_relations(self):
        from ..models import Board, Topic, Post

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Lorem ipsum dolor sit"))
        post = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Hello, world",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        self.assertEqual(post.topic, topic)
        self.assertEqual([post], list(topic.posts))

    def test_versioned(self):
        from ..models import Board, Topic, Post

        PostHistory = Post.__history_mapper__.class_
        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Lorem ipsum dolor"))
        post = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Foobar baz",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        self.assertEqual(post.version, 1)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 0)
        post.body = "Foobar baz updated"
        self.dbsession.add(post)
        self.dbsession.commit()
        self.assertEqual(post.version, 2)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 1)
        post_1 = self.dbsession.query(PostHistory).filter_by(version=1).one()
        self.assertEqual(post_1.id, post.id)
        self.assertEqual(post_1.topic_id, topic.id)
        self.assertEqual(post_1.body, "Foobar baz")
        self.assertEqual(post_1.version, 1)
        self.assertIsNotNone(post_1.changed_at)
        self.assertIsNotNone(post_1.created_at)
        self.assertIsNone(post_1.updated_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic, Post

        PostHistory = Post.__history_mapper__.class_
        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Lorem ipsum dolor"))
        post = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Foobar baz",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        self.dbsession.delete(post)
        self.dbsession.commit()
        self.assertTrue(inspect(post).was_deleted)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 1)
        post_1 = self.dbsession.query(PostHistory).filter_by(version=1).one()
        self.assertEqual(post_1.id, post.id)
        self.assertEqual(post_1.topic_id, topic.id)
        self.assertEqual(post_1.body, "Foobar baz")
        self.assertEqual(post_1.change_type, "delete")
        self.assertEqual(post_1.version, 1)
