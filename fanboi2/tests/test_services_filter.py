import unittest
import unittest.mock


class TestFilterService(unittest.TestCase):
    def setUp(self):
        super(TestFilterService, self).setUp()

    def _get_target_class(self):
        from ..services import FilterService

        return FilterService

    def _make_one(self, filters, services):
        def _dummy_query_fn(iface=None, name=None):
            for l in (iface, name):
                if l in services:
                    return services[l]

        return self._get_target_class()(filters, _dummy_query_fn)

    def tearDown(self):
        super(TestFilterService, self).tearDown()

    def test_init(self):
        filter_svc = self._make_one(tuple(), {"cache": "test"})
        self.assertEqual(filter_svc.filters, tuple())
        self.assertEqual(filter_svc.service_query_fn("cache"), "test")

    def test_evaluate(self):
        from . import make_cache_region
        from ..interfaces import ISettingQueryService

        _settings = None
        _services = None
        _payload = None

        class _DummyFilter(object):
            __use_services__ = ("cache",)

            def __init__(self, settings=None, services=None):
                nonlocal _settings, _services
                self.settings = _settings = settings
                self.services = _services = services

            def should_reject(self, payload):
                nonlocal _payload
                _payload = payload
                return True

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {"ext.filters.dummy": "overridden"}.get(key, None)

        cache_region = make_cache_region({})
        filter_svc = self._make_one(
            (("dummy", _DummyFilter),),
            {"cache": cache_region, ISettingQueryService: _DummySettingQueryService()},
        )

        results = filter_svc.evaluate({"foo": "bar"})
        self.assertEqual(results.filters, ["dummy"])
        self.assertEqual(results.rejected_by, "dummy")
        self.assertEqual(_settings, "overridden")
        self.assertEqual(_services, {"cache": cache_region})
        self.assertEqual(_payload, {"foo": "bar"})

    def test_evaluate_recently_seen(self):
        from ..interfaces import IPostQueryService

        called_ = False

        class _DummyFilter(object):  # pragma: no cover
            def __init__(self, **kwargs):
                pass

            def should_reject(self, payload):
                nonlocal called_
                called_ = True
                return True

        class _DummyPostQueryService(object):
            def was_recently_seen(self, ip_address):
                return True

        filter_svc = self._make_one(
            (("dummy", _DummyFilter),), {IPostQueryService: _DummyPostQueryService()}
        )

        results = filter_svc.evaluate({"ip_address": "127.0.0.1"})
        self.assertEqual(results.filters, [])
        self.assertEqual(results.rejected_by, None)
        self.assertFalse(called_)

    def test_evaluate_fallback(self):
        from . import make_cache_region
        from ..interfaces import ISettingQueryService

        class _DummyFilterFalse(object):
            def __init__(self, settings=None, services=None):
                self.settings = settings
                self.services = services

            def should_reject(self, payload):
                return False

        class _DummyFilterTrue(_DummyFilterFalse):
            def should_reject(self, payload):
                return True

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        cache_region = make_cache_region({})
        filter_svc = self._make_one(
            (("dummy1", _DummyFilterFalse), ("dummy2", _DummyFilterTrue)),
            {"cache": cache_region, ISettingQueryService: _DummySettingQueryService()},
        )

        results = filter_svc.evaluate({"foo": "bar"})
        self.assertEqual(results.filters, ["dummy1", "dummy2"])
        self.assertEqual(results.rejected_by, "dummy2")

    def test_evaluate_false(self):
        from . import make_cache_region
        from ..interfaces import ISettingQueryService

        class _DummyFilterFalse(object):
            def __init__(self, settings=None, services=None):
                self.settings = settings
                self.services = services

            def should_reject(self, payload):
                return False

        class _DummySettingQueryService(object):
            def value_from_key(self, key, **kwargs):
                return {}.get(key, None)

        cache_region = make_cache_region({})
        filter_svc = self._make_one(
            (("dummy1", _DummyFilterFalse), ("dummy2", _DummyFilterFalse)),
            {"cache": cache_region, ISettingQueryService: _DummySettingQueryService()},
        )

        results = filter_svc.evaluate({"foo": "bar"})
        self.assertEqual(results.filters, ["dummy1", "dummy2"])
        self.assertIsNone(results.rejected_by)
