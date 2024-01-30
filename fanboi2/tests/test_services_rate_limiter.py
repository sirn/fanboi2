import unittest
import unittest.mock


class TestRateLimiterService(unittest.TestCase):
    def _get_target_class(self):
        from ..services import RateLimiterService

        return RateLimiterService

    def test_init(self):
        from . import DummyRedis

        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        self.assertEqual(rate_limiter_svc.redis_conn, redis_conn)

    def test_is_limited_not_limited(self):
        from . import DummyRedis

        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        self.assertFalse(rate_limiter_svc.is_limited(foo="bar"))

    def test_time_left_not_limited(self):
        from . import DummyRedis

        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        self.assertEqual(rate_limiter_svc.time_left(foo="bar"), 0)

    def test_naive_limit_for(self):
        from . import DummyRedis

        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        rate_limiter_svc.limit_for(10, foo="bar", baz="bax")
        self.assertIn("services.rate_limiter:baz=bax,foo=bar", redis_conn._store)

    def test_naive_is_limited(self):
        from . import DummyRedis

        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        rate_limiter_svc.limit_for(10, foo="bar")
        self.assertTrue(rate_limiter_svc.is_limited(foo="bar"))

    def test_naive_time_left(self):
        from . import DummyRedis

        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        rate_limiter_svc.limit_for(10, foo="bar")
        self.assertEqual(rate_limiter_svc.time_left(foo="bar"), 10)

    def test_scaled_limit_for(self):
        from . import DummyRedis

        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        rate_limiter_svc.limit_for(10, 5, 3600, foo="bar", baz="bax")
        self.assertIn("services.rate_limiter:baz=bax,foo=bar,type=ts", redis_conn._store)
        self.assertIn("services.rate_limiter:baz=bax,foo=bar", redis_conn._store)

    def test_scaled_is_limited(self):
        from . import DummyRedis

        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        rate_limiter_svc.limit_for(10, 5, 3600, foo="bar")
        self.assertTrue(rate_limiter_svc.is_limited(foo="bar"))

    def test_scaled_time_left(self):
        from . import DummyRedis

        redis_conn = DummyRedis()
        rate_limiter_svc = self._get_target_class()(redis_conn)
        rate_limiter_svc.limit_for(10, 5, 1800, foo="bar")
        self.assertEqual(rate_limiter_svc.time_left(foo="bar"), 3)

        rate_limiter_svc.limit_for(10, 5, 1800, foo="bar")
        self.assertEqual(rate_limiter_svc.time_left(foo="bar"), 10)

        rate_limiter_svc.limit_for(10, 5, 1800, foo="bar")
        self.assertEqual(rate_limiter_svc.time_left(foo="bar"), 37)

        rate_limiter_svc.limit_for(10, 5, 1800, foo="bar")
        self.assertEqual(rate_limiter_svc.time_left(foo="bar"), 134)

        rate_limiter_svc.limit_for(10, 5, 1800, foo="bar")
        self.assertEqual(rate_limiter_svc.time_left(foo="bar"), 491)

        rate_limiter_svc.limit_for(10, 5, 1800, foo="bar")
        self.assertEqual(rate_limiter_svc.time_left(foo="bar"), 1800)

        rate_limiter_svc.limit_for(10, 5, 1800, foo="bar")
        self.assertEqual(rate_limiter_svc.time_left(foo="bar"), 1800)
