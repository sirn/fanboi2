import unittest
import unittest.mock

from sqlalchemy.orm.exc import NoResultFound

from . import ModelSessionMixin


class TestPageCreateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import PageCreateService

        return PageCreateService

    def test_create(self):
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_create_svc = self._get_target_class()(self.dbsession, cache_region)
        page = page_create_svc.create(
            "foobar", title="Foobar", body="**Hello, world!**"
        )
        self.assertEqual(page.slug, "foobar")
        self.assertEqual(page.title, "Foobar")
        self.assertEqual(page.body, "**Hello, world!**")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_create_internal(self):
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_create_svc = self._get_target_class()(self.dbsession, cache_region)
        page = page_create_svc.create_internal(
            "global/foo",
            body="<em>Hello, world!</em>",
            _internal_pages=(("global/foo", "html"),),
        )
        self.assertEqual(page.slug, "global/foo")
        self.assertEqual(page.title, "global/foo")
        self.assertEqual(page.body, "<em>Hello, world!</em>")
        self.assertEqual(page.namespace, "internal")
        self.assertEqual(page.formatter, "html")

    def test_create_internal_not_allowed(self):
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_create_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(ValueError):
            page_create_svc.create_internal(
                "global/foo", body="<em>Hello, world!</em>", _internal_pages=tuple()
            )

    def test_create_internal_cache(self):
        from ..models import Page
        from ..services import PageQueryService
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_query_svc = PageQueryService(self.dbsession, cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foo", _internal_pages=(("global/foo", "html"),)
            ),
            None,
        )
        page_create_svc = self._get_target_class()(self.dbsession, cache_region)
        page_create_svc.create_internal(
            "global/foo",
            body="<em>Hello, world!</em>",
            _internal_pages=(("global/foo", "html"),),
        )
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foo", _internal_pages=(("global/foo", "html"),)
            ),
            "<em>Hello, world!</em>",
        )


