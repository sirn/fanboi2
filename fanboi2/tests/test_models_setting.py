import unittest

from . import ModelSessionMixin


class TestSettingModel(ModelSessionMixin, unittest.TestCase):
    def test_versioned(self):
        from ..models import Setting

        SettingHistory = Setting.__history_mapper__.class_
        setting = self._make(Setting(key="foo", value="bar"))
        self.dbsession.commit()
        self.assertEqual(setting.version, 1)
        self.assertEqual(self.dbsession.query(SettingHistory).count(), 0)
        setting.value = "baz"
        self.dbsession.add(setting)
        self.dbsession.commit()
        self.assertEqual(setting.version, 2)
        self.assertEqual(self.dbsession.query(SettingHistory).count(), 1)
        setting_1 = self.dbsession.query(SettingHistory).filter_by(version=1).one()
        self.assertEqual(setting_1.key, "foo")
        self.assertEqual(setting_1.value, "bar")
        self.assertEqual(setting_1.version, 1)
        self.assertEqual(setting_1.change_type, "update")
        self.assertIsNotNone(setting_1.changed_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from ..models import Setting

        SettingHistory = Setting.__history_mapper__.class_
        setting = self._make(Setting(key="foo", value="bar"))
        self.dbsession.commit()
        self.dbsession.delete(setting)
        self.dbsession.commit()
        self.assertTrue(inspect(setting).was_deleted)
        self.assertEqual(self.dbsession.query(SettingHistory).count(), 1)
        setting_1 = self.dbsession.query(SettingHistory).filter_by(version=1).one()
        self.assertEqual(setting_1.key, "foo")
        self.assertEqual(setting_1.value, "bar")
        self.assertEqual(setting_1.version, 1)
        self.assertEqual(setting_1.change_type, "delete")
        self.assertIsNotNone(setting_1.changed_at)
