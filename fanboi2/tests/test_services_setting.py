import unittest
import unittest.mock

from . import ModelSessionMixin


class TestSettingQueryService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import SettingQueryService

        return SettingQueryService

    def test_init(self):
        from . import make_cache_region

        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertEqual(setting_query_svc.dbsession, self.dbsession)
        self.assertEqual(setting_query_svc.cache_region, cache_region)

    def test_list_all(self):
        from ..models import Setting
        from . import make_cache_region

        cache_region = make_cache_region()
        self._make(Setting(key="app.test", value="test"))
        self._make(Setting(key="bax", value=32))
        self.dbsession.commit()
        setting_query_svc = self._get_target_class()(self.dbsession, cache_region)
        result = setting_query_svc.list_all(
            _default={"foo": None, "bar": "baz", "bax": 1}
        )
        self.assertEqual(result, [("bar", "baz"), ("bax", 32), ("foo", None)])

    def test_value_from_key(self):
        from . import make_cache_region
        from ..models import Setting

        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(self.dbsession, cache_region)
        self._make(Setting(key="app.test", value="test"))
        self.dbsession.commit()
        self.assertEqual(
            setting_query_svc.value_from_key("app.test", _default={}), "test"
        )

    def test_value_from_key_safe_keys(self):
        from . import make_cache_region

        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(self.dbsession, cache_region)
        with self.assertRaises(KeyError):
            setting_query_svc.value_from_key("app.test", safe_keys=True, _default={})

    def test_value_from_key_use_cache(self):
        from . import make_cache_region
        from ..models import Setting

        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertIsNone(
            setting_query_svc.value_from_key("app.test", use_cache=True, _default={})
        )
        self._make(Setting(key="app.test", value="test"))
        self.dbsession.commit()
        self.assertIsNone(
            setting_query_svc.value_from_key("app.test", use_cache=True, _default={})
        )
        self.assertEqual(
            setting_query_svc.value_from_key("app.test", use_cache=False, _default={}),
            "test",
        )

    def test_value_from_key_not_found(self):
        from . import make_cache_region

        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertIsNone(setting_query_svc.value_from_key("app.test", _default={}))

    def test_reload_cache(self):
        from . import make_cache_region
        from ..models import Setting

        cache_region = make_cache_region()
        setting_query_svc = self._get_target_class()(self.dbsession, cache_region)
        self._make(Setting(key="app.test", value="test"))
        self.dbsession.commit()
        self.assertEqual(
            setting_query_svc.value_from_key("app.test", _default={}), "test"
        )
        setting = self.dbsession.query(Setting).get("app.test")
        setting.value = "foobar"
        self.dbsession.add(setting)
        self.dbsession.commit()
        self.assertEqual(
            setting_query_svc.value_from_key("app.test", _default={}), "test"
        )
        setting_query_svc.reload_cache("app.test")
        self.assertEqual(
            setting_query_svc.value_from_key("app.test", _default={}), "foobar"
        )


class TestSettingUpdateService(ModelSessionMixin, unittest.TestCase):
    def _get_target_class(self):
        from ..services import SettingUpdateService

        return SettingUpdateService

    def test_update(self):
        from . import make_cache_region
        from ..models import Setting
        from ..services import SettingQueryService

        self._make(Setting(key="app.test", value="test"))
        self.dbsession.commit()
        cache_region = make_cache_region()
        setting_query_svc = SettingQueryService(self.dbsession, cache_region)
        setting_update_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertEqual(setting_query_svc.value_from_key("app.test"), "test")
        setting = setting_update_svc.update("app.test", "test2")
        self.assertEqual(setting.key, "app.test")
        self.assertEqual(setting.value, "test2")
        self.assertEqual(setting_query_svc.value_from_key("app.test"), "test2")

    def test_update_insert(self):
        from . import make_cache_region
        from ..services import SettingQueryService

        cache_region = make_cache_region()
        setting_query_svc = SettingQueryService(self.dbsession, cache_region)
        setting_update_svc = self._get_target_class()(self.dbsession, cache_region)
        self.assertIsNone(setting_query_svc.value_from_key("app.test"))
        setting = setting_update_svc.update("app.test", "test")
        self.assertEqual(setting.key, "app.test")
        self.assertEqual(setting.value, "test")
        self.assertEqual(setting_query_svc.value_from_key("app.test"), "test")

    def test_update_data_structure(self):
        from . import make_cache_region

        cache_region = make_cache_region()
        setting_update_svc = self._get_target_class()(self.dbsession, cache_region)
        setting = setting_update_svc.update("app.test", {"foo": "bar"})
        self.assertEqual(setting.key, "app.test")
        self.assertEqual(setting.value, {"foo": "bar"})
