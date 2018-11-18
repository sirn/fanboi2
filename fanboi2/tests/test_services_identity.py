import unittest
import unittest.mock


class TestIdentityService(unittest.TestCase):
    def _get_target_class(self):
        from ..services import IdentityService

        return IdentityService

    def test_init(self):
        from . import DummyRedis

        redis_conn = DummyRedis()
        identity_svc = self._get_target_class()(redis_conn, 10)
        self.assertEqual(identity_svc.redis_conn, redis_conn)
        self.assertEqual(identity_svc.ident_size, 10)

    def test_identity_for(self):
        from . import DummyRedis

        redis_conn = DummyRedis()
        identity_svc = self._get_target_class()(redis_conn, 10)
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

        redis_conn = DummyRedis()
        identity_svc = self._get_target_class()(redis_conn, 5)
        self.assertEqual(len(identity_svc.identity_for(a="1", b="2")), 5)
