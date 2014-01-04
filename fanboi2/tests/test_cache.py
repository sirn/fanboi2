import unittest
from fanboi2.tests import CacheMixin


class TestCache(CacheMixin, unittest.TestCase):

    def test_key_mangler(self):
        from fanboi2.cache import _key_mangler
        store = {}
        region = self._getRegion(store)
        region.key_mangler = _key_mangler
        region.set("Foobar", 1)
        self.assertIn("89d5739baabbbe65be35cbe61c88e06d", store)


class TestJinja2CacheExtension(CacheMixin, unittest.TestCase):

    def _getJinja2(self, region):
        from jinja2 import Environment
        from fanboi2.cache import Jinja2CacheExtension
        env = Environment(extensions=[Jinja2CacheExtension])
        env.cache_region = region
        return env

    def test_cache(self):
        store = {}
        region = self._getRegion(store)
        jinja2 = self._getJinja2(region)
        jinja2.from_string('{% cache "a", "b" %}Baz{% endcache %}').render()
        self.assertIn('jinja2:None:a:b', store)
        self.assertEqual(region.get('jinja2:None:a:b'), 'Baz')

    def test_cache_not_setup(self):
        store = {}
        jinja2 = self._getJinja2(None)
        jinja2.from_string('{% cache "a", "b" %}Baz{% endcache %}').render()
        self.assertEqual({}, store)
