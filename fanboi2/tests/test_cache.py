import unittest


class TestCache(unittest.TestCase):

    def _getRegion(self, store=None):
        from dogpile.cache import make_region
        return make_region().configure('dogpile.cache.memory', arguments={
            'cache_dict': store if store is not None else {}})

    def test_key_mangler(self):
        from fanboi2.cache import _key_mangler
        store = {}
        region = self._getRegion(store)
        region.key_mangler = _key_mangler
        region.set("Foobar", 1)
        self.assertIn("89d5739baabbbe65be35cbe61c88e06d", store)
