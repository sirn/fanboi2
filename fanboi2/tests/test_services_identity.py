import datetime
import unittest
import unittest.mock


class TestIdentityService(unittest.TestCase):
    def _get_target_class(self):
        from ..services import IdentityService

        return IdentityService

    def test_init(self):
        from . import DummyRedis

        redis_conn = DummyRedis()

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {"app.ident_size": 10}.get(key, None)

        identity_svc = self._get_target_class()(redis_conn, _DummySettingQueryService())
        self.assertEqual(identity_svc.redis_conn, redis_conn)
        self.assertEqual(identity_svc.ident_size, 10)

    def test_identity_for(self):
        from . import DummyRedis

        redis_conn = DummyRedis()

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {"app.ident_size": 10}.get(key, None)

        identity_svc = self._get_target_class()(redis_conn, _DummySettingQueryService())
        ident1 = identity_svc.identity_for(a="1", b="2")
        ident2 = identity_svc.identity_for(b="2", a="1")
        ident3 = identity_svc.identity_for(a="1", b="2", c="3")
        self.assertEqual(ident1, ident2)
        self.assertNotEqual(ident1, ident3)
        self.assertEqual(len(ident1), 10)
        self.assertEqual(len(ident3), 10)
        for _, v in redis_conn._expire.items():
            self.assertEqual(v, 86400)
        redis_conn._reset()
        ident4 = identity_svc.identity_for(a="1", b="2")
        self.assertNotEqual(ident1, ident4)

    def test_identity_for_length(self):
        from . import DummyRedis

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {"app.ident_size": 5}.get(key, None)

        redis_conn = DummyRedis()
        identity_svc = self._get_target_class()(redis_conn, _DummySettingQueryService())
        self.assertEqual(len(identity_svc.identity_for(a="1", b="2")), 5)

    def test_identity_with_tz_for(self):
        from . import DummyRedis

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {"app.ident_size": 10}.get(key, None)

        tz = "Asia/Bangkok"
        redis_conn = DummyRedis(datetime.datetime(2018, 12, 9, 17, 0, 0, 0, None))
        identity_svc = self._get_target_class()(redis_conn, _DummySettingQueryService())
        ident1 = identity_svc.identity_with_tz_for(tz, a="1", b="2")
        ident2 = identity_svc.identity_with_tz_for(tz, b="2", a="1", timestamp="foo")
        redis_conn._set_time(datetime.datetime(2018, 12, 10, 16, 59, 59, 0, None))
        ident3 = identity_svc.identity_with_tz_for(tz, a="1", b="2")
        ident4 = identity_svc.identity_with_tz_for(tz, a="3", b="4")
        redis_conn._set_time(datetime.datetime(2018, 12, 10, 17, 0, 0, 0, None))
        ident5 = identity_svc.identity_with_tz_for(tz, a="1", b="2")
        ident6 = identity_svc.identity_with_tz_for(tz, a="3", b="4")
        self.assertEqual(ident1, ident2)
        self.assertEqual(ident1, ident3)
        self.assertNotEqual(ident1, ident5)
        self.assertNotEqual(ident3, ident4)
        self.assertNotEqual(ident4, ident6)
        self.assertEqual(len(ident1), 10)
        self.assertEqual(len(ident4), 10)
        self.assertEqual(len(ident5), 10)
        self.assertEqual(len(ident6), 10)
        for _, v in redis_conn._expire.items():
            self.assertEqual(v, 86400)

    def test_identity_with_tz_for_pytz(self):
        from . import DummyRedis
        import pytz

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {"app.ident_size": 10}.get(key, None)

        tz = pytz.timezone("Asia/Bangkok")
        redis_conn = DummyRedis(datetime.datetime(2018, 12, 9, 17, 0, 0, 0, None))
        identity_svc = self._get_target_class()(redis_conn, _DummySettingQueryService())
        ident1 = identity_svc.identity_with_tz_for(tz, a="1", b="2")
        redis_conn._set_time(datetime.datetime(2018, 12, 10, 16, 59, 59, 0, None))
        ident2 = identity_svc.identity_with_tz_for(tz, a="1", b="2")
        redis_conn._set_time(datetime.datetime(2018, 12, 10, 17, 0, 0, 0, None))
        ident3 = identity_svc.identity_with_tz_for(tz, a="1", b="2")
        self.assertEqual(ident1, ident2)
        self.assertNotEqual(ident1, ident3)

    def test_identity_with_tz_for_length(self):
        from . import DummyRedis

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {"app.ident_size": 5}.get(key, None)

        redis_conn = DummyRedis()
        identity_svc = self._get_target_class()(redis_conn, _DummySettingQueryService())
        self.assertEqual(
            len(identity_svc.identity_with_tz_for("Asia/Bangkok", a="1", b="2")), 5
        )
