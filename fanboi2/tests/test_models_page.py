import unittest

from . import ModelSessionMixin


class TestPageModel(ModelSessionMixin, unittest.TestCase):
    def test_versioned(self):
        from ..models import Page

        PageHistory = Page.__history_mapper__.class_
        page = self._make(Page(title="Foo", slug="foo", body="Foobar"))
        self.dbsession.commit()
        self.assertEqual(page.version, 1)
        self.assertEqual(self.dbsession.query(PageHistory).count(), 0)
        page.body = "Foobar baz updated"
        self.dbsession.add(page)
        self.dbsession.commit()
        self.assertEqual(page.version, 2)
        self.assertEqual(self.dbsession.query(PageHistory).count(), 1)
        page_1 = self.dbsession.query(PageHistory).filter_by(version=1).one()
        self.assertEqual(page_1.id, page.id)
        self.assertEqual(page_1.title, "Foo")
        self.assertEqual(page_1.slug, "foo")
        self.assertEqual(page_1.body, "Foobar")
        self.assertEqual(page_1.version, 1)
        self.assertEqual(page_1.change_type, "update")
        self.assertIsNotNone(page_1.changed_at)
        self.assertIsNotNone(page_1.created_at)
        self.assertIsNone(page_1.updated_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from ..models import Page

        PageHistory = Page.__history_mapper__.class_
        page = self._make(Page(title="Foo", slug="foo", body="Foobar"))
        self.dbsession.commit()
        self.dbsession.delete(page)
        self.dbsession.commit()
        self.assertTrue(inspect(page).was_deleted)
        self.assertEqual(self.dbsession.query(PageHistory).count(), 1)
        page_1 = self.dbsession.query(PageHistory).filter_by(version=1).one()
        self.assertEqual(page_1.id, page.id)
        self.assertEqual(page_1.title, "Foo")
        self.assertEqual(page_1.slug, "foo")
        self.assertEqual(page_1.body, "Foobar")
        self.assertEqual(page_1.version, 1)
        self.assertEqual(page_1.change_type, "delete")
        self.assertIsNotNone(page_1.changed_at)
        self.assertIsNotNone(page_1.created_at)
        self.assertIsNone(page_1.updated_at)
