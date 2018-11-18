import unittest

from . import ModelSessionMixin


class TestTopicMetaModel(ModelSessionMixin, unittest.TestCase):
    def test_relations(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Lorem ipsum dolor sit"))
        topic_meta = self._make(TopicMeta(topic=topic, post_count=1))
        self.dbsession.commit()
        self.assertEqual(topic_meta.topic, topic)
        self.assertEqual(topic_meta, topic.meta)