class TestPageDeleteService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import PageDeleteService

        return PageDeleteService

    def test_delete(self):
        from sqlalchemy import inspect
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        page1 = self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Foobar**",
                namespace="public",
                formatter="markdown",
            )
        )
        page2 = self._make(
            Page(
                slug="foobar2",
                title="Foobar2",
                body="**Foobar2**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        page_delete_svc = self._get_target_class()(self.dbsession, cache_region)
        page_delete_svc.delete("foobar")
        self.dbsession.flush()
        self.assertTrue(inspect(page1).was_deleted)
        self.assertFalse(inspect(page2).was_deleted)

    def test_delete_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_delete_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(NoResultFound):
            page_delete_svc.delete("notexists")

    def test_delete_wrong_namespace(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="global/foo",
                title="global/foo",
                body="<em>Foobar</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        page_delete_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(NoResultFound):
            page_delete_svc.delete("global/foo")

    def test_delete_internal(self):
        from sqlalchemy import inspect
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        page1 = self._make(
            Page(
                slug="global/foo",
                title="global/foo",
                body="<em>Foobar</em>",
                namespace="internal",
                formatter="html",
            )
        )
        page2 = self._make(
            Page(
                slug="global/bar",
                title="global/bar",
                body="<em>Baz</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        page_delete_svc = self._get_target_class()(self.dbsession, cache_region)
        page_delete_svc.delete_internal("global/foo")
        self.dbsession.flush()
        self.assertTrue(inspect(page1).was_deleted)
        self.assertFalse(inspect(page2).was_deleted)

    def test_delete_internal_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_delete_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(NoResultFound):
            page_delete_svc.delete_internal("global/notexists")

    def test_delete_internal_wrong_namespace(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Foobar**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(Page).count(), 1)
        page_delete_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(NoResultFound):
            page_delete_svc.delete_internal("foobar")

    def test_delete_internal_cache(self):
        from sqlalchemy import inspect
        from ..models import Page
        from ..services import PageQueryService
        from . import make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="global/foo",
                title="global/foo",
                body="<em>Foobar</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        page_query_svc = PageQueryService(self.dbsession, cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foo", _internal_pages=(("global/foo", "html"),)
            ),
            "<em>Foobar</em>",
        )
        page_delete_svc = self._get_target_class()(self.dbsession, cache_region)
        page_delete_svc.delete_internal("global/foo")
        self.dbsession.flush()
        self.assertTrue(inspect(page).was_deleted)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foo", _internal_pages=(("global/foo", "html"),)
            ),
            None,
        )


class TestPageQueryService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import PageQueryService

        return PageQueryService

    def test_list_public(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
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
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertEqual(page_query_svc.list_public(), [page2, page3, page1])

    def test_list_internal(self):
        from sqlalchemy import inspect
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        internal_pages = (("foo", "none"), ("bar", "markdown"), ("baz", "html"))
        self._make(Page(title="bar", slug="bar", body="Hello", namespace="internal"))
        self._make(Page(title="hoge", slug="hoge", body="Hoge", namespace="internal"))
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(self.dbsession, cache_region)
        pages = page_query_svc.list_internal(_internal_pages=internal_pages)
        self.assertEqual(pages[0].slug, "bar")
        self.assertTrue(inspect(pages[0]).persistent)
        self.assertEqual(pages[1].slug, "baz")
        self.assertFalse(inspect(pages[1]).persistent)
        self.assertEqual(pages[2].slug, "foo")
        self.assertFalse(inspect(pages[2]).persistent)
        self.assertEqual(pages[3].slug, "hoge")
        self.assertTrue(inspect(pages[3]).persistent)

    def test_public_page_from_slug(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(title="Test", body="Hello", slug="test", namespace="public")
        )
        self._make(
            Page(title="Test", body="Internal Test", slug="test", namespace="internal")
        )
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertEqual(page_query_svc.public_page_from_slug("test"), page)

    def test_public_page_from_slug_not_found(self):
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_query_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(NoResultFound):
            page_query_svc.public_page_from_slug("notfound")

    def test_internal_page_from_slug(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(Page(title="Test", body="Hello", slug="test", namespace="public"))
        page = self._make(
            Page(title="Test", body="Internal Test", slug="test", namespace="internal")
        )
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertEqual(
            page_query_svc.internal_page_from_slug(
                "test", _internal_pages=(("test", "none"),)
            ),
            page,
        )

    def test_internal_page_from_slug_not_found(self):
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_query_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(NoResultFound):
            page_query_svc.internal_page_from_slug(
                "notfound", _internal_pages=(("notfound", "none"),)
            )

    def test_internal_page_from_slug_not_allowed(self):
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_query_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(ValueError):
            page_query_svc.internal_page_from_slug(
                "notallowed", _internal_pages=tuple()
            )

    def test_internal_body_from_slug(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="foo/test",
                title="foo/test",
                body="<em>Test</em>",
                formatter="html",
                namespace="internal",
            )
        )
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "foo/test", _internal_pages=(("foo/test", "html"),)
            ),
            "<em>Test</em>",
        )

    def test_internal_body_from_slug_not_found(self):
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_query_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertIsNone(
            page_query_svc.internal_body_from_slug(
                "foo/test", _internal_pages=(("foo/test", "none"),)
            )
        )

    def test_internal_body_from_slug_not_allowed(self):
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_query_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(ValueError):
            page_query_svc.internal_body_from_slug("foo/test", _internal_pages=tuple())

    def test_internal_body_from_slug_cache(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        page = self._make(
            Page(
                slug="foo/test",
                title="foo/test",
                body="<em>Test</em>",
                formatter="html",
                namespace="internal",
            )
        )
        self.dbsession.commit()
        page_query_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "foo/test", _internal_pages=(("foo/test", "html"),)
            ),
            "<em>Test</em>",
        )
        self.dbsession.delete(page)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "foo/test", _internal_pages=(("foo/test", "html"),)
            ),
            "<em>Test</em>",
        )


class TestPageUpdateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import PageUpdateService

        return PageUpdateService

    def test_update(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Foobar**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(self.dbsession, cache_region)
        page = page_update_svc.update("foobar", title="Baz", body="*Baz*")
        self.assertEqual(page.slug, "foobar")
        self.assertEqual(page.title, "Baz")
        self.assertEqual(page.body, "*Baz*")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_update_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_update_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(NoResultFound):
            page_update_svc.update("notexists", title="Baz", body="*Baz*")

    def test_update_wrong_namespace(self):
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="global/foo",
                title="global/foo",
                body="<em>Foobar</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(NoResultFound):
            page_update_svc.update("global/foo", title="Baz", body="*Baz*")

    def test_update_none(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Foobar**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(self.dbsession, cache_region)
        page = page_update_svc.update("foobar")
        self.assertEqual(page.slug, "foobar")
        self.assertEqual(page.title, "Foobar")
        self.assertEqual(page.body, "**Foobar**")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_update_not_whitelisted(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Foobar**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(self.dbsession, cache_region)
        page = page_update_svc.update("foobar", namespace="internal", formatter="html")
        self.assertEqual(page.namespace, "public")
        self.assertEqual(page.formatter, "markdown")

    def test_update_internal(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Foobar</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(self.dbsession, cache_region)
        page = page_update_svc.update_internal("global/foobar", body="<em>Baz</em>")
        self.assertEqual(page.slug, "global/foobar")
        self.assertEqual(page.title, "global/foobar")
        self.assertEqual(page.body, "<em>Baz</em>")
        self.assertEqual(page.namespace, "internal")
        self.assertEqual(page.formatter, "html")

    def test_update_internal_not_found(self):
        from sqlalchemy.orm.exc import NoResultFound
        from . import make_cache_region

        cache_region = make_cache_region({})
        page_update_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(NoResultFound):
            page_update_svc.update_internal("global/notexists", body="<em>Baz</em>")

    def test_update_internal_wrong_namespace(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="foobar",
                title="Foobar",
                body="**Foobar**",
                namespace="public",
                formatter="markdown",
            )
        )
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(NoResultFound):
            page_update_svc.update_internal("global/foobar", body="<em>Baz</em>")

    def test_update_internal_none(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Foobar</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(self.dbsession, cache_region)
        page = page_update_svc.update_internal("global/foobar")
        self.assertEqual(page.slug, "global/foobar")
        self.assertEqual(page.title, "global/foobar")
        self.assertEqual(page.body, "<em>Foobar</em>")
        self.assertEqual(page.namespace, "internal")
        self.assertEqual(page.formatter, "html")

    def test_update_internal_not_whitelisted(self):
        from ..models import Page
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Foobar</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        page_update_svc = self._get_target_class()(self.dbsession, cache_region)
        page = page_update_svc.update_internal(
            "global/foobar", title="Foobar", namespace="public", formatter="markdown"
        )
        self.assertEqual(page.slug, "global/foobar")
        self.assertEqual(page.title, "global/foobar")
        self.assertEqual(page.body, "<em>Foobar</em>")
        self.assertEqual(page.namespace, "internal")
        self.assertEqual(page.formatter, "html")

    def test_update_internal_cache(self):
        from ..models import Page
        from ..services import PageQueryService
        from . import make_cache_region

        cache_region = make_cache_region({})
        self._make(
            Page(
                slug="global/foobar",
                title="global/foobar",
                body="<em>Foobar</em>",
                namespace="internal",
                formatter="html",
            )
        )
        self.dbsession.commit()
        page_query_svc = PageQueryService(self.dbsession, cache_region)
        page_update_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            ),
            "<em>Foobar</em>",
        )
        page_update_svc.update_internal("global/foobar", body="<em>Baz</em>")
        self.assertEqual(
            page_query_svc.internal_body_from_slug(
                "global/foobar", _internal_pages=(("global/foobar", "html"),)
            ),
            "<em>Baz</em>",
        )
