import unittest
import unittest.mock

from webob.multidict import MultiDict

from . import IntegrationMixin


class TestIntegrationAdminBoards(IntegrationMixin, unittest.TestCase):
    def test_boards_get(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.admin import boards_get
        from . import mock_service

        board1 = self._make(Board(slug="foo", title="Foo", status="open"))
        board2 = self._make(Board(slug="baz", title="Baz", status="restricted"))
        board3 = self._make(Board(slug="bax", title="Bax", status="locked"))
        board4 = self._make(Board(slug="wel", title="Wel", status="open"))
        board5 = self._make(Board(slug="bar", title="Bar", status="archived"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        response = boards_get(request)
        self.assertEqual(response["boards"], [board5, board3, board2, board1, board4])

    def test_board_new_get(self):
        from ..forms import AdminBoardNewForm
        from ..views.admin import board_new_get

        self.request.method = "GET"
        response = board_new_get(self.request)
        self.assertIsInstance(response["form"], AdminBoardNewForm)

    def test_board_new_post(self):
        from ..interfaces import IBoardCreateService
        from ..models import Board
        from ..services import BoardCreateService
        from ..views.admin import board_new_post
        from . import mock_service

        request = mock_service(
            self.request, {IBoardCreateService: BoardCreateService(self.dbsession)}
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["slug"] = "foobar"
        request.POST["title"] = "Foobar"
        request.POST["status"] = "open"
        request.POST["description"] = "Foobar"
        request.POST["agreements"] = "I agree"
        request.POST["settings"] = '{"name":"Nameless Foobar"}'
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_board", "/admin/boards/{board}")
        response = board_new_post(request)
        board = self.dbsession.query(Board).first()
        self.assertEqual(response.location, "/admin/boards/foobar")
        self.assertEqual(self.dbsession.query(Board).count(), 1)
        self.assertEqual(board.slug, "foobar")
        self.assertEqual(board.title, "Foobar")
        self.assertEqual(board.description, "Foobar")
        self.assertEqual(board.agreements, "I agree")
        self.assertEqual(
            board.settings,
            {
                "expire_duration": 0,
                "max_posts": 1000,
                "name": "Nameless Foobar",
                "post_delay": 10,
                "use_ident": True,
            },
        )

    def test_board_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import board_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["slug"] = "foobar"
        self.request.POST["title"] = "Foobar"
        self.request.POST["status"] = "open"
        self.request.POST["description"] = "Foobar"
        self.request.POST["agreements"] = "I agree"
        self.request.POST["settings"] = "{}"
        with self.assertRaises(BadCSRFToken):
            board_new_post(self.request)

    def test_board_new_post_invalid_status(self):
        from ..models import Board
        from ..views.admin import board_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["slug"] = "foobar"
        self.request.POST["title"] = "Foobar"
        self.request.POST["status"] = "foobar"
        self.request.POST["description"] = "Foobar"
        self.request.POST["agreements"] = "I agree"
        self.request.POST["settings"] = "{}"
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = board_new_post(self.request)
        self.assertEqual(self.dbsession.query(Board).count(), 0)
        self.assertEqual(response["form"].slug.data, "foobar")
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].status.data, "foobar")
        self.assertEqual(response["form"].description.data, "Foobar")
        self.assertEqual(response["form"].agreements.data, "I agree")
        self.assertEqual(response["form"].settings.data, "{}")
        self.assertDictEqual(
            response["form"].errors, {"status": ["Not a valid choice"]}
        )

    def test_board_new_post_invalid_settings(self):
        from ..models import Board
        from ..views.admin import board_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["slug"] = "foobar"
        self.request.POST["title"] = "Foobar"
        self.request.POST["status"] = "open"
        self.request.POST["description"] = "Foobar"
        self.request.POST["agreements"] = "I agree"
        self.request.POST["settings"] = "foobar"
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = board_new_post(self.request)
        self.assertEqual(self.dbsession.query(Board).count(), 0)
        self.assertEqual(response["form"].slug.data, "foobar")
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].status.data, "open")
        self.assertEqual(response["form"].description.data, "Foobar")
        self.assertEqual(response["form"].agreements.data, "I agree")
        self.assertEqual(response["form"].settings.data, "foobar")
        self.assertDictEqual(
            response["form"].errors, {"settings": ["Must be a valid JSON."]}
        )

    def test_board_get(self):
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.admin import board_get
        from . import mock_service

        board = self._make(Board(title="Foobar", slug="foobar"))
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "foobar"
        response = board_get(request)
        self.assertEqual(response["board"], board)

    def test_board_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_get
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "foobar"
        with self.assertRaises(NoResultFound):
            board_get(request)

    def test_board_edit_get(self):
        from ..forms import AdminBoardForm
        from ..interfaces import IBoardQueryService
        from ..models import Board
        from ..services import BoardQueryService
        from ..views.admin import board_edit_get
        from . import mock_service

        board = self._make(
            Board(
                title="Foobar",
                slug="foobar",
                description="Foobar",
                agreements="I agree",
                settings={"name": "Nameless Foobar"},
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "foobar"
        response = board_edit_get(request)
        self.assertEqual(response["board"], board)
        self.assertIsInstance(response["form"], AdminBoardForm)
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].status.data, "open")
        self.assertEqual(response["form"].description.data, "Foobar")
        self.assertEqual(response["form"].agreements.data, "I agree")
        self.assertEqual(
            response["form"].settings.data,
            "{\n"
            + '    "expire_duration": 0,\n'
            + '    "max_posts": 1000,\n'
            + '    "name": "Nameless Foobar",\n'
            + '    "post_delay": 10,\n'
            + '    "use_ident": true\n'
            + "}",
        )

    def test_board_edit_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_edit_get
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "GET"
        request.matchdict["board"] = "foobar"
        with self.assertRaises(NoResultFound):
            board_edit_get(request)

    def test_board_edit_post(self):
        from ..interfaces import IBoardQueryService, IBoardUpdateService
        from ..models import Board
        from ..services import BoardQueryService, BoardUpdateService
        from ..views.admin import board_edit_post
        from . import mock_service

        board = self._make(Board(slug="baz", title="Baz"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IBoardUpdateService: BoardUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "baz"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["title"] = "Foobar"
        request.POST["status"] = "locked"
        request.POST["description"] = "Foobar"
        request.POST["agreements"] = "I agree"
        request.POST["settings"] = '{"name":"Nameless Foobar"}'
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_board", "/admin/boards/{board}")
        response = board_edit_post(request)
        self.assertEqual(response.location, "/admin/boards/baz")
        self.assertEqual(board.title, "Foobar")
        self.assertEqual(board.status, "locked")
        self.assertEqual(board.description, "Foobar")
        self.assertEqual(board.agreements, "I agree")
        self.assertEqual(
            board.settings,
            {
                "expire_duration": 0,
                "max_posts": 1000,
                "name": "Nameless Foobar",
                "post_delay": 10,
                "use_ident": True,
            },
        )

    def test_board_edit_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IBoardQueryService
        from ..services import BoardQueryService
        from ..views.admin import board_edit_post
        from . import mock_service

        request = mock_service(
            self.request, {IBoardQueryService: BoardQueryService(self.dbsession)}
        )
        request.method = "POST"
        request.matchdict["board"] = "notexists"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            board_edit_post(request)

    def test_board_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..models import Board
        from ..views.admin import board_edit_post

        board = self._make(Board(slug="baz", title="Baz"))
        self.dbsession.commit()
        self.request.method = "POST"
        self.request.matchdict["board"] = board.slug
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["title"] = "Foobar"
        self.request.POST["status"] = "open"
        self.request.POST["description"] = "Foobar"
        self.request.POST["agreements"] = "I agree"
        self.request.POST["settings"] = "{}"
        with self.assertRaises(BadCSRFToken):
            board_edit_post(self.request)

    def test_board_edit_post_invalid_status(self):
        from ..interfaces import IBoardQueryService, IBoardUpdateService
        from ..models import Board
        from ..services import BoardQueryService, BoardUpdateService
        from ..views.admin import board_edit_post
        from . import mock_service

        board = self._make(Board(slug="baz", title="Baz"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IBoardUpdateService: BoardUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "baz"
        request.POST = MultiDict([])
        request.POST["title"] = "Foobar"
        request.POST["status"] = "foobar"
        request.POST["description"] = "Foobar"
        request.POST["agreements"] = "I agree"
        request.POST["settings"] = '{"name":"Nameless Foobar"}'
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_board", "/admin/boards/{board}")
        response = board_edit_post(request)
        self.assertEqual(board.status, "open")
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].status.data, "foobar")
        self.assertEqual(response["form"].description.data, "Foobar")
        self.assertEqual(response["form"].agreements.data, "I agree")
        self.assertEqual(response["form"].settings.data, '{"name":"Nameless Foobar"}')
        self.assertDictEqual(
            response["form"].errors, {"status": ["Not a valid choice"]}
        )

    def test_board_edit_post_invalid_settings(self):
        from ..interfaces import IBoardQueryService, IBoardUpdateService
        from ..models import Board
        from ..services import BoardQueryService, BoardUpdateService
        from ..views.admin import board_edit_post
        from . import mock_service

        board = self._make(Board(slug="baz", title="Baz"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IBoardQueryService: BoardQueryService(self.dbsession),
                IBoardUpdateService: BoardUpdateService(self.dbsession),
            },
        )
        request.method = "POST"
        request.matchdict["board"] = "baz"
        request.POST = MultiDict([])
        request.POST["title"] = "Foobar"
        request.POST["status"] = "locked"
        request.POST["description"] = "Foobar"
        request.POST["agreements"] = "I agree"
        request.POST["settings"] = "invalid"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_board", "/admin/boards/{board}")
        response = board_edit_post(request)
        self.assertEqual(board.status, "open")
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].status.data, "locked")
        self.assertEqual(response["form"].description.data, "Foobar")
        self.assertEqual(response["form"].agreements.data, "I agree")
        self.assertEqual(response["form"].settings.data, "invalid")
        self.assertDictEqual(
            response["form"].errors, {"settings": ["Must be a valid JSON."]}
        )
