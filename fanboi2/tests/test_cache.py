import unittest


class TestCache(unittest.TestCase):
    def test_key_mangler(self):
        from ..cache import key_mangler

        self.assertEqual(
            key_mangler("Foobar"),
            "e811818f80d9c3c22d577ba83d6196788e553bb408535bb42105cdff726a60ab",
        )
