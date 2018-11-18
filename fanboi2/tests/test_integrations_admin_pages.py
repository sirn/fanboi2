import unittest
import unittest.mock

from webob.multidict import MultiDict

from . import IntegrationMixin


class TestIntegrationAdminPages(IntegrationMixin, unittest.TestCase):
    def test_pages_get(self):
        from sqlalchemy import inspect
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import pages_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        internal_pages = (("foo", "none"), ("bar", "markdown"), ("baz", "html"))

        class _WrappedPageQueryService(PageQueryService):
            def list_internal(self):
                return super(_WrappedPageQueryService, self).list_internal(
                    _internal_pages=internal_pages
                )

        page1 = self._make(
            Page(title="Foo", body="Hi", slug="test1", namespace="public")
        )
        page2 = self._make(
            Page(
                title="Bar",
                body="Hi",
                slug="test2",
                formatter="html",
                namespace="public",
            )
        )
        page3 = self._make(
            Page(
                title="Baz",
                body="Hi",
                slug="test3",
                formatter="none",
                namespace="public",
            )
        )
        self._make(
            Page(
                title="Test",
                body="Hi",
                slug="test4",
                formatter="markdown",
                namespace="internal",
            )
        )
        self._make(Page(title="bar", slug="bar", body="Hello", namespace="internal"))
        self._make(Page(title="hoge", slug="hoge", body="Hoge", namespace="internal"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        response = pages_get(request)
        self.assertEqual(response["pages"], [page2, page3, page1])
        self.assertEqual(response["pages_internal"][0].slug, "bar")
        self.assertEqual(response["pages_internal"][1].slug, "baz")
        self.assertEqual(response["pages_internal"][2].slug, "foo")
        self.assertEqual(response["pages_internal"][3].slug, "hoge")
        self.assertTrue(inspect(response["pages_internal"][0]).persistent)
        self.assertFalse(inspect(response["pages_internal"][1]).persistent)
        self.assertFalse(inspect(response["pages_internal"][2]).persistent)
        self.assertTrue(inspect(response["pages_internal"][3]).persistent)

    def test_page_new_get(self):
        from ..forms import AdminPublicPageNewForm
        from ..views.admin import page_new_get

        self.request.method = "GET"
        response = page_new_get(self.request)
        self.assertIsInstance(response["form"], AdminPublicPageNewForm)

    def test_page_new_post(self):
        from ..interfaces import IPageCreateService
        from ..models import Page
        from ..services import PageCreateService
        from ..views.admin import page_new_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageCreateService: PageCreateService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict({})
        request.POST["title"] = "Foobar"
        request.POST["slug"] = "foobar"
        request.POST["body"] = "**Hello, world!**"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page", "/admin/pages/{page}")
        response = page_new_post(request)
        page = self.dbsession.query(Page).first()
        self.assertEqual(response.location, "/admin/pages/foobar")
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        self.assertEqual(page.slug, "foobar")
        self.assertEqual(page.title, "Foobar")
        self.assertEqual(page.body, "**Hello, world!**")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_page_new_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["title"] = "Foobar"
        self.request.POST["slug"] = "foobar"
        self.request.POST["body"] = "**Hello, world!**"
        with self.assertRaises(BadCSRFToken):
            page_new_post(self.request)

    def test_page_new_post_invalid_title(self):
        from ..forms import AdminPublicPageNewForm
        from ..models import Page
        from ..views.admin import page_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["title"] = ""
        self.request.POST["slug"] = "foobar"
        self.request.POST["body"] = "**Hello, world!**"
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = page_new_post(self.request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)
        self.assertIsInstance(response["form"], AdminPublicPageNewForm)
        self.assertEqual(response["form"].title.data, "")
        self.assertEqual(response["form"].slug.data, "foobar")
        self.assertEqual(response["form"].body.data, "**Hello, world!**")
        self.assertDictEqual(
            response["form"].errors, {"title": ["This field is required."]}
        )

    def test_page_new_post_invalid_slug(self):
        from ..forms import AdminPublicPageNewForm
        from ..models import Page
        from ..views.admin import page_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["title"] = "Foobar"
        self.request.POST["slug"] = ""
        self.request.POST["body"] = "**Hello, world!**"
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = page_new_post(self.request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)
        self.assertIsInstance(response["form"], AdminPublicPageNewForm)
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].slug.data, "")
        self.assertEqual(response["form"].body.data, "**Hello, world!**")
        self.assertDictEqual(
            response["form"].errors, {"slug": ["This field is required."]}
        )

    def test_page_new_post_invalid_body(self):
        from ..forms import AdminPublicPageNewForm
        from ..models import Page
        from ..views.admin import page_new_post

        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict({})
        self.request.POST["title"] = "Foobar"
        self.request.POST["slug"] = "foobar"
        self.request.POST["body"] = ""
        self.request.POST["csrf_token"] = self.request.session.get_csrf_token()
        response = page_new_post(self.request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)
        self.assertIsInstance(response["form"], AdminPublicPageNewForm)
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].slug.data, "foobar")
        self.assertEqual(response["form"].body.data, "")
        self.assertDictEqual(
            response["form"].errors, {"body": ["This field is required."]}
        )

    def test_page_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "foobar"
        response = page_get(request)
        self.assertEqual(response["page"], page)

    def test_page_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "notexists"
        with self.assertRaises(NoResultFound):
            page_get(request)

    def test_page_edit_get(self):
        from ..forms import AdminPublicPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_edit_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "foobar"
        response = page_edit_get(request)
        self.assertEqual(response["page"], page)
        self.assertIsInstance(response["form"], AdminPublicPageForm)
        self.assertEqual(response["form"].title.data, "Foobar")
        self.assertEqual(response["form"].body.data, "**Hello**")

    def test_page_edit_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_edit_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "notexists"
        with self.assertRaises(NoResultFound):
            page_edit_get(request)

    def test_page_edit_post(self):
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IPageQueryService: PageQueryService(self.dbsession, cache_region),
                IPageUpdateService: PageUpdateService(self.dbsession, cache_region),
            },
        )
        request.method = "POST"
        request.matchdict["page"] = "foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["title"] = "Baz"
        request.POST["body"] = "**Baz**"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page", "/admin/pages/{page}")
        response = page_edit_post(request)
        self.assertEqual(response.location, "/admin/pages/foobar")
        self.assertEqual(page.slug, "foobar")
        self.assertEqual(page.title, "Baz")
        self.assertEqual(page.body, "**Baz**")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_page_edit_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "notexists"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            page_edit_post(request)

    def test_page_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..models import Page
        from ..views.admin import page_edit_post

        self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        self.request.method = "POST"
        self.request.matchdict["page"] = "notexists"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["title"] = "Baz"
        self.request.POST["body"] = "**Baz**"
        with self.assertRaises(BadCSRFToken):
            page_edit_post(self.request)

    def test_page_edit_post_invalid_title(self):
        from ..forms import AdminPublicPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["title"] = ""
        request.POST["body"] = "**Baz**"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = page_edit_post(request)
        self.assertIsInstance(response["form"], AdminPublicPageForm)
        self.assertEqual(response["form"].title.data, "")
        self.assertEqual(response["form"].body.data, "**Baz**")
        self.assertEqual(page.slug, "foobar")
        self.assertEqual(page.title, "Foobar")
        self.assertEqual(page.body, "**Hello**")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_page_edit_post_invalid_body(self):
        from ..forms import AdminPublicPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["title"] = "Baz"
        request.POST["body"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = page_edit_post(request)
        self.assertIsInstance(response["form"], AdminPublicPageForm)
        self.assertEqual(response["form"].title.data, "Baz")
        self.assertEqual(response["form"].body.data, "")
        self.assertEqual(page.slug, "foobar")
        self.assertEqual(page.title, "Foobar")
        self.assertEqual(page.body, "**Hello**")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_page_delete_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_delete_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "foobar"
        response = page_delete_get(request)
        self.assertEqual(response["page"], page)

    def test_page_delete_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_delete_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "notexists"
        with self.assertRaises(NoResultFound):
            page_delete_get(request)

    def test_page_delete_post(self):
        from ..interfaces import IPageDeleteService
        from ..models import Page
        from ..services import PageDeleteService
        from ..views.admin import page_delete_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Hello**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageDeleteService: PageDeleteService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_pages", "/admin/pages")
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        response = page_delete_post(request)
        self.assertEqual(response.location, "/admin/pages")
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_delete_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageDeleteService
        from ..services import PageDeleteService
        from ..views.admin import page_delete_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageDeleteService: PageDeleteService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "notexists"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            page_delete_post(request)

    def test_page_delete_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_delete_post

        self.request.method = "POST"
        self.request.matchdict["page"] = "notexists"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        with self.assertRaises(BadCSRFToken):
            page_delete_post(self.request)

    def test_page_internal_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page = self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        response = page_internal_get(request)
        self.assertEqual(response["page_slug"], "global/foobar")
        self.assertEqual(response["page"], page)

    def test_page_internal_get_not_found(self):
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/notexists", "none"),)
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/notexists"
        response = page_internal_get(request)
        self.assertEqual(response["page_slug"], "global/notexists")
        self.assertIsNone(response["page"])

    def test_page_internal_get_not_allowed(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=tuple()
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        with self.assertRaises(HTTPNotFound):
            page_internal_get(request)

    def test_page_internal_edit_get(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page = self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        response = page_internal_edit_get(request)
        self.assertIsInstance(response["form"], AdminPageForm)
        self.assertEqual(response["form"].body.data, "<em>Hello</em>")
        self.assertEqual(response["page_slug"], "global/foobar")
        self.assertEqual(response["page"], page)

    def test_page_internal_edit_get_auto_create(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        response = page_internal_edit_get(request)
        self.assertIsInstance(response["form"], AdminPageForm)
        self.assertEqual(response["form"].body.data, None)
        self.assertEqual(response["page_slug"], "global/foobar")
        self.assertIsNone(response["page"])

    def test_page_internal_edit_not_allowed(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=tuple()
                )

        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/notallowed"
        with self.assertRaises(HTTPNotFound):
            page_internal_edit_get(request)

    def test_page_internal_edit_post(self):
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region()

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page = self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IPageQueryService: _WrappedPageQueryService(
                    self.dbsession, cache_region
                ),
                IPageUpdateService: PageUpdateService(self.dbsession, cache_region),
            },
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = "<em>World</em>"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page_internal", "/admin/pages_i/{page}")
        response = page_internal_edit_post(request)
        self.assertEqual(response.location, "/admin/pages_i/global/foobar")
        self.assertEqual(page.slug, "global/foobar")
        self.assertEqual(page.title, "global/foobar")
        self.assertEqual(page.body, "<em>World</em>")
        self.assertEqual(page.namespace, "internal")
        self.assertEqual(page.formatter, "html")

    def test_page_internal_edit_post_auto_create(self):
        from ..interfaces import IPageQueryService, IPageCreateService
        from ..models import Page
        from ..services import PageQueryService, PageCreateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageCreateService(PageCreateService):
            def create_internal(self, slug, body):
                return super(_WrappedPageCreateService, self).create_internal(
                    slug, body, _internal_pages=(("global/foobar", "html"),)
                )

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        request = mock_service(
            self.request,
            {
                IPageQueryService: _WrappedPageQueryService(
                    self.dbsession, cache_region
                ),
                IPageCreateService: _WrappedPageCreateService(
                    self.dbsession, cache_region
                ),
            },
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = "<em>World</em>"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page_internal", "/admin/pages_i/{page}")
        response = page_internal_edit_post(request)
        self.assertEqual(response.location, "/admin/pages_i/global/foobar")
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        page = self.dbsession.query(Page).first()
        self.assertEqual(page.slug, "global/foobar")
        self.assertEqual(page.title, "global/foobar")
        self.assertEqual(page.body, "<em>World</em>")
        self.assertEqual(page.namespace, "internal")
        self.assertEqual(page.formatter, "html")

    def test_page_internal_edit_post_not_allowed(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=tuple()
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = "<em>World</em>"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(HTTPNotFound):
            page_internal_edit_post(request)
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_internal_edit_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_internal_edit_post

        self.request.method = "GET"
        self.request.matchdict["page"] = "global/foobar"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        self.request.POST["body"] = "<em>World</em>"
        with self.assertRaises(BadCSRFToken):
            page_internal_edit_post(self.request)

    def test_page_internal_edit_post_invalid_body(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page = self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {
                IPageQueryService: _WrappedPageQueryService(
                    self.dbsession, cache_region
                ),
                IPageUpdateService: PageUpdateService(self.dbsession, cache_region),
            },
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = page_internal_edit_post(request)
        self.assertIsInstance(response["form"], AdminPageForm)
        self.assertEqual(response["form"].body.data, "")
        self.assertEqual(response["form"].errors, {"body": ["This field is required."]})
        self.assertEqual(response["page_slug"], "global/foobar")
        self.assertEqual(response["page"], page)
        self.assertEqual(page.slug, "global/foobar")
        self.assertEqual(page.title, "global/foobar")
        self.assertEqual(page.body, "<em>Hello</em>")
        self.assertEqual(page.namespace, "internal")
        self.assertEqual(page.formatter, "html")

    def test_page_internal_edit_post_auto_create_invalid_body(self):
        from ..forms import AdminPageForm
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = ""
        request.POST["csrf_token"] = request.session.get_csrf_token()
        response = page_internal_edit_post(request)
        self.assertIsInstance(response["form"], AdminPageForm)
        self.assertEqual(response["form"].body.data, "")
        self.assertEqual(response["form"].errors, {"body": ["This field is required."]})
        self.assertEqual(response["page_slug"], "global/foobar")
        self.assertIsNone(response["page"])
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_internal_edit_post_cache(self):
        from ..interfaces import IPageQueryService, IPageUpdateService
        from ..models import Page
        from ..services import PageQueryService, PageUpdateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region()

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page_query_svc = PageQueryService(self.dbsession, cache_region)
        self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            ),
            "<em>Hello</em>",
        )
        request = mock_service(
            self.request,
            {
                IPageQueryService: _WrappedPageQueryService(
                    self.dbsession, cache_region
                ),
                IPageUpdateService: PageUpdateService(self.dbsession, cache_region),
            },
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = "<em>World</em>"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page_internal", "/admin/pages_i/{page}")
        response = page_internal_edit_post(request)
        self.assertEqual(response.location, "/admin/pages_i/global/foobar")
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            ),
            "<em>World</em>",
        )

    def test_page_internal_edit_post_auto_create_cache(self):
        from ..interfaces import IPageQueryService, IPageCreateService
        from ..services import PageQueryService, PageCreateService
        from ..views.admin import page_internal_edit_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageCreateService(PageCreateService):
            def create_internal(self, slug, body):
                return super(_WrappedPageCreateService, self).create_internal(
                    slug, body, _internal_pages=(("global/foobar", "html"),)
                )

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page_query_svc = PageQueryService(self.dbsession, cache_region)
        self.assertIsNone(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            )
        )
        request = mock_service(
            self.request,
            {
                IPageQueryService: _WrappedPageQueryService(
                    self.dbsession, cache_region
                ),
                IPageCreateService: _WrappedPageCreateService(
                    self.dbsession, cache_region
                ),
            },
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["body"] = "<em>World</em>"
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_page_internal", "/admin/pages_i/{page}")
        response = page_internal_edit_post(request)
        self.assertEqual(response.location, "/admin/pages_i/global/foobar")
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            ),
            "<em>World</em>",
        )

    def test_page_internal_delete_get(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.admin import page_internal_delete_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/foobar", "html"),)
                )

        page = self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        response = page_internal_delete_get(request)
        self.assertEqual(response["page"], page)

    def test_page_internal_delete_get_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_delete_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=(("global/notexists", "none"),)
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/notexists"
        with self.assertRaises(NoResultFound):
            page_internal_delete_get(request)

    def test_page_internal_delete_get_not_allowed(self):
        from pyramid.httpexceptions import HTTPNotFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.admin import page_internal_delete_get
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})

        class _WrappedPageQueryService(PageQueryService):
            def internal_page_from_slug(self, slug):
                return super(_WrappedPageQueryService, self).internal_page_from_slug(
                    slug, _internal_pages=tuple()
                )

        request = mock_service(
            self.request,
            {IPageQueryService: _WrappedPageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "global/foobar"
        with self.assertRaises(HTTPNotFound):
            page_internal_delete_get(request)

    def test_page_internal_delete_post(self):
        from ..interfaces import IPageDeleteService
        from ..models import Page
        from ..services import PageDeleteService
        from ..views.admin import page_internal_delete_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageDeleteService: PageDeleteService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_pages", "/admin/pages")
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        response = page_internal_delete_post(request)
        self.assertEqual(response.location, "/admin/pages")
        self.assertEqual(self.dbsession.query(Page).count(), 0)

    def test_page_internal_delete_post_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageDeleteService
        from ..services import PageDeleteService
        from ..views.admin import page_internal_delete_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageDeleteService: PageDeleteService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "global/notexists"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        with self.assertRaises(NoResultFound):
            page_internal_delete_post(request)

    def test_page_internal_delete_post_bad_csrf(self):
        from pyramid.csrf import BadCSRFToken
        from ..views.admin import page_internal_delete_post

        self.request.method = "POST"
        self.request.matchdict["page"] = "global/notexists"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = MultiDict([])
        with self.assertRaises(BadCSRFToken):
            page_internal_delete_post(self.request)

    def test_page_internal_delete_post_cache(self):
        from ..interfaces import IPageDeleteService
        from ..models import Page
        from ..services import PageDeleteService, PageQueryService
        from ..views.admin import page_internal_delete_post
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Hello</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        page_query_svc = PageQueryService(self.dbsession, cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            ),
            "<em>Hello</em>",
        )
        request = mock_service(
            self.request,
            {IPageDeleteService: PageDeleteService(self.dbsession, cache_region)},
        )
        request.method = "POST"
        request.matchdict["page"] = "global/foobar"
        request.content_type = "application/x-www-form-urlencoded"
        request.POST = MultiDict([])
        request.POST["csrf_token"] = request.session.get_csrf_token()
        self.config.add_route("admin_pages", "/admin/pages")
        response = page_internal_delete_post(request)
        self.assertEqual(response.location, "/admin/pages")
        self.assertIsNone(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            )
        )
