import unittest
import unittest.mock

from . import IntegrationMixin


class TestIntegrationPage(IntegrationMixin, unittest.TestCase):
    def test_page_show(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.pages import page_show
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(Page(title="Foo", body="Foo", slug="foo"))
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = page.slug
        response = page_show(request)
        self.assertEqual(response["page"], page)

    def test_page_show_internal(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.pages import page_show
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(title="Foo", body="Foo", slug="foo", namespace="internal")
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = page.slug
        with self.assertRaises(NoResultFound):
            page_show(request)

    def test_page_show_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.pages import page_show
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        request.matchdict["page"] = "notexists"
        with self.assertRaises(NoResultFound):
            page_show(request)

    def test_page_robots(self):
        from ..interfaces import IPageQueryService
        from ..models import Page
        from ..services import PageQueryService
        from ..views.pages import robots_show
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(title="Robots", slug="global/robots", namespace="internal", body="Hi")
        )
        self.dbsession.commit()
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        self.assertEqual(robots_show(request).body, b"Hi")

    def test_page_robots_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..interfaces import IPageQueryService
        from ..services import PageQueryService
        from ..views.pages import robots_show
        from . import mock_service, make_cache_region

        cache_region = make_cache_region({})
        request = mock_service(
            self.request,
            {IPageQueryService: PageQueryService(self.dbsession, cache_region)},
        )
        request.method = "GET"
        with self.assertRaises(NoResultFound):
            robots_show(request)
