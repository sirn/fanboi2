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
