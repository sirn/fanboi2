import unittest
import unittest.mock

from sqlalchemy.orm.exc import NoResultFound

from . import ModelSessionMixin


class TestBoardCreateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import BoardCreateService

        return BoardCreateService

    def test_create(self):
        board_create_svc = self._get_target_class()(self.dbsession)
        board = board_create_svc.create(
            "foobar",
            title="Foobar",
            description="Board about foobar",
            status="open",
            agreements="Nope",
            settings={"foo": "bar"},
        )
        self.assertEqual(board.slug, "foobar")
        self.assertEqual(board.title, "Foobar")
        self.assertEqual(board.description, "Board about foobar")
        self.assertEqual(board.status, "open")
        self.assertEqual(board.agreements, "Nope")
        self.assertEqual(board.settings["foo"], "bar")


class TestBoardQueryService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import BoardQueryService

        return BoardQueryService

    def test_list_all(self):
        from ..models import Board

        board1 = self._make(Board(slug="foo", title="Foo", status="open"))
        board2 = self._make(Board(slug="baz", title="Baz", status="restricted"))
        board3 = self._make(Board(slug="bax", title="Bax", status="locked"))
        board4 = self._make(Board(slug="wel", title="Wel", status="open"))
        board5 = self._make(Board(slug="bar", title="Bar", status="archived"))
        self.dbsession.commit()
        board_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            board_query_svc.list_all(), [board5, board3, board2, board1, board4]
        )

    def test_list_active(self):
        from ..models import Board

        board1 = self._make(Board(slug="foo", title="Foo", status="open"))
        board2 = self._make(Board(slug="baz", title="Baz", status="restricted"))
        board3 = self._make(Board(slug="bax", title="Bax", status="locked"))
        board4 = self._make(Board(slug="wel", title="Wel", status="open"))
        self._make(Board(slug="bar", title="Bar", status="archived"))
        self.dbsession.commit()
        board_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(
            board_query_svc.list_active(), [board3, board2, board1, board4]
        )

    def test_list_active_no_active(self):
        board_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(board_query_svc.list_active(), [])

    def test_board_from_slug(self):
        from ..models import Board

        board = self._make(Board(slug="foo", title="Foo"))
        self.dbsession.commit()
        board_query_svc = self._get_target_class()(self.dbsession)
        self.assertEqual(board_query_svc.board_from_slug("foo"), board)

    def test_board_from_slug_not_found(self):
        board_query_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            board_query_svc.board_from_slug("not_found")


class TestBoardUpdateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import BoardUpdateService

        return BoardUpdateService

    def test_update(self):
        from ..models import Board

        board = self._make(
            Board(
                slug="baz",
                title="Baz",
                description="Baz baz baz",
                status="open",
                agreements="Yes",
                settings={"baz": "baz"},
            )
        )
        self.dbsession.commit()
        board_update_svc = self._get_target_class()(self.dbsession)
        board_update_svc.update(
            board.slug,
            title="Foobar",
            description="Foo foo foo",
            status="locked",
            agreements="Nope",
            settings={"baz": "bar"},
        )
        self.assertEqual(board.title, "Foobar")
        self.assertEqual(board.description, "Foo foo foo")
        self.assertEqual(board.status, "locked")
        self.assertEqual(board.agreements, "Nope")
        self.assertEqual(board.settings["baz"], "bar")

    def test_update_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound

        board_update_svc = self._get_target_class()(self.dbsession)
        with self.assertRaises(NoResultFound):
            board_update_svc.update(
                "notexists",
                title="Foobar",
                description="Foo foo foo",
                status="locked",
                agreements="Nope",
                settings={"baz": "bar"},
            )
