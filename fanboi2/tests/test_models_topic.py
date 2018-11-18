import unittest

from . import ModelSessionMixin


class TestTopicModel(ModelSessionMixin, unittest.TestCase):
    def test_relations(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Lorem ipsum dolor"))
        topic_meta = self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        self.assertEqual(topic.board, board)
        self.assertEqual([], list(topic.posts))
        self.assertEqual([topic], list(board.topics))
        self.assertEqual(topic.meta, topic_meta)

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic, TopicMeta, Post

        board = self._make(Board(title="Foobar", slug="foo"))
        topic1 = self._make(Topic(board=board, title="Shamshir Dance"))
        topic2 = self._make(Topic(board=board, title="Nyoah Sword Dance"))
        topic_meta1 = self._make(TopicMeta(topic=topic1, post_count=0))
        topic_meta2 = self._make(TopicMeta(topic=topic2, post_count=0))
        post1 = self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Fanboi",
                body="Lorem ipsum",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Fanboi",
                body="Dolor sit amet",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Quas magnam et",
                ip_address="127.0.0.1",
            )
        )
        self.assertEqual({post2, post1}, set(topic1.posts))
        self.assertEqual({post3}, set(topic2.posts))
        self.dbsession.delete(topic1)
        self.dbsession.commit()
        self.assertTrue(inspect(topic1).was_deleted)
        self.assertFalse(inspect(topic2).was_deleted)
        self.assertTrue(inspect(topic_meta1).was_deleted)
        self.assertFalse(inspect(topic_meta2).was_deleted)
        self.assertTrue(inspect(post1).was_deleted)
        self.assertTrue(inspect(post2).was_deleted)
        self.assertFalse(inspect(post3).was_deleted)

    def test_versioned(self):
        from ..models import Board, Topic

        TopicHistory = Topic.__history_mapper__.class_
        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self.dbsession.commit()
        self.assertEqual(topic.version, 1)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 0)
        topic.title = "Foobar Baz"
        self.dbsession.add(topic)
        self.dbsession.commit()
        self.assertEqual(topic.version, 2)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 1)
        topic_1 = self.dbsession.query(TopicHistory).filter_by(version=1).one()
        self.assertEqual(topic_1.id, topic.id)
        self.assertEqual(topic_1.board_id, topic.board_id)
        self.assertEqual(topic_1.title, "Foobar")
        self.assertEqual(topic_1.change_type, "update")
        self.assertEqual(topic_1.version, 1)
        self.assertIsNotNone(topic_1.changed_at)
        self.assertIsNotNone(topic_1.created_at)
        self.assertIsNone(topic_1.updated_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic

        TopicHistory = Topic.__history_mapper__.class_
        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Foobar"))
        self.dbsession.commit()
        self.dbsession.delete(topic)
        self.dbsession.commit()
        self.assertTrue(inspect(topic).was_deleted)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 1)
        topic_1 = self.dbsession.query(TopicHistory).filter_by(version=1).one()
        self.assertEqual(topic_1.id, topic.id)
        self.assertEqual(topic_1.board_id, topic.board_id)
        self.assertEqual(topic_1.title, "Foobar")
        self.assertEqual(topic_1.change_type, "delete")
        self.assertEqual(topic_1.version, 1)

    def test_versioned_deleted_cascade(self):
        from ..models import Board, Topic, Post

        BoardHistory = Board.__history_mapper__.class_
        TopicHistory = Topic.__history_mapper__.class_
        PostHistory = Post.__history_mapper__.class_
        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Cosmic Agenda"))
        post = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Foobar",
                ip_address="127.0.0.1",
            )
        )
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 0)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 0)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 0)
        self.dbsession.delete(topic)
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 0)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 1)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 1)
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

    def test_posts(self):
        from ..models import Board, Topic, Post

        board = self._make(Board(title="Foobar", slug="foo"))
        topic1 = self._make(Topic(board=board, title="Lorem ipsum dolor"))
        topic2 = self._make(Topic(board=board, title="Some lonely topic"))
        post1 = self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Fanboi",
                body="Lorem",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Fanboi",
                body="Ipsum",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic1,
                number=3,
                name="Nameless Fanboi",
                body="Dolor",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        self.assertEqual([post1, post2, post3], list(topic1.posts))
        self.assertEqual([], list(topic2.posts))

    def test_meta(self):
        from ..models import Board, Topic, TopicMeta

        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Lorem ipsum dolor"))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        self.assertEqual(topic.meta.post_count, 0)
        self.assertIsNone(topic.meta.posted_at)
        self.assertIsNone(topic.meta.bumped_at)

    def test_scoped_posts(self):
        from ..models import Board, Topic, Post

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Hello, world!"))
        post1 = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Post 1",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic,
                number=2,
                name="Nameless Fanboi",
                body="Post 2",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                number=3,
                topic=topic,
                name="Nameless Fanboi",
                body="Post 3",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        self.assertListEqual(topic.scoped_posts(None), [post1, post2, post3])
        self.assertListEqual(topic.scoped_posts("bogus"), [])

    def test_single_post(self):
        from ..models import Board, Topic, Post

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Hello, world!"))
        topic2 = self._make(Topic(board=board, title="Another post!!1"))
        topic3 = self._make(Topic(board=board, title="Empty topic"))
        self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Fanboi",
                body="Post 1",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Post 1",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Fanboi",
                body="Post 2",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic2,
                number=2,
                name="Nameless Fanboi",
                body="Post 2",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        results = topic1.single_post(2)
        self.assertListEqual(results, [post3])
        self.assertListEqual(results, topic1.scoped_posts("2"))
        self.assertListEqual(topic1.single_post(1000), [])
        self.assertListEqual(topic3.single_post(1), [])
        self.assertListEqual(topic3.single_post(), [])

    def test_ranged_posts(self):
        from ..models import Board, Topic, Post

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Hello, world!"))
        topic2 = self._make(Topic(board=board, title="Another test"))
        topic3 = self._make(Topic(board=board, title="Empty topic"))
        self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Fanboi",
                body="Topic 1, Post 1",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Fanboi",
                body="Topic 1, Post 2",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic1,
                number=3,
                name="Nameless Fanboi",
                body="Topic 1, Post 3",
                ip_address="127.0.0.1",
            )
        )
        post4 = self._make(
            Post(
                topic=topic1,
                number=4,
                name="Nameless Fanboi",
                body="Topic 1, Post 4",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Topic 2, Post 1",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic2,
                number=2,
                name="Nameless Fanboi",
                body="Topic 2, Post 2",
                ip_address="127.0.0.1",
            )
        )
        post7 = self._make(
            Post(
                topic=topic1,
                number=5,
                name="Nameless Fanboi",
                body="Topic 1, Post 5",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        results = topic1.ranged_posts(2, 5)
        self.assertListEqual(results, [post2, post3, post4, post7])
        self.assertListEqual(results, topic1.scoped_posts("2-5"))
        self.assertListEqual(topic1.ranged_posts(1000, 1005), [])
        self.assertListEqual(topic3.ranged_posts(1, 5), [])
        self.assertListEqual(topic1.ranged_posts(), topic1.posts.all())

    def test_ranged_posts_without_end(self):
        from ..models import Board, Topic, Post

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Hello, world!"))
        topic2 = self._make(Topic(board=board, title="Another test"))
        topic3 = self._make(Topic(board=board, title="Empty topic"))
        self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Fanboi",
                body="Topic 1, Post 1",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Fanboi",
                body="Topic 1, Post 2",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic1,
                number=3,
                name="Nameless Fanboi",
                body="Topic 1, Post 3",
                ip_address="127.0.0.1",
            )
        )
        post4 = self._make(
            Post(
                topic=topic1,
                number=4,
                name="Nameless Fanboi",
                body="Topic 1, Post 4",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Topic 2, Post 1",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic2,
                number=2,
                name="Nameless Fanboi",
                body="Topic 2, Post 2",
                ip_address="127.0.0.1",
            )
        )
        post7 = self._make(
            Post(
                topic=topic1,
                number=5,
                name="Nameless Fanboi",
                body="Topic 1, Post 5",
                ip_address="127.0.0.1",
            )
        )
        results = topic1.ranged_posts(3)
        self.assertListEqual(results, [post3, post4, post7])
        self.assertListEqual(results, topic1.scoped_posts("3-"))
        self.assertListEqual(topic1.ranged_posts(1000), [])
        self.assertListEqual(topic3.ranged_posts(3), [])

    def test_range_query_without_start(self):
        from ..models import Board, Topic, Post

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Hello, world!"))
        topic2 = self._make(Topic(board=board, title="Another test"))
        topic3 = self._make(Topic(board=board, title="Empty topic"))
        post1 = self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Fanboi",
                body="Topic 1, Post 1",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Fanboi",
                body="Topic 1, Post 2",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic1,
                number=3,
                name="Nameless Fanboi",
                body="Topic 1, Post 3",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic1,
                number=4,
                name="Nameless Fanboi",
                body="Topic 1, Post 4",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic2,
                number=1,
                name="Nameless Fanboi",
                body="Topic 2, Post 1",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic2,
                number=2,
                name="Nameless Fanboi",
                body="Topic 2, Post 2",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic1,
                number=5,
                name="Nameless Fanboi",
                body="Topic 1, Post 5",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        results = topic1.ranged_posts(None, 3)
        self.assertListEqual(results, [post1, post2, post3])
        self.assertListEqual(results, topic1.scoped_posts("-3"))
        self.assertListEqual(topic1.ranged_posts(None, 0), [])
        self.assertListEqual(topic3.ranged_posts(None, 3), [])

    def test_recent_query(self):
        from ..models import Board, Topic, Post

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Hello, world!"))
        topic2 = self._make(Topic(board=board, title="Another test"))
        topic3 = self._make(Topic(board=board, title="Empty topic"))
        self._make(
            Post(
                topic=topic1,
                number=1,
                name="Nameless Fanboi",
                body="Topic 1, Post 1",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic1,
                number=2,
                name="Nameless Fanboi",
                body="Topic 1, Post 2",
                ip_address="127.0.0.1",
            )
        )
        for i in range(5):
            self._make(
                Post(
                    topic=topic2,
                    number=i + 1,
                    name="Nameless Fanboi",
                    body="Foobar",
                    ip_address="127.0.0.1",
                )
            )
        post3 = self._make(
            Post(
                topic=topic2,
                number=6,
                name="Nameless Fanboi",
                body="Topic 2, Post 6",
                ip_address="127.0.0.1",
            )
        )
        self._make(
            Post(
                topic=topic1,
                number=3,
                name="Nameless Fanboi",
                body="Topic 1, Post 3",
                ip_address="127.0.0.1",
            )
        )
        for i in range(24):
            self._make(
                Post(
                    topic=topic2,
                    number=i + 7,
                    name="Nameless Fanboi",
                    body="Foobar",
                    ip_address="127.0.0.1",
                )
            )
        post5 = self._make(
            Post(
                topic=topic2,
                number=31,
                name="Nameless Fanboi",
                body="Topic 2, Post 31",
                ip_address="127.0.0.1",
            )
        )
        for i in range(3):
            self._make(
                Post(
                    topic=topic2,
                    number=i + 32,
                    name="Nameless Fanboi",
                    body="Foobar",
                    ip_address="127.0.0.1",
                )
            )
        post6 = self._make(
            Post(
                topic=topic2,
                number=35,
                name="Nameless Fanboi",
                body="Topic 2, Post 35",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        default_results = topic2.recent_posts()
        self.assertEqual(default_results[0], post3)
        self.assertEqual(default_results[-1], post6)
        self.assertListEqual(default_results, topic2.scoped_posts("recent"))
        numbered_results = topic2.recent_posts(5)
        self.assertEqual(numbered_results[0], post5)
        self.assertEqual(numbered_results[-1], post6)
        self.assertListEqual(numbered_results, topic2.scoped_posts("l5"))
        self.assertListEqual(topic2.recent_posts(0), [])
        self.assertListEqual(topic3.recent_posts(), [])

    def test_recent_query_missing(self):
        from ..models import Board, Topic, Post

        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Hello, world!"))
        post1 = self._make(
            Post(
                topic=topic,
                number=1,
                name="Nameless Fanboi",
                body="Post 1",
                ip_address="127.0.0.1",
            )
        )
        post2 = self._make(
            Post(
                topic=topic,
                number=2,
                name="Nameless Fanboi",
                body="Post 2",
                ip_address="127.0.0.1",
            )
        )
        post3 = self._make(
            Post(
                topic=topic,
                number=3,
                name="Nameless Fanboi",
                body="Post 3",
                ip_address="127.0.0.1",
            )
        )
        post4 = self._make(
            Post(
                topic=topic,
                number=4,
                name="Nameless Fanboi",
                body="Post 4",
                ip_address="127.0.0.1",
            )
        )
        post5 = self._make(
            Post(
                topic=topic,
                number=5,
                name="Nameless Fanboi",
                body="Post 5",
                ip_address="127.0.0.1",
            )
        )
        post6 = self._make(
            Post(
                topic=topic,
                number=6,
                name="Nameless Fanboi",
                body="Post 6",
                ip_address="127.0.0.1",
            )
        )
        self.dbsession.commit()
        self.assertListEqual(
            [post2, post3, post4, post5, post6], topic.scoped_posts("l5")
        )
        self.dbsession.delete(post3)
        self.dbsession.commit()
        self.assertListEqual(
            [post1, post2, post4, post5, post6], topic.scoped_posts("l5")
        )
