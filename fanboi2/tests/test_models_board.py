import unittest

from . import ModelSessionMixin


class TestBoardModel(ModelSessionMixin, unittest.TestCase):
    def test_relations(self):
        from ..models import Board

        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        self.assertEqual([], list(board.topics))

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic, TopicMeta, Post

        board1 = self._make(Board(title="Foobar", slug="foo"))
        board2 = self._make(Board(title="Lorem", slug="lorem"))
        topic1 = self._make(Topic(board=board1, title="Heavenly Moon"))
        topic2 = self._make(Topic(board=board1, title="Beastie Starter"))
        topic3 = self._make(Topic(board=board2, title="Evans"))
        topic_meta1 = self._make(TopicMeta(topic=topic1, post_count=2))
        topic_meta2 = self._make(TopicMeta(topic=topic2, post_count=1))
        topic_meta3 = self._make(TopicMeta(topic=topic3, post_count=1))
        post1 = self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Fanboi",
                body="Bazz",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Hoge",
                ip_address="127.0.0.1",
            )
        )
        post4 = self._make(
            Post(
                topic=topic3,
                number=1,
                name="Nameless Fanboi",
                body="Fuzz",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        self.assertEqual({topic2, topic1}, set(board1.topics))
        self.assertEqual({topic3}, set(board2.topics))
        self.assertEqual({post2, post1}, set(topic1.posts))
        self.assertEqual({post3}, set(topic2.posts))
        self.assertEqual({post4}, set(topic3.posts))
        self.dbsession.delete(board1)
        self.dbsession.commit()
        self.assertTrue(inspect(board1).was_deleted)
        self.assertFalse(inspect(board2).was_deleted)
        self.assertTrue(inspect(topic1).was_deleted)
        self.assertTrue(inspect(topic2).was_deleted)
        self.assertFalse(inspect(topic3).was_deleted)
        self.assertTrue(inspect(topic_meta1).was_deleted)
        self.assertTrue(inspect(topic_meta2).was_deleted)
        self.assertFalse(inspect(topic_meta3).was_deleted)
        self.assertTrue(inspect(post1).was_deleted)
        self.assertTrue(inspect(post2).was_deleted)
        self.assertTrue(inspect(post3).was_deleted)
        self.assertFalse(inspect(post4).was_deleted)

    def test_versioned(self):
        from ..models import Board

        BoardHistory = Board.__history_mapper__.class_
        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        self.assertEqual(board.version, 1)
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 0)
        board.title = "Foobar and Baz"
        self.dbsession.add(board)
        self.dbsession.commit()
        self.assertEqual(board.version, 2)
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 1)
        board_1 = self.dbsession.query(BoardHistory).filter_by(version=1).one()
        self.assertEqual(board_1.id, board.id)
        self.assertEqual(board_1.title, "Foobar")
        self.assertEqual(board_1.change_type, "update")
        self.assertEqual(board_1.version, 1)
        self.assertIsNotNone(board_1.changed_at)
        self.assertIsNotNone(board_1.created_at)
        self.assertIsNone(board_1.updated_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from ..models import Board

        BoardHistory = Board.__history_mapper__.class_
        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        self.dbsession.delete(board)
        self.dbsession.commit()
        self.assertTrue(inspect(board).was_deleted)
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 1)
        board_1 = self.dbsession.query(BoardHistory).filter_by(version=1).one()
        self.assertEqual(board_1.id, board.id)
        self.assertEqual(board_1.title, "Foobar")
        self.assertEqual(board_1.change_type, "delete")
        self.assertEqual(board_1.version, 1)

    def test_versioned_deleted_cascade(self):
        from ..models import Board, Topic, Post

        BoardHistory = Board.__history_mapper__.class_
        TopicHistory = Topic.__history_mapper__.class_
        PostHistory = Post.__history_mapper__.class_
        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Heavenly Moon"))
        post = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 0)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 0)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 0)
        self.dbsession.delete(board)
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 1)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 1)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 1)
        board_1 = self.dbsession.query(BoardHistory).filter_by(version=1).one()
        self.assertEqual(board_1.id, board.id)
        self.assertEqual(board_1.change_type, "delete")
        self.assertEqual(board_1.version, 1)
        topic_1 = self.dbsession.query(TopicHistory).filter_by(version=1).one()
        self.assertEqual(topic_1.id, topic.id)
        self.assertEqual(topic_1.board_id, board.id)
        self.assertEqual(topic_1.change_type, "delete")
        self.assertEqual(topic_1.version, 1)
        post_1 = self.dbsession.query(PostHistory).filter_by(version=1).one()
        self.assertEqual(post_1.id, post.id)
        self.assertEqual(post_1.topic_id, topic.id)
        self.assertEqual(post_1.change_type, "delete")
        self.assertEqual(post_1.version, 1)

    def test_settings(self):
        from ..models import Board
        from ..models.board import DEFAULT_BOARD_CONFIG

        board = self._make(Board(title="Foobar", slug="Foo"))
        self.assertEqual(board.settings, DEFAULT_BOARD_CONFIG)
        board.settings = {"name": "Hamster"}
        new_settings = DEFAULT_BOARD_CONFIG.copy()
        new_settings.update({"name": "Hamster"})
        self.dbsession.add(board)
        self.dbsession.commit()
        self.assertEqual(board.settings, new_settings)

    def test_topics(self):
        from ..models import Board, Topic

        board1 = self._make(Board(title="Foobar", slug="foo"))
        board2 = self._make(Board(title="Lorem", slug="lorem"))
        topic1 = self._make(Topic(board=board1, title="Heavenly Moon"))
        topic2 = self._make(Topic(board=board1, title="Beastie Starter"))
        topic3 = self._make(Topic(board=board1, title="Evans"))
        self.dbsession.commit()
        self.assertEqual({topic3, topic2, topic1}, set(board1.topics))
        self.assertEqual([], list(board2.topics))

    def test_topics_sort(self):
        from datetime import datetime, timedelta
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="First"))
        topic2 = self._make(Topic(board=board, title="Second"))
        topic3 = self._make(Topic(board=board, title="Third"))
        topic4 = self._make(Topic(board=board, title="Fourth"))
        topic5 = self._make(Topic(board=board, title="Fifth"))
        self._make(
            TopicMeta(
                topic=topic1,
                post_count=1,
                bumped_at=datetime.now() + timedelta(minutes=2),
                posted_at=datetime.now() + timedelta(minutes=6),
            )
        )
        self._make(
            TopicMeta(
                topic=topic2,
                post_count=1,
                bumped_at=datetime.now() + timedelta(minutes=4),
                posted_at=datetime.now() + timedelta(minutes=6),
            )
        )
        self._make(
            TopicMeta(
                topic=topic3,
                post_count=1,
                bumped_at=datetime.now() + timedelta(minutes=3),
                posted_at=datetime.now() + timedelta(minutes=3),
            )
        )
        self._make(
            TopicMeta(
                topic=topic5,
                post_count=1,
                bumped_at=datetime.now() + timedelta(minutes=5),
                posted_at=datetime.now() + timedelta(minutes=5),
            )
        )
        self.dbsession.commit()
        self.assertEqual([topic5, topic2, topic3, topic1, topic4], list(board.topics))
